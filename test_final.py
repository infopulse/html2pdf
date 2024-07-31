# imports
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Locator
import asyncio
import logging
import re
import os
from PIL import Image
from reportlab.pdfgen import canvas

BASE_URL = 'https://accord.kineoadapt.com/#user/login'  # @param {type:"string"}
USERNAME = 'nwo@anthillagency.com'  # @param {type:"string"}
PASSWORD = 'Oncodemia1234'  # @param {type:"string"}

# @markdown ---
# @markdown #### Enter urls to be parsed (coma separated):
urls_to_parse = (
    'https://accord.kineoadapt.com/preview/5ea043936faab32f3e380a7e/60b6423c6cccde5e97c4b7a5/#/id/60b6423d6cccde5e97c4b7a6,'
    ' https://accord.kineoadapt.com/preview/5ea043936faab32f3e380a7e/60a2514f6cccde5e97c4ad20/#/id/60a2514f6cccde5e97c4ad21')  # @param {type: "string"}
URLS = [url.strip() for url in urls_to_parse.split(',')]

#  technicals configs. Leave unchanged but execute anyway
PAGE_WIDTH = 1024
PLAYWRIGHT_TIMEOUT = 30_000
OUTPUT_FOLDER = 'output'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
log = logging.getLogger('html2pdf')
log.setLevel(logging.DEBUG)


# helpers
def join_pdfs(files: list, output_folder: str, file_name: str):
    from pypdf import PdfMerger
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(f'{output_folder}/{file_name}.pdf')
    log.info('files merged')
    merger.close()


def delete_files(files: list):
    for file in files:
        os.remove(file)
    log.info('temp pdf files deleted')
    png_files = [file for file in os.listdir(OUTPUT_FOLDER) if file.endswith('.png')]
    for file in png_files:
        os.remove(os.path.join(OUTPUT_FOLDER, file))
    log.info('temp png files deleted')


def convert_png_to_pdf(path) -> str:
    img = Image.open(path + '.png')
    img_width, img_height = img.size
    c = canvas.Canvas(path + '.pdf', pagesize=(img_width, img_height))
    c.drawImage(path + '.png', 0, 0, width=img_width, height=img_height)
    c.save()
    return path + '.pdf'


# recorder class. All magic is here 💛💙

