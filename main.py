import tomllib
import argparse
import logging
import datetime as dt
import os
from playwright.async_api import async_playwright
from async_recorder import Recorder
import asyncio

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main-2pdf')


def get_config(file_name: str):
    with open(file_name, 'rb') as f:
        return tomllib.load(f)


def read_config_and_args():
    parser = argparse.ArgumentParser(description="this app grabs web pages and saves them as pdf")
    parser.add_argument('--config', type=str, help="config file", default='config.toml')
    parser.add_argument('--urls', type=str, help="file with urls to grab", default='urls.txt')
    parser.add_argument('--out', type=str, help="output folder for pdfs", default='output')
    parser.add_argument('--user', type=str, help="username", default=None)
    parser.add_argument('--password', type=str, help="password", default=None)
    args = parser.parse_args()
    config = get_config(args.config)
    log.info(f'config {args.config} parsed')
    if args.user is None and args.password is None:
        log.info('login and pasword not provided, using config')
    else:
        log.info('login and pasword provided, using them')
        config['credentials']['username'] = args.user
        config['credentials']['password'] = args.password
    config['output'] = args.out
    try:
        with open(args.urls, 'r') as f:
            config['urls'] = f.readlines()
    except FileNotFoundError:
        log.error(f'file {args.urls} not found')
        exit(1)
    except Exception as e:
        log.error(f'error with parsing {args.urls} happened')
        exit(1)
    return config


# async def run_playwright_code(url: str, output: str, prefix: str):
#     async with async_playwright() as sp:
#         browser = await sp.chromium.launch(headless=True)
#         context = browser.new_context(ignore_https_errors=True)
#         page = context.new_page()
#         page.goto(url, wait_until='networkidle')
#         page.emulate_media(media="screen")
#         # page.locator().click(force=True)
#
#         timestamp = dt.datetime.now().strftime('%d-%m-%Y_%H%M')
#         page.pdf(path=f'output/{prefix}{timestamp}.pdf')


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
    log.info('files deleted')


async def main():
    log.info('application started')
    config = read_config_and_args()
    os.makedirs(config['output'], exist_ok=True)
    async with async_playwright() as asp:
        browser = await asp.chromium.launch(headless=True)
        recorder = Recorder(browser, base_url=config['website']['base_url'])
        await recorder.create()
        await recorder.authenticate(username=config['credentials']['username'],
                                    password=config['credentials']['password'])
        for url in config['urls']:
            title = await recorder.goto(url)
            files = await recorder.save_pdf()
            join_pdfs(files, config['output'], title)
            delete_files(files)


if __name__ == '__main__':
    asyncio.run(main())

    log.info('application finished')
