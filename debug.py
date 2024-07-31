from playwright.sync_api import sync_playwright
from PIL import Image
from reportlab.pdfgen import canvas


def convert_png_to_pdf(path):
    img = Image.open(path + '.png')
    img_width, img_height = img.size
    c = canvas.Canvas(path + '.pdf', pagesize=(img_width, img_height))
    c.drawImage(path + '.png', 0, 0, width=img_width, height=img_height)
    c.save()


with sync_playwright() as sp:
    bro = sp.chromium.launch(headless=False)
    con = bro.new_context(ignore_https_errors=True)
    page = con.new_page()
    page.goto('https://accord.kineoadapt.com/#user/login', wait_until='networkidle')
    page.fill('id=login-input-username', 'nwo@anthillagency.com')
    page.fill('id=login-input-password', 'Oncodemia1234')
    with page.expect_navigation(url='**/#dashboard', wait_until='networkidle'):
        page.click('button[type="submit"]')

    page.goto(
        'https://accord.kineoadapt.com/preview/5ea043936faab32f3e380a7e/60b6423c6cccde5e97c4b7a5/#/id/60b6423d6cccde5e97c4b7a6',
        wait_until='networkidle')
    page.wait_for_timeout(1000)
    page.locator('.hotgrid__item').nth(1).click()
    page.locator('.notify__popup').wait_for(state='visible')
    page.wait_for_timeout(300)
    name = 'test'
    page.locator('.notify__popup').screenshot(path=name+'.png')
    convert_png_to_pdf(name)
    con.close()
    bro.close()
