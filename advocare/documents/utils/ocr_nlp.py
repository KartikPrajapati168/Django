import os
import re
import shutil

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


# ============================================================
# CONFIGURATION
# ============================================================

TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD"
)

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = (
        TESSERACT_CMD
    )


OCR_LANG = os.getenv(
    "OCR_LANG",
    "eng"
)


# ============================================================
# CHECK TESSERACT
# ============================================================

def check_tesseract():

    try:

        version = pytesseract.get_tesseract_version()

        print(
            "Tesseract version:",
            version
        )

        return True

    except Exception as e:

        print(
            "Tesseract check failed:",
            repr(e)
        )

        return False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):

    gray = image.convert(
        "L"
    )

    gray = ImageEnhance.Contrast(
        gray
    ).enhance(1.8)

    gray = gray.filter(
        ImageFilter.SHARPEN
    )

    return gray


def preprocess_threshold(image):

    gray = preprocess_image(
        image
    )

    return gray.point(
        lambda p:
            255 if p > 160 else 0
    )


# ============================================================
# OCR
# ============================================================

def run_ocr(
    image,
    psm=6
):

    try:

        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=(
                f"--oem 3 --psm {psm}"
            ),
        )

        return text or ""

    except pytesseract.TesseractNotFoundError as e:

        raise RuntimeError(
            "Tesseract OCR is not installed "
            "or cannot be found on the server."
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

def extract_text_from_image(
    file_path
):

    print(
        "Starting image OCR:",
        file_path
    )

    try:

        image = Image.open(
            file_path
        )

        image.load()

    except Exception as e:

        raise RuntimeError(
            f"Could not open image: {e}"
        ) from e

    texts = []

    # --------------------------------------------------------
    # Original image
    # --------------------------------------------------------

    for psm in (
        6,
        11
    ):

        text = run_ocr(
            image,
            psm=psm
        )

        if text.strip():

            texts.append(
                text
            )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    processed = preprocess_image(
        image.copy()
    )

    for psm in (
        6,
        11
    ):

        text = run_ocr(
            processed,
            psm=psm
        )

        if text.strip():

            texts.append(
                text
            )

    # --------------------------------------------------------
    # Threshold
    # --------------------------------------------------------

    threshold = preprocess_threshold(
        image.copy()
    )

    text = run_ocr(
        threshold,
        psm=6
    )

    if text.strip():

        texts.append(
            text
        )

    final_text = "\n".join(
        texts
    ).strip()

    print(
        "OCR text length:",
        len(final_text)
    )

    return final_text


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text_with_pypdf2(
    file_path
):

    if PyPDF2 is None:

        print(
            "PyPDF2 is not installed."
        )

        return ""

    texts = []

    try:

        with open(
            file_path,
            "rb"
        ) as f:

            reader = PyPDF2.PdfReader(
                f
            )

            print(
                "PDF pages:",
                len(reader.pages)
            )

            for page in reader.pages:

                try:

                    page_text = (
                        page.extract_text()
                        or ""
                    )

                    if page_text.strip():

                        texts.append(
                            page_text
                        )

                except Exception as e:

                    print(
                        "PDF page extraction failed:",
                        repr(e)
                    )

    except Exception as e:

        print(
            "PyPDF2 failed:",
            repr(e)
        )

        return ""

    return "\n".join(
        texts
    ).strip()


# ============================================================
# PDF OCR
# ============================================================

def extract_text_from_pdf(
    file_path
):

    print(
        "Starting PDF processing:",
        file_path
    )

    # --------------------------------------------------------
    # STEP 1 - Direct PDF text
    # --------------------------------------------------------

    direct_text = (
        extract_pdf_text_with_pypdf2(
            file_path
        )
    )

    if direct_text.strip():

        print(
            "PDF text extracted using PyPDF2."
        )

        return direct_text.strip()

    print(
        "No usable PDF text found."
    )

    # --------------------------------------------------------
    # STEP 2 - PDF -> Image using Poppler
    # --------------------------------------------------------

    try:

        images = (
            pdf2image.convert_from_path(
                file_path,
                dpi=250,
                fmt="jpeg"
            )
        )

    except Exception as e:

        print(
            "PDF to image conversion failed:",
            repr(e)
        )

        raise RuntimeError(
            "Could not convert PDF to image. "
            "Make sure Poppler is installed."
        ) from e

    print(
        "PDF converted to images:",
        len(images)
    )

    all_text = []

    for page_number, image in enumerate(
        images,
        start=1
    ):

        print(
            f"Processing PDF page {page_number}"
        )

        # ----------------------------------------------------
        # Original
        # ----------------------------------------------------

        for psm in (
            6,
            11
        ):

            text = run_ocr(
                image,
                psm=psm
            )

            if text.strip():

                all_text.append(
                    text
                )

        # ----------------------------------------------------
        # Processed
        # ----------------------------------------------------

        processed = preprocess_image(
            image.copy()
        )

        text = run_ocr(
            processed,
            psm=6
        )

        if text.strip():

            all_text.append(
                text
            )

    return "\n".join(
        all_text
    ).strip()


# ============================================================
# FILE OCR
# ============================================================

def extract_text_from_file(
    file_path
):

    if not os.path.exists(
        file_path
    ):

        raise RuntimeError(
            "Temporary document file does not exist."
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    print(
        "Processing extension:",
        extension
    )

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

    if not text:

        return ""

    text = text.replace(
        "\x00",
        " "
    )

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
# NAME
# ============================================================

def extract_name(text):

    text = clean_text(
        text
    )

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

            return match.group(
                1
            ).strip()

    return None


# ============================================================
# ADDRESS
# ============================================================

def extract_address(text):

    text = clean_text(
        text
    )

    patterns = [

        r"\bAddress\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",

        r"\bPermanent\s+Address\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",

        r"\bResidential\s+Address\s*[:\-]\s*(.+?)(?=\n(?:Phone|Mobile|Email|DOB|Date|Name)\b|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=(
                re.IGNORECASE
                |
                re.DOTALL
            )
        )

        if match:

            address = re.sub(
                r"\s+",
                " ",
                match.group(1)
            )

            return address.strip()

    return None


# ============================================================
# PHONE
# ============================================================

def extract_phone(text):

    text = clean_text(
        text
    )

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

            if (
                number.startswith("91")
                and
                len(number) == 12
            ):

                number = number[-10:]

            if len(number) == 10:

                return number

    return None


# ============================================================
# FIRM NAME
# ============================================================

def extract_firm_name(text):

    text = clean_text(
        text
    )

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

            return (
                match.group(1)
                .splitlines()[0]
                .strip()
            )

    return None


# ============================================================
# REGISTRATION NUMBER
# ============================================================

def extract_registration_number(
    text
):

    text = clean_text(
        text
    )

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

            return match.group(
                1
            ).strip()

    return None