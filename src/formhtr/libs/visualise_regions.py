from PIL import Image, ImageDraw, ImageFont
import urllib.request
from pathlib import Path


FONT_URL = 'https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf'

def load_font():
    """Return a TrueType font for overlay labels.

    Returns:
        A PIL ``ImageFont`` instance (Arial if available, else default bitmap font).

    Note:
        May download ``Arial.ttf`` into the current working directory once.
    """
    font_file = Path('Arial.ttf')
    if not font_file.is_file():
        urllib.request.urlretrieve(FONT_URL, 'Arial.ttf')

    try:
        font = ImageFont.truetype('Arial.ttf', size=30)
    except IOError:
        font = ImageFont.load_default()
    return font

def create_debug_dir():
    """Create ``debug/`` in the current working directory if missing.

    Returns:
        ``None``.
    """
    Path('debug/').mkdir(parents=True, exist_ok=True)

def annotate_pdfs(identified_content, logsheet_image, front):
    """Write one debug PDF per OCR provider under ``debug/``.

    Args:
        identified_content: Dict ``google`` / ``amazon`` / ``azure`` mapping to
            iterables of regions with ``get_coords()`` and ``content`` (may be ``None``).
        logsheet_image: Raster image (``numpy``) to draw on.
        front: If False, suffix output filenames with ``_back``.

    Returns:
        ``None``.
    """
    create_debug_dir()

    backside = '_back' if not front else ''

    for service, content in identified_content.items():
        visualise_regions(content, logsheet_image, f'{service}_annotated{backside}.pdf')

def visualise_regions(regions, image, output_pdf):
    """Draw bounding boxes and labels, save as PDF in ``debug/``.

    Args:
        regions: Iterable of objects with ``get_coords()``, ``get_start()``, ``content``.
        image: Source ``numpy`` image (RGB/BGR as supported by PIL).
        output_pdf: Filename only; written as ``debug/{output_pdf}``.

    Returns:
        ``None``.
    """
    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    font = load_font()

    # Iterate through OCR results and annotate the image
    for region in regions:
        draw.rectangle(region.get_coords(), outline='red')
        draw.text((region.get_start()[0], region.get_start()[1]-20), region.content, fill='red', font=font)
    
    img.save(f'debug/{output_pdf}', 'PDF', resolution=100.0)
