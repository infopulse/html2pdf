from playwright.sync_api import sync_playwright, Browser
from settings import BASE_URL
from typing import NamedTuple
from misc import check_browser_state, join_pdfs, delete_files
from typing import Callable
from new_recorder import Recorder


class Status(NamedTuple):
    result: bool
    message: str


state_file = 'state.json'


def authenticate(username: str, password: str, headless: bool = True) -> Status:
    if check_browser_state(state_file):
        return Status(True, '✅ Already authenticated')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(BASE_URL)
            page.fill('id=login-input-username', username)
            page.fill('id=login-input-password', password)
            with page.expect_navigation(url='**/#dashboard', wait_until='networkidle'):
                page.click('button[type="submit"]')
            context.storage_state(path=state_file)
            return Status(True, '✅ Authentication done')
        except Exception as e:
            return Status(False, '❌ ' + str(e))


def parse_the_page(url: str, output_folder: str, progress: Callable, headless: bool = False) -> None:
    with sync_playwright() as p:
        viewport = {'width': 1024, 'height': 800}
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=state_file,
            viewport=viewport,
            ignore_https_errors=True)
        context.set_default_timeout(15_000)
        page = context.new_page()
        page.emulate_media(media="screen")

        progress('page created')
        recorder = Recorder(page, output_folder, progress)
        title = recorder.goto(url)
        files = recorder.save_pdf()
        print('all files --->> ', files)
        join_pdfs(files, output_folder, title)
        delete_files(files)
