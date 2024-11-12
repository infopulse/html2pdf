import os
import re
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Locator
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO


HEADLESS = True
BASE_URL = 'https://accord.kineoadapt.com'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)


class Recorder:
    page: Page
    base_url: str
    page_blocks: list[bytes]
    current_page_title: str

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.page_blocks = []
        self.current_page_title = ''

    def _clean_up(self):
        self.page_blocks = []
        self.current_page_title = ''

    def _add_screenshot(self, locator: Locator):
        screenshot_params = {
            'type': 'jpeg',
            'quality': 100,
            'animations': 'disabled',
            'scale': 'css'
        }
        screenshot = locator.screenshot(**screenshot_params)
        log.debug('Block screenshot added')
        self.page_blocks.append(screenshot)

    def login(self, username: str, password: str):
        log.info('Logging in')
        self._clean_up()
        self.page.goto(BASE_URL)
        log.debug('navigate to login page')
        self.page.fill('id=login-input-username', username)
        self.page.fill('id=login-input-password', password)
        with self.page.expect_navigation(url='**/#dashboard', wait_until='networkidle'):
            log.debug('submitting login form')
            self.page.click('button[type="submit"]')
        log.info('Logged in')

    def save_pages(self, urls: list[str]):
        for url in urls:
            self.save_page(url)

    def save_page(self, url: str):
        self.goto(url)
        self.get_header()
        title = self.get_page_title()
        self.hide_navigation()
        self.expand_accordion_blocks()
        self.expand_dropdown_blocks()
        self.get_blocks()
        self.save_pdf(f'{title}.pdf')

    def get_page_title(self) -> str:
        log.debug('Getting page title')
        title = self.page.locator('.page__title').inner_text()
        if '\n' in title:
            title = title.split('\n')[1].strip()
        self.current_page_title = re.sub('[^a-zA-Z0-9]', '_', title)
        return self.current_page_title

    def goto(self, url: str):
        self._clean_up()
        log.info(f'Navigating to {url}')
        self.page.goto(url, wait_until='networkidle')
        self.page.locator('.loading').wait_for(state='hidden')
        log.debug('shake the page to make sure all animations are done')
        for _ in range(2):
            self.page.wait_for_timeout(100)
            self.page.keyboard.press('End')
            self.page.wait_for_timeout(100)
            self.page.keyboard.press('Home')

    def get_header(self):
        log.info('Getting header')
        header = self.page.locator('.page__header').screenshot()
        self.page_blocks.append(header)

    def hide_navigation(self):
        log.info('Hiding navigation panel')
        navigation = self.page.locator('.nav__inner')
        navigation.evaluate("x => x.style.setProperty('display', 'none', 'important')")

    def expand_accordion_blocks(self):
        log.info('Expanding accordion blocks')
        accordions = self.page.locator('.accordion__item-content').all()
        for accordion in accordions:
            accordion.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    def expand_dropdown_blocks(self):
        log.info('Expanding dropdown blocks')
        dropdown_lists = self.page.locator('.dropdown .dropdown__list').all()
        for dropdown_list in dropdown_lists:
            dropdown_list.evaluate("x => x.style.setProperty('position', 'relative', 'important')")
            dropdown_list.evaluate("x => x.style.setProperty('display', 'block', 'important')")
        dropdowns = self.page.locator('.dropdown .u-display-none').all()
        for dropdown in dropdowns:
            dropdown.evaluate("x => x.style.setProperty('display', 'block', 'important')")

    def get_blocks(self):
        log.info('Taking screenshots block by block')
        blocks = self.page.locator('.block').all()
        for n, block in enumerate(blocks):
            self._add_screenshot(block)

            if block.locator('.block__inner:has(.narrative__slide-container)').is_visible():
                log.debug('Block has slider')
                slider_cls = '.narrative__slide-container .narrative__controls-right'
                right_arrow = block.locator(slider_cls)
                limit = 20
                while limit > 0 and right_arrow.is_visible():
                    block.locator(slider_cls).click()
                    self.page.wait_for_timeout(100)
                    self._add_screenshot(block)
                    limit -= 1

            elif block.locator('.hotgrid__item').count() > 0:
                log.debug('Block has hotgrid')
                block.locator('.hotgrid__item').first.click()
                popup = self.page.locator('.notify__popup')
                self.page.wait_for_timeout(500)
                self._add_screenshot(popup)
                limit = 20
                next_btn = popup.locator('.hotgrid-popup__controls.next')
                while limit > 0 and next_btn.is_visible():
                    next_btn.click()
                    self.page.wait_for_timeout(100)
                    self._add_screenshot(popup)
                self.page.keyboard.press('Escape')
                self.page.wait_for_timeout(500)

            else:
                # TODO new interactive elements
                pass

    def save_pdf(self, file_name: str):
        log.info(f'Saving PDF')
        pdf_buffer = BytesIO()
        c = None
        for block in self.page_blocks:
            img_buffer = BytesIO(block)
            img = ImageReader(img_buffer)
            img_width, img_height = img.getSize()
            if c is None:
                c = canvas.Canvas(pdf_buffer, pagesize=(img_width, img_height))
            else:
                c.setPageSize((img_width, img_height))
            c.drawImage(img, 0, 0, width=img_width, height=img_height)
            c.showPage()
        c.save()
        pdf_buffer.seek(0)
        output = Path('output')
        if not output.exists():
            output.mkdir()
        with open(output / file_name, "wb") as f:
            f.write(pdf_buffer.getbuffer())
        log.info(f'PDF saved to {file_name}')


def main(username: str, password: str, links: list[str], headless: bool = True):
    # chromium_bin = Path(os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/usr/local/share/playwright'))
    with sync_playwright() as p:
        log.info('Starting browser')
        browser = p.chromium.launch(headless=headless)
        # browser = p.chromium.launch(headless=headless, executable_path=chromium_bin / 'chrome')
        context = browser.new_context(
            viewport={'width': 1024, 'height': 800},
            ignore_https_errors=True)
        context.set_default_timeout(15_000)
        page = context.new_page()
        page.emulate_media(media="screen")
        log.info('launching recorder')
        recorder = Recorder(page, BASE_URL)
        recorder.login(username, password)
        recorder.save_pages(links)

if __name__ == "__main__":
    pages = []
    # main()