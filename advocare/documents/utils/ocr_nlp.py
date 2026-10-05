import os
import re

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Local Windows machine:
# You can set TESSERACT_CMD if required.
#
# Render/Docker:
# Tesseract is installed through Dockerfile and should be
# available automatically as "tesseract".

TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# OCR language
#
# eng       -> English
# eng+guj   -> English + Gujarati
#
# Start with eng. If Gujarati documents are required,
# set OCR_LANG=eng+guj in Render environment variables.
OCR_LANG = os.getenv("OCR_LANG", "eng")


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """
    Convert image to grayscale and improve contrast/sharpness.
    """

    gray = image.convert("L")

    # Improve contrast
    gray = ImageEnhance.Contrast(gray).enhance(1.8)

    # Slight sharpening
    gray = gray.filter(ImageFilter.SHARPEN)

    return gray


def preprocess_threshold(image):
    """
    Convert image into black/white threshold image.
    """

    gray = preprocess_image(image)

    return gray.point(
        lambda p: 255 if p > 160 else 0
    )


# ============================================================
# OCR
# ============================================================

def run_ocr(image, psm=6):
    """
    Run Tesseract OCR on an image.

    psm:
        6  -> Assume a uniform block of text
        11 -> Sparse text
    """

    try:
        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=f"--oem 3 --psm {psm}",
        )

        return text or ""

    except pytesseract.TesseractNotFoundError as e:
        raise RuntimeError(
            "Tesseract OCR is not installed or not available on the server."
        ) from e

    except pytesseract.TesseractError as e:
        raise RuntimeError(
            f"Tesseract OCR error: {e}"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"OCR failed: {e}"
        ) from e


# ============================================================
# IMAGE OCR
# ============================================================

def extract_text_from_image(file_path):
    """
    Extract text from JPG/JPEG/PNG/WebP etc.
    """

    try:
        image = Image.open(file_path)

        # Make sure image is loaded before file gets closed
        image.load()

    except Exception as e:
        raise RuntimeError(
            f"Could not open image: {e}"
        ) from e

    texts = []

    # Original image
    for psm in (6, 11):
        text = run_ocr(image, psm=psm)

        if text.strip():
            texts.append(text)

    # Grayscale + contrast
    processed = preprocess_image(image.copy())

    for psm in (6, 11):
        text = run_ocr(processed, psm=psm)

        if text.strip():
            texts.append(text)

    # Threshold version
    threshold = preprocess_threshold(image.copy())

    text = run_ocr(threshold, psm=6)

    if text.strip():
        texts.append(text)

    return "\n".join(texts).strip()


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text_with_pypdf2(file_path):
    """
    Try extracting text directly from a text-based PDF.
    """

    if PyPDF2 is None:
        return ""

    full_text = []

    try:
        with open(file_path, "rb") as f:

            reader = PyPDF2.PdfReader(f)

            for page in reader.pages:

                try:
                    page_text = page.extract_text() or ""

                    if page_text.strip():
                        full_text.append(page_text)

                except Exception as e:
                    print(
                        f"WARNING: Could not extract PDF page text: {e}"
                    )

    except Exception as e:
        print(
            f"WARNING: PyPDF2 failed: {e}"
        )

    return "\n".join(full_text).strip()


# ============================================================
# PDF OCR
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF.

    First:
        Try PyPDF2.

    If PDF has no readable text:
        Convert PDF pages into images using Poppler.
        Then run Tesseract OCR.
    """

    # --------------------------------------------------------
    # STEP 1: Try normal PDF text extraction
    # --------------------------------------------------------

    text_from_pdf = extract_pdf_text_with_pypdf2(file_path)

    if text_from_pdf.strip():
        return text_from_pdf.strip()

    # --------------------------------------------------------
    # STEP 2: OCR PDF pages
    # --------------------------------------------------------

    try:

        images = pdf2image.convert_from_path(
            file_path,
            dpi=250,
            fmt="jpeg",
        )

    except Exception as e:

        raise RuntimeError(
            "PDF could not be converted into images. "
            "Make sure Poppler is installed on the server."
        ) from e

    all_text = []

    for page_number, image in enumerate(images, start=1):

        print(
            f"OCR processing PDF page {page_number}"
        )

        # Original image
        for psm in (6, 11):

            text = run_ocr(
                image,
                psm=psm
            )

            if text.strip():
                all_text.append(text)

        # Preprocessed image
        processed = preprocess_image(
            image.copy()
        )

        text = run_ocr(
            processed,
            psm=6
        )

        if text.strip():
            all_text.append(text)

    return "\n".join(all_text).strip()


# ============================================================
# FILE TYPE DETECTION
# ============================================================

def extract_text_from_file(file_path):
    """
    Automatically detect PDF/image and extract text.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    if extension in (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif",
    ):

        return extract_text_from_image(
            file_path
        )

    raise RuntimeError(
        f"Unsupported document format: {extension}"
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Basic OCR text cleanup.
    """

    if not text:
        return ""

    text = text.replace("\x00", " ")

    # Normalize spaces but preserve line breaks
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# FIELD EXTRACTION
# ============================================================

def extract_name(text):
    """
    Extract a name from OCR text.
    """

    text = clean_text(text)

    patterns = [
        r"\bName\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",
        r"\bFull\s*Name\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",
        r"\bApplicant\s*Name\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",
        r"\bCandidate\s*Name\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    # Line-based fallback
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):

        if re.search(
            r"\b(full\s+)?name\b",
            line,
            re.IGNORECASE
        ):

            # Example:
            # Name
            # Kartik Prajapati

            if index + 1 < len(lines):

                candidate = lines[index + 1]

                if (
                    len(candidate) >= 3
                    and re.search(
                        r"[A-Za-z]",
                        candidate
                    )
                ):
                    return candidate

    return None


def extract_address(text):
    """
    Extract address from OCR text.
    """

    text = clean_text(text)

    patterns = [
        r"\bAddress\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",
        r"\bPermanent\s+Address\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",
        r"\bResidential\s+Address\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            address = match.group(1)

            address = re.sub(
                r"\s+",
                " ",
                address
            )

            return address.strip()

    return None


def extract_phone(text):
    """
    Extract Indian phone number.
    """

    text = clean_text(text)

    patterns = [
        r"(?:\+91[\s\-]?)?[6-9]\d{9}",
        r"\b[6-9]\d{9}\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            number = re.sub(
                r"\D",
                "",
                match.group(0)
            )

            if number.startswith("91") and len(number) == 12:
                number = number[-10:]

            if len(number) == 10:
                return number

    return None


def extract_firm_name(text):
    """
    Extract firm/company name.
    """

    text = clean_text(text)

    patterns = [
        r"\bFirm\s*Name\s*[:\-]\s*(.+)",
        r"\bCompany\s*Name\s*[:\-]\s*(.+)",
        r"\bOrganization\s*Name\s*[:\-]\s*(.+)",
        r"\bOrganisation\s*Name\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            value = match.group(1).splitlines()[0]

            return value.strip()

    return None


def extract_registration_number(text):
    """
    Extract common registration number formats.
    """

    text = clean_text(text)

    patterns = [
        r"\bRegistration\s*(?:No|Number|#)?\s*[:\-]?\s*([A-Z0-9\/\-]{4,30})",
        r"\bReg(?:istration)?\.?\s*(?:No|Number|#)?\s*[:\-]?\s*([A-Z0-9\/\-]{4,30})",
        r"\bCertificate\s*(?:No|Number|#)?\s*[:\-]?\s*([A-Z0-9\/\-]{4,30})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return None