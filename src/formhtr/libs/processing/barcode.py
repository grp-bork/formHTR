import cv2
import zxingcpp

# Barcode formats where the check digit is optional or unused.
# pyzbar reports Interleaved 2 of 5 as I25; zxing-cpp reports it as ITF.
_UNCHECKED_SYMBOLS = frozenset({"I25", "ITF", "CODE39", "CODABAR"})


def extract_barcode(candidates):
    """Pick a barcode string from per-service single-word OCR fallbacks.

    Args:
        candidates: Dict mapping provider name to a list of ``Rectangle`` (or empty).

    Returns:
        Most frequent barcode string among singleton lists, or ``None`` if none.
    """
    barcodes = []
    for key in candidates.keys():
        if len(candidates[key]) == 1:
            barcodes.append(candidates[key][0].content)

    if barcodes:
        return max(barcodes, key=barcodes.count)


def _ocr_payloads(candidates):
    texts = set()
    for rectangles in (candidates or {}).values():
        for rectangle in rectangles:
            content = getattr(rectangle, "content", None)
            if content:
                texts.add(content)
    return texts


def _symbol_name(symbol):
    return getattr(symbol, "name", str(symbol)).upper()


def select_barcode(hits, ocr_texts):
    """Pick a payload from decoder hits, optionally confirmed by OCR.

    ``hits`` is a sequence of ``(symbol, payload)``. If ``ocr_texts`` is
    non-empty, only a payload that also appears in OCR is accepted. Among
    remaining hits, checksummed symbologies are preferred over
    ``_UNCHECKED_SYMBOLS``.
    """
    if not hits:
        return None
    if ocr_texts:
        hits = [hit for hit in hits if hit[1] in ocr_texts]
        if not hits:
            return None

    def rank(hit):
        symbol, payload = hit
        return (symbol not in _UNCHECKED_SYMBOLS, len(payload))

    return max(hits, key=rank)[1]


def decode_with_zxing(image):
    return [(_symbol_name(obj.format), obj.text) for obj in zxingcpp.read_barcodes(image)]


def decode_with_pyzbar(image):
    from formhtr.deps import configure_zbar_library_search
    configure_zbar_library_search()
    from pyzbar.pyzbar import decode

    hits = []
    for obj in decode(image):
        payload = obj.data.decode("utf-8") if isinstance(obj.data, bytes) else str(obj.data)
        hits.append((_symbol_name(obj.type), payload))
    return hits


def decode_barcode(image, ocr_texts):
    selected = select_barcode(decode_with_zxing(image), ocr_texts)
    if selected:
        return selected
    return select_barcode(decode_with_pyzbar(image), ocr_texts)


def rotate_barcode_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    angle = cv2.minAreaRect(largest_contour)[-1]
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def read_barcode(image, candidates):
    """Decode a barcode from a ROI image, with rotation retry and OCR fallback.

    Args:
        image: ROI crop as ``numpy`` BGR array.
        candidates: Per-service OCR rectangles (used to confirm a decode, or as fallback).

    Returns:
        Decoded payload string, or ``None`` if nothing is found.
    """
    ocr_texts = _ocr_payloads(candidates)

    selected = decode_barcode(image, ocr_texts)
    if selected:
        return selected

    rotated = rotate_barcode_image(image)
    if rotated is not None:
        selected = decode_barcode(rotated, ocr_texts)
        if selected:
            return selected

    return extract_barcode(candidates)
