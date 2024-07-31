import os
from os import path
import time
from PIL import Image
from reportlab.pdfgen import canvas


def check_browser_state(path_to_state: str) -> bool:
    return (path.exists(path_to_state) and
            path.getctime(path_to_state) > time.time() - 60 * 60 * 24)


def join_pdfs(files: list, output_folder: str, file_name: str):
    from pypdf import PdfMerger
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(f'{output_folder}/{file_name}.pdf')
    merger.close()


def delete_files(files: list):
    for file in files:
        os.remove(file)


def convert_png_to_pdf(path) -> str:
    with Image.open(path + '.png') as img:
        img_width, img_height = img.size
        c = canvas.Canvas(path + '.pdf', pagesize=(img_width, img_height))
        c.drawImage(path + '.png', 0, 0, width=img_width, height=img_height)
        c.save()
    os.remove(path + '.png')
    return path + '.pdf'
