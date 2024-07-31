import re
from typing import NamedTuple, Callable
from playwright.sync_api import Page, Locator
from misc import convert_png_to_pdf


class Block(NamedTuple):
    name: str
    element: Locator


class Recorder:
    def __init__(self, page: Page, output_folder: str, progress: Callable):
        self.page = page
        self.output_folder = output_folder
        self.file_name = None
        self.variants_counter = 0
        self.log = progress

    # returns page title
    def goto(self, url: str) -> str:
        self.variants_counter = 0
        self.page.goto(url, wait_until='networkidle')
        self.page.locator('.loading').wait_for(state='hidden')
        # wait 2 sec more to make sure all animations are done
        self.page.wait_for_timeout(1000)
        self.page.keyboard.press('End')
        self.page.wait_for_timeout(1000)
        self.page.locator('.block__inner').last.locator('.block__header').click()
        title = self.page.locator('.page__title').inner_text()
        if '\n' in title:
            title = title.split('\n')[1].strip()
        self.file_name = re.sub('[^a-zA-Z0-9]', '_', title)

        self.log("target page is loaded")

        return self.file_name

    def get_slider_blocks(self) -> list[Block]:
        blocks = self.page.locator('.block__inner:has(.narrative__slide-container)').all()
        return [Block('slider', block) for block in blocks]

    def get_hotgrid_blocks(self) -> list[Block]:
        blocks = self.page.locator('.hotgrid__grid .hotgrid__item').all()
        return [Block('hotgrid', block) for block in blocks]

    def get_accordion_blocks(self) -> list[Block]:
        blocks = self.page.locator('.block__inner:has(.accordion__widget)').all()
        return [Block('accordion', block) for block in blocks]

    def get_dropdown_blocks(self) -> list[Block]:
        blocks = self.page.locator('.block__inner:has(.dropdown)').all()
        return [Block('dropdown', block) for block in blocks]

    def expand_accordion_blocks(self):
        accordions = self.page.locator('.accordion__item-content').all()
        for accordion in accordions:
            accordion.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    def expand_dropdown_blocks(self):
        dropdown_lists = self.page.locator('.dropdown .dropdown__list').all()
        for dropdown_list in dropdown_lists:
            dropdown_list.evaluate("x => x.style.setProperty('position', 'relative', 'important')")
            dropdown_list.evaluate("x => x.style.setProperty('display', 'block', 'important')")
        dropdowns = self.page.locator('.dropdown .u-display-none').all()
        for dropdown in dropdowns:
            dropdown.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    def get_all_blocks(self) -> list[Block]:
        blocks = (self.get_slider_blocks() +
                  self.get_hotgrid_blocks())
                  # self.get_accordion_blocks() +
                  # self.get_dropdown_blocks())

        script = """x => x.getBoundingClientRect().top + window.pageYOffset"""
        annotated_list = [(x.element.evaluate(script), x) for x in blocks]
        annotated_list.sort(key=lambda x: x[0])
        return [x[1] for x in annotated_list]

    def save_sliders(self, element: Locator) -> list:
        files = []
        images = element.locator('.narrative__slider-image-container').count()
        # set image count -1 because 1st one already displayed
        for image in range(images - 1):
            file_name = f'{self.output_folder}/{self.file_name}-{self.variants_counter:02}'
            element.locator('.narrative__controls-right').click()
            self.page.wait_for_timeout(1000)
            element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            self.variants_counter += 1
        return files

    def save_hotgrid(self, element: Locator) -> list:
        files = []
        file_name = f'{self.output_folder}/{self.file_name}-{self.variants_counter:02}'
        self.variants_counter += 1
        element.click()
        self.page.locator('.notify__popup').wait_for(state='visible')
        self.page.wait_for_timeout(1000)
        self.page.locator('.notify__popup').screenshot(path=file_name + '.png')
        convert_png_to_pdf(file_name)
        files.append(file_name + '.pdf')
        self.page.keyboard.press('Escape')
        self.page.wait_for_timeout(500)
        return files

    def save_accordion(self, element: Locator) -> list:
        files = []
        accordion_count = element.locator('.accordion__item').count()
        for accordion in range(accordion_count):
            file_name = f'{self.output_folder}/{self.file_name}-{self.variants_counter:02}'
            element.locator('.accordion__item').nth(accordion).click()
            self.page.wait_for_timeout(1000)
            element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            self.variants_counter += 1
        return files

    def save_dropdown(self, element: Locator):
        files = []
        dropdown_count = element.locator('.dropdown').count()
        for dropdown in range(dropdown_count):
            file_name = f'{self.output_folder}/{self.file_name}-{self.variants_counter:02}'
            element.locator('.dropdown').nth(dropdown).click()
            self.page.wait_for_timeout(1000)
            element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(500)
            self.variants_counter += 1
        return files

    def save_block(self, block: Block):
        if block.name == 'slider':
            return self.save_sliders(block.element)
        elif block.name == 'hotgrid':
            return self.save_hotgrid(block.element)
        # elif block.name == 'accordion':
        #     return self.save_accordion(block.element)
        # elif block.name == 'dropdown':
        #     return self.save_dropdown(block.element)

    def save_pdf(self):
        files = []
        # saving initial page view
        file_name = f'{self.output_folder}/{self.file_name}-{self.variants_counter:02}.pdf'
        self.variants_counter += 1
        files.append(file_name)

        self.expand_accordion_blocks()
        self.expand_dropdown_blocks()

        self.page.keyboard.press('Home')

        height = self.page.evaluate('document.body.scrollHeight')
        # add more height to make sure all elements are visible
        height += 500
        self.page.pdf(path=file_name,
                      print_background=True,
                      width=f'{1024}px',
                      height=f'{height}px',
                      prefer_css_page_size=True,
                      page_ranges=None)

        self.log('initial page view saved')
        for block in self.get_all_blocks():
            f = self.save_block(block)
            print(f)
            files += f
        self.log('all variants saved')
        return files
