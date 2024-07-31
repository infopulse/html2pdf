from playwright.sync_api import Browser
import logging
import re

log = logging.getLogger('2pdf')
log.setLevel(logging.INFO)


# Create playwright context and page
class Recorder:
    def __init__(self, browser: Browser, base_url: str, timeout: int = 10_000):
        self.base_url = base_url
        self.variants_counter = 0

        self.context = browser.new_context(ignore_https_errors=True)
        self.context.set_default_timeout(timeout)
        self.page = self.context.new_page()
        self.page.emulate_media(media="screen")
        log.info('page created')

    def authenticate(self, username: str, password: str):
        log.debug('starting authentication')
        self.page.goto(self.base_url, wait_until='networkidle')
        self.page.fill('id=login-input-username', username)
        self.page.fill('id=login-input-password', password)

        with self.page.expect_navigation(url='**/#dashboard', wait_until='networkidle'):
            self.page.click('button[type="submit"]')
        log.info('authentication done')

    def goto(self, url: str) -> str:
        log.info('navigating to ' + url)
        self.variants_counter = 0
        log.debug('variants counter reset')
        self.page.goto(url, wait_until='networkidle')
        # wait 1 sec more to make sure all animations are done
        self.page.wait_for_timeout(1000)
        title = self.page.locator('.page__title').inner_text()
        return re.sub('[^a-zA-Z0-9]', '_', title)

    def save_sliders(self, folder: str, file_name: str):
        files = []
        log.debug('looking for narrative sliders')
        sliders_count = self.page.locator('.narrative__slide-container').count()
        for slider in range(sliders_count):
            log.debug(f'iterating through narrative slider {slider}')
            images = self.page.locator('.narrative__slide-container').nth(slider).locator(
                '.narrative__slider-image-container').count()
            # set image count -1 because 1st one already displayed
            for image in range(images - 1):
                self.page.locator('.narrative__slide-container').nth(slider).locator(
                    '.narrative__controls-right').click()
                self.page.wait_for_timeout(1000)
                file_name = f'{folder}/{file_name}-var{self.variants_counter:02}.pdf'
                files.append(file_name)
                self.page.pdf(path=file_name)
                log.info(f'page with narrative slider updated saved #{image} time')
                self.variants_counter += 1
        return files


    def save_hotgrid(self, folder: str, file_name: str):
        files = []
        log.debug('looking for hotgrid widgets')
        hotgrid_count = self.page.locator('.hotgrid__grid .hotgrid__item').count()
        for item, hotgrid in enumerate(range(hotgrid_count)):
            log.debug(f'iterating through hotgrid widgets {hotgrid}')
            self.page.locator('.hotgrid__grid .hotgrid__item').nth(hotgrid).click()
            self.page.wait_for_timeout(500)
            file_name = f'{folder}/{file_name}-var{self.variants_counter:02}.pdf'
            files.append(file_name)
            self.page.pdf(path=file_name)
            log.info(f'page with hotgrid updated saved #{item} time')
            self.variants_counter += 1
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(500)
        return files

    def save_accordion(self, folder: str, file_name: str):
        files = []
        log.debug('looking for accordion widgets')
        accordion_count = self.page.locator('.accordion__widget').count()
        for accordion in range(accordion_count):
            log.debug(f'iterating through accordion widgets {accordion}')
            items = self.page.locator('.accordion__widget').nth(accordion).locator('.accordion__item').count()
            for item in range(items):
                self.page.locator('.accordion__widget').nth(accordion).locator('.accordion__item').nth(item).click()
                self.page.wait_for_timeout(1000)
                file_name = f'{folder}/{file_name}-var{self.variants_counter:02}.pdf'
                files.append(file_name)
                self.page.pdf(path=file_name)
                log.info(f'page with accordion updated saved #{item} time')
                self.variants_counter += 1
        return files

    def save_pdf(self, folder: str, file_name: str):
        files = []
        # saving initial page view
        file_name = f'{folder}/{file_name}-var{self.variants_counter:02}.pdf'
        files.append(file_name)
        self.page.pdf(path=file_name)
        self.variants_counter += 1
        # looking for interactive elements and clicking them one by one
        files += self.save_sliders(folder, file_name)
        files += self.save_accordion(folder, file_name)
        files += self.save_hotgrid(folder, file_name)

        log.info('page with all variants saved')
        return files
