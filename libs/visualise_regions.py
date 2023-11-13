from PIL import Image, ImageDraw, ImageFont
import urllib.request
from pathlib import Path


FONT_URL = 'https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf'

def load_font():
    font_file = Path('Arial.ttf')
    if not font_file.is_file():
        urllib.request.urlretrieve(FONT_URL, 'Arial.ttf')

    try:
        font = ImageFont.truetype('Arial.ttf', size=30)
    except IOError:
        font = ImageFont.load_default()
    return font

def create_debug_dir():
    Path('debug/').mkdir(parents=True, exist_ok=True)

def annotate_pdfs(identified_content, logsheet_image, front):
    create_debug_dir()

    backside = '_back' if not front else ''

    for service, content in identified_content.items():
        visualise_regions(content, logsheet_image, f'{service}_annotated{backside}.pdf')

def visualise_regions(regions, image, output_pdf):
    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    font = load_font()

    # Iterate through OCR results and annotate the image
    for region in regions:
        draw.rectangle(region.get_coords(), outline='red')
        draw.text((region.get_start()[0], region.get_start()[1]-20), region.content, fill='red', font=font)
    
    img.save(f'debug/{output_pdf}', 'PDF', resolution=100.0)