class Recorder:
    browser: Browser
    context: BrowserContext
    page: Page

    def __init__(self, browser: Browser, base_url: str, folder: str, page_width=1024,
                 timeout: int = 10_000):
        self.browser = browser
        self.base_url = base_url
        self.folder = folder
        self.page_width = page_width
        self.timeout = timeout
        self.variants_counter = 0
        self.file_name = None

    async def create(self):
        self.context = await self.browser.new_context(viewport={'width': self.page_width,
                                                                'height': 800})
        self.context.set_default_timeout(self.timeout)
        self.page = await self.context.new_page()
        await self.page.emulate_media(media="screen")
        log.info('page created')

    async def authenticate(self, username: str, password: str):
        log.debug('starting authentication')
        await self.page.goto(self.base_url, wait_until='networkidle')
        await self.page.fill('id=login-input-username', username)
        await self.page.fill('id=login-input-password', password)
        async with self.page.expect_navigation(url='**/#dashboard', wait_until='networkidle'):
            await self.page.click('button[type="submit"]')
        log.info('authentication done')

    async def goto(self, url: str) -> str:
        log.info('navigating to ' + url)
        self.variants_counter = 0
        log.debug('variants counter reset')
        await self.page.goto(url, wait_until='networkidle')
        await self.page.locator('.loading').wait_for(state='hidden')
        # wait 5 sec more to make sure all animations are done
        await self.page.wait_for_timeout(5000)
        await self.page.keyboard.press('End')
        await self.page.wait_for_timeout(2000)
        # await self.page.locator('.block__inner').last.is_visible()
        title = await self.page.locator('.page__title').inner_text()
        if '\n' in title:
            title = title.split('\n')[1].strip()
        self.file_name = re.sub('[^a-zA-Z0-9]', '_', title)
        return self.file_name

    async def get_slider_blocks(self):
        log.debug('looking for narrative sliders')
        blocks = await self.page.locator('.block__inner:has(.narrative__slide-container)').all()
        log.debug(f'found {len(blocks)} sliders')
        for block in blocks:
            yield 'slider', block

    async def get_hotgrid_blocks(self):
        log.debug('looking for hotgrid widgets')
        blocks = await self.page.locator('.hotgrid__grid .hotgrid__item').all()
        log.debug(f'found {len(blocks)} hotgrid widgets')
        for block in blocks:
            yield 'hotgrid', block

    async def get_accordion_blocks(self):
        log.debug('looking for accordion widgets')
        blocks = await self.page.locator('.block__inner:has(.accordion__widget)').all()
        log.debug(f'found {len(blocks)} accordion widgets')
        for block in blocks:
            yield 'accordion', block

    async def expand_accordion_blocks(self):
        accordions = await self.page.locator('.accordion__item-content').all()
        for accordion in accordions:
            await accordion.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    async def expand_dropdown_blocks(self):
        dropdown_lists = await self.page.locator('.dropdown .dropdown__list').all()
        for dropdown_list in dropdown_lists:
            await dropdown_list.evaluate("x => x.style.setProperty('position', 'relative', 'important')")
            await dropdown_list.evaluate("x => x.style.setProperty('display', 'block', 'important')")
        dropdowns = await self.page.locator('.dropdown .u-display-none').all()
        for dropdown in dropdowns:
            await dropdown.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    async def get_dropdown_blocks(self):
        log.debug('looking for dropdowns')
        blocks = await self.page.locator('.block__inner:has(.dropdown)').all()
        log.debug(f'found {len(blocks)} dropdowns')
        for block in blocks:
            yield 'dropdown', block

    async def get_all_blocks(self):
        blocks = []
        async for block in self.get_slider_blocks():
            blocks.append(block)
        async for block in self.get_hotgrid_blocks():
            blocks.append(block)
        # async for block in self.get_accordion_blocks():
        #     blocks.append(block)
        # async for block in self.get_dropdown_blocks():
        #     blocks.append(block)
        annotated_list = [(await x[1].evaluate('x => x.getBoundingClientRect().top + window.pageYOffset'), x) for x in
                          blocks]
        annotated_list.sort(key=lambda x: x[0])
        return [x[1] for x in annotated_list]

    async def save_block(self, block):
        if block[0] == 'slider':
            return await self.save_sliders(block[1])
        elif block[0] == 'hotgrid':
            return await self.save_hotgrid(block[1])
        # elif block[0] == 'accordion':
        #     return await self.save_accordion(block[1])
        # elif block[0] == 'dropdown':
        #     return await self.save_dropdown(block[1])

    async def save_sliders(self, element: Locator) -> list:
        files = []

        images = await element.locator('.narrative__slider-image-container').count()
        # set image count -1 because 1st one already displayed
        for image in range(images - 1):
            file_name = f'{self.folder}/{self.file_name}-{self.variants_counter:02}'
            await element.locator('.narrative__slide-container .narrative__controls-right').click()
            await self.page.wait_for_timeout(1000)
            await element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            log.info(f'narrative slider saved')
            self.variants_counter += 1
        return files

    async def save_hotgrid(self, element: Locator) -> list:
        files = []
        file_name = f'{self.folder}/{self.file_name}-{self.variants_counter:02}'
        self.variants_counter += 1
        await element.click()
        await self.page.locator('.notify__popup').wait_for(state='visible')
        await self.page.wait_for_timeout(1000)
        await self.page.locator('.notify__popup').screenshot(path=file_name + '.png')
        convert_png_to_pdf(file_name)
        files.append(file_name + '.pdf')
        log.info(f'hotgrid saved')
        await self.page.keyboard.press('Escape')
        await self.page.wait_for_timeout(500)
        return files

    async def save_accordion(self, element: Locator) -> list:
        files = []
        accordion_count = await element.locator('.accordion__item').count()
        for accordion in range(accordion_count):
            file_name = f'{self.folder}/{self.file_name}-{self.variants_counter:02}'
            await element.locator('.accordion__item').nth(accordion).click()
            await self.page.wait_for_timeout(1000)
            await element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            log.info(f'accordion saved')
            self.variants_counter += 1
        return files

    async def save_dropdown(self, element: Locator):
        files = []
        dropdown_count = await element.locator('.dropdown').count()
        for dropdown in range(dropdown_count):
            file_name = f'{self.folder}/{self.file_name}-{self.variants_counter:02}'
            await element.locator('.dropdown').nth(dropdown).click()
            await self.page.wait_for_timeout(1000)
            await element.screenshot(path=file_name + '.png')
            convert_png_to_pdf(file_name)
            files.append(file_name + '.pdf')
            log.info(f'dropdown saved')
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(500)
            self.variants_counter += 1
        return files

    async def save_pdf(self):
        files = []
        # saving initial page view
        file_name = f'{self.folder}/{self.file_name}-{self.variants_counter:02}.pdf'
        self.variants_counter += 1
        files.append(file_name)
        height = await self.page.evaluate('document.body.scrollHeight')
        # add more height to make sure all elements are visible
        height += 1000
        await self.expand_accordion_blocks()
        await self.expand_dropdown_blocks()
        await self.page.pdf(path=file_name,
                            print_background=True,
                            width=f'{self.page_width}px',
                            height=f'{height}px',
                            prefer_css_page_size=True,
                            page_ranges=None)
        for block in await self.get_all_blocks():
            files += await self.save_block(block)
        log.info('page with all variants saved')
        return files


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        recorder = Recorder(browser, base_url=BASE_URL, folder=OUTPUT_FOLDER, page_width=PAGE_WIDTH,
                            timeout=PLAYWRIGHT_TIMEOUT)
        await recorder.create()
        await recorder.authenticate(username=USERNAME,
                                    password=PASSWORD)
        for url in URLS:
            try:
                title = await recorder.goto(url)
                files = await recorder.save_pdf()
            except Exception as e:
                await recorder.page.screenshot(path='error.png')
                raise e
            join_pdfs(files, OUTPUT_FOLDER, title)
            delete_files(files)


asyncio.run(main())
# await main()
