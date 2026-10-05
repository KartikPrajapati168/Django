# documents/utils/ocr_nlp.py

import os
import re
import shutil
import traceback

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

import pdf2image

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from fuzzywuzzy import fuzz


# ============================================================
# CONFIGURATION
# ============================================================

# IMPORTANT:
# Do NOT hard-code Windows Tesseract path.
#
# Local Windows:
# Set TESSERACT_CMD environment variable if required.
#
# Render Linux:
# Docker installs tesseract and this code automatically finds it.

TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


OCR_LANG = os.getenv("OCR_LANG", "eng")

# Keep this LOW because Render Free has limited memory.
MAX_IMAGE_DIMENSION = 2200

# PDF resolution.
# 200 DPI is enough for most ID documents and uses less memory than 300 DPI.
PDF_DPI = 200


# ============================================================
# LOGGING
# ============================================================

def log(message):
    print(f"[OCR] {message}", flush=True)


# ============================================================
# TESSERACT CHECK
# ============================================================

def check_tesseract():
    """
    Check whether Tesseract is available.
    """

    try:

        version = pytesseract.get_tesseract_version()

        log(f"Tesseract detected: {version}")

        return True

    except Exception as e:

        log(f"Tesseract check failed: {repr(e)}")

        raise RuntimeError(
            "Tesseract OCR is not available on the server. "
            "Make sure tesseract-ocr is installed."
        )


# ============================================================
# IMAGE RESIZE
# ============================================================

def resize_image_if_needed(image):
    """
    Prevent very large images from consuming huge RAM.
    """

    width, height = image.size

    largest_dimension = max(width, height)

    if largest_dimension <= MAX_IMAGE_DIMENSION:

        return image

    scale = MAX_IMAGE_DIMENSION / largest_dimension

    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))

    log(
        f"Resizing image "
        f"{width}x{height} -> "
        f"{new_width}x{new_height}"
    )

    return image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """
    Lightweight preprocessing.
    """

    image = resize_image_if_needed(image)

    # Convert to grayscale
    image = image.convert("L")

    # Improve contrast
    image = ImageEnhance.Contrast(image).enhance(1.5)

    # Slight sharpening
    image = image.filter(ImageFilter.SHARPEN)

    return image


def preprocess_threshold(image):
    """
    Black/white version.
    """

    image = preprocess_image(image)

    # Autocontrast
    image = ImageOps.autocontrast(image)

    # Threshold
    image = image.point(
        lambda pixel: 255 if pixel > 160 else 0
    )

    return image


# ============================================================
# OCR
# ============================================================

def run_ocr(image, psm=6):
    """
    Run Tesseract OCR.

    IMPORTANT:
    Only one OCR call at a time.
    """

    try:

        check_tesseract()

        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=f"--oem 3 --psm {psm}"
        )

        return text or ""

    except pytesseract.TesseractNotFoundError as e:

        raise RuntimeError(
            "Tesseract OCR is not installed/configured on Render."
        ) from e

    except Exception as e:

        log(f"Tesseract OCR error: {repr(e)}")

        raise RuntimeError(
            f"Tesseract OCR failed: {str(e)}"
        ) from e


# ============================================================
# IMAGE OCR
# ============================================================

def extract_text_from_image(file_path):
    """
    Extract text from JPG/JPEG/PNG.

    IMPORTANT:
    This version intentionally uses very few OCR passes
    to prevent Render Free OOM.
    """

    log("==========================================")
    log(f"Starting image OCR: {file_path}")
    log("==========================================")

    try:

        image = Image.open(file_path)

        log(
            f"Original image size: "
            f"{image.size}"
        )

        # Convert + resize
        image = resize_image_if_needed(image)

        log(
            f"Processing image size: "
            f"{image.size}"
        )

        # ----------------------------------------------------
        # PASS 1
        # Normal grayscale
        # ----------------------------------------------------

        processed = preprocess_image(
            image.copy()
        )

        text = run_ocr(
            processed,
            psm=6
        )

        log(
            f"OCR pass 1 characters: "
            f"{len(text)}"
        )

        # If enough text is already detected,
        # don't waste memory on another OCR pass.
        if len(text.strip()) >= 40:

            return text.strip()

        # ----------------------------------------------------
        # PASS 2
        # Threshold only if required
        # ----------------------------------------------------

        log("OCR pass 1 produced little text.")
        log("Starting OCR pass 2...")

        threshold_image = preprocess_threshold(
            image.copy()
        )

        text2 = run_ocr(
            threshold_image,
            psm=11
        )

        log(
            f"OCR pass 2 characters: "
            f"{len(text2)}"
        )

        combined = "\n".join(
            [
                text,
                text2
            ]
        ).strip()

        return combined

    except Exception as e:

        log(
            f"IMAGE OCR FAILED: "
            f"{repr(e)}"
        )

        traceback.print_exc()

        raise RuntimeError(
            f"Image OCR failed: {str(e)}"
        ) from e

    finally:

        log("Image OCR finished.")


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF.

    First tries PyPDF2.
    If PDF is scanned/image-based,
    falls back to Poppler + Tesseract.
    """

    log("==========================================")
    log(f"Starting PDF processing: {file_path}")
    log("==========================================")

    full_text = ""

    # --------------------------------------------------------
    # STEP 1 - Try normal PDF text extraction
    # --------------------------------------------------------

    if PyPDF2 is not None:

        try:

            log("Trying PyPDF2 text extraction...")

            with open(
                file_path,
                "rb"
            ) as pdf_file:

                reader = PyPDF2.PdfReader(
                    pdf_file
                )

                # Limit pages to prevent memory issues.
                pages = reader.pages[:3]

                for page in pages:

                    page_text = (
                        page.extract_text()
                        or ""
                    )

                    if page_text.strip():

                        full_text += (
                            page_text
                            + "\n"
                        )

            if full_text.strip():

                log(
                    f"PyPDF2 extracted "
                    f"{len(full_text)} characters"
                )

                return full_text.strip()

        except Exception as e:

            log(
                f"PyPDF2 failed: {repr(e)}"
            )

    # --------------------------------------------------------
    # STEP 2 - Check Poppler
    # --------------------------------------------------------

    poppler_path = shutil.which(
        "pdftoppm"
    )

    if not poppler_path:

        raise RuntimeError(
            "Poppler is not installed on the server. "
            "Install poppler-utils in Docker."
        )

    log(
        f"Poppler detected: "
        f"{poppler_path}"
    )

    # --------------------------------------------------------
    # STEP 3 - Convert PDF to image
    # --------------------------------------------------------

    try:

        log(
            f"Converting PDF at "
            f"{PDF_DPI} DPI..."
        )

        images = pdf2image.convert_from_path(
            file_path,
            dpi=PDF_DPI,
            first_page=1,
            last_page=3,
            fmt="jpeg",
            thread_count=1
        )

    except Exception as e:

        log(
            f"PDF conversion failed: "
            f"{repr(e)}"
        )

        raise RuntimeError(
            f"PDF could not be converted to image: {str(e)}"
        ) from e

    # --------------------------------------------------------
    # STEP 4 - OCR pages
    # --------------------------------------------------------

    chunks = []

    for index, image in enumerate(
        images,
        start=1
    ):

        log(
            f"Processing PDF page {index}"
        )

        try:

            image = resize_image_if_needed(
                image
            )

            processed = preprocess_image(
                image.copy()
            )

            text = run_ocr(
                processed,
                psm=6
            )

            if text.strip():

                chunks.append(text)

            log(
                f"Page {index} OCR chars: "
                f"{len(text)}"
            )

        except Exception as e:

            log(
                f"Page {index} OCR failed: "
                f"{repr(e)}"
            )

    full_text = "\n".join(
        chunks
    ).strip()

    log(
        f"Final PDF OCR chars: "
        f"{len(full_text)}"
    )

    return full_text


# ============================================================
# FILE TYPE HANDLER
# ============================================================

def extract_text_from_file(file_path):
    """
    Detect file type and extract text.
    """

    extension = (
        os.path.splitext(
            file_path
        )[1]
        .lower()
    )

    log(
        f"File extension detected: "
        f"{extension}"
    )

    if extension in (
        ".jpg",
        ".jpeg",
        ".png"
    ):

        return extract_text_from_image(
            file_path
        )

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    raise RuntimeError(
        f"Unsupported document format: {extension}"
    )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):
    """
    Try to extract a person's name.
    """

    if not text:
        return ""

    patterns = [

        r"\bname\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",

        r"\bनाम\s*[:\-]?\s*([A-Za-z .]{2,80})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            value = re.sub(
                r"\s+",
                " ",
                value
            ).strip()

            return value

    # Fallback:
    # Search lines containing "name"

    for line in text.splitlines():

        clean = line.strip()

        if not clean:
            continue

        if (
            "name" in clean.lower()
            and len(clean) < 100
        ):

            clean = re.sub(
                r"(?i).*?name\s*[:\-]?\s*",
                "",
                clean
            )

            clean = clean.strip()

            if clean:
                return clean

    return ""


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(text):
    if not text:
        return ""

    patterns = [

        r"\baddress\s*[:\-]\s*(.+)",

        r"\baddr\s*[:\-]\s*(.+)",

        r"\bपता\s*[:\-]?\s*(.+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return re.sub(
                r"\s+",
                " ",
                match.group(1)
            ).strip()

    return ""


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text):
    if not text:
        return ""

    # Indian mobile number
    patterns = [

        r"\b[6-9]\d{9}\b",

        r"\+91[\s\-]?[6-9]\d{9}",

        r"91[\s\-]?[6-9]\d{9}",

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

            if number.startswith("91"):
                number = number[-10:]

            return number

    return ""


# ============================================================
# FIRM NAME
# ============================================================

def extract_firm_name(text):
    if not text:
        return ""

    patterns = [

        r"\bfirm\s*name\s*[:\-]\s*(.+)",

        r"\bfirm\s*[:\-]\s*(.+)",

        r"\bcompany\s*name\s*[:\-]\s*(.+)",

        r"\bcompany\s*[:\-]\s*(.+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return re.sub(
                r"\s+",
                " ",
                match.group(1)
            ).strip()

    return ""


# ============================================================
# REGISTRATION NUMBER
# ============================================================

def extract_registration_number(text):
    if not text:
        return ""

    patterns = [

        r"\bregistration\s*(?:no|number)?\s*[:\-]\s*([A-Za-z0-9\/\-]+)",

        r"\breg(?:istration)?\.?\s*(?:no|number)?\s*[:\-]\s*([A-Za-z0-9\/\-]+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

    return ""


# ============================================================
# AADHAAR DETECTION
# ============================================================

def detect_aadhaar_keyword(text):
    """
    Detect Aadhaar-related words.
    """

    normalized = normalize_text(
        text
    )

    keywords = [

        "aadhaar",
        "aadhar",
        "uidai",
        "unique identification",
        "government of india",
        "आधार",

    ]

    for keyword in keywords:

        if keyword in normalized:

            return True

    # OCR may make spelling mistakes.
    words = normalized.split()

    for word in words:

        if fuzz.ratio(
            word,
            "aadhaar"
        ) >= 72:

            return True

        if fuzz.ratio(
            word,
            "aadhar"
        ) >= 75:

            return True

    return False


def detect_aadhaar_number(text):
    """
    Aadhaar is a 12 digit number.
    """

    if not text:
        return False

    # Remove spaces/dashes around digits.
    digits = re.sub(
        r"[\s\-]",
        "",
        text
    )

    matches = re.findall(
        r"\b\d{12}\b",
        digits
    )

    return len(matches) > 0


def detect_aadhaar_document(text):
    """
    Aadhaar detection using both keyword
    and 12-digit number.
    """

    keyword_found = detect_aadhaar_keyword(
        text
    )

    number_found = detect_aadhaar_number(
        text
    )

    return (
        keyword_found
        or number_found
    )


# ============================================================
# FUZZY MATCH
# ============================================================

def fuzzy_match(
    expected,
    actual,
    threshold=65
):
    if not expected or not actual:
        return False

    expected = normalize_text(
        expected
    )

    actual = normalize_text(
        actual
    )

    if expected in actual:
        return True

    score = fuzz.token_set_ratio(
        expected,
        actual
    )

    return score >= threshold


# ============================================================
# PHONE MATCH
# ============================================================

def phone_match(
    expected,
    actual
):
    if not expected or not actual:
        return False

    expected_digits = re.sub(
        r"\D",
        "",
        str(expected)
    )

    actual_digits = re.sub(
        r"\D",
        "",
        str(actual)
    )

    if len(expected_digits) >= 10:
        expected_digits = expected_digits[-10:]

    if len(actual_digits) >= 10:
        actual_digits = actual_digits[-10:]

    return (
        expected_digits
        == actual_digits
    )


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

def normalize_document_type(
    expected_type
):
    if not expected_type:
        return ""

    value = str(
        expected_type
    ).strip().lower()

    aliases = {

        "aadhar": "aadhar",
        "aadhaar": "aadhar",
        "aadhaar card": "aadhar",
        "aadhar card": "aadhar",
        "id proof": "aadhar",

        "bar council": "bar_council",
        "bar_council": "bar_council",

        "firm registration": "firm_registration",
        "firm_registration": "firm_registration",

        "fir": "fir",

        "legal notice": "notice",
        "notice": "notice",

    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# MAIN DOCUMENT VERIFICATION
# ============================================================

def verify_document(
    file_path,
    expected_type,
    **kwargs
):
    """
    Main document verification function.

    Everything is handled from this file.
    """

    log("")
    log("==========================================")
    log("DOCUMENT VERIFICATION")
    log("==========================================")

    log(
        f"File: {file_path}"
    )

    log(
        f"Expected type: {expected_type}"
    )

    try:

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        text = extract_text_from_file(
            file_path
        )

    except Exception as e:

        log(
            "DOCUMENT OCR ERROR"
        )

        log(
            repr(e)
        )

        traceback.print_exc()

        return {

            "valid": False,

            "message":
                f"Document processing failed: {str(e)}",

            "extracted": {},

        }

    # --------------------------------------------------------
    # No text
    # --------------------------------------------------------

    if not text or not text.strip():

        return {

            "valid": False,

            "message":
                "Could not read document. "
                "Please upload a clear image/PDF.",

            "extracted": {},

        }

    log(
        f"Total OCR text characters: "
        f"{len(text)}"
    )

    # Do not print complete Aadhaar OCR text.
    # It may contain sensitive personal information.

    document_type = normalize_document_type(
        expected_type
    )

    # --------------------------------------------------------
    # Extract fields
    # --------------------------------------------------------

    extracted_name = extract_name(
        text
    )

    extracted_address = extract_address(
        text
    )

    extracted_phone = extract_phone(
        text
    )

    extracted_firm_name = extract_firm_name(
        text
    )

    extracted_registration_number = (
        extract_registration_number(
            text
        )
    )

    extracted = {

        "name": extracted_name,

        "address": extracted_address,

        "phone": extracted_phone,

        "firm_name": extracted_firm_name,

        "registration_number":
            extracted_registration_number,

    }

    # --------------------------------------------------------
    # AADHAAR
    # --------------------------------------------------------

    if document_type == "aadhar":

        aadhaar_keyword = (
            detect_aadhaar_keyword(
                text
            )
        )

        aadhaar_number = (
            detect_aadhaar_number(
                text
            )
        )

        aadhaar_detected = (
            aadhaar_keyword
            or aadhaar_number
        )

        extracted[
            "aadhaar_keyword_detected"
        ] = aadhaar_keyword

        extracted[
            "aadhaar_number_detected"
        ] = aadhaar_number

        if not aadhaar_detected:

            return {

                "valid": False,

                "message":
                    "This document does not appear "
                    "to be an Aadhaar document.",

                "extracted":
                    extracted,

            }

        # ----------------------------------------------------
        # Expected name check
        # ----------------------------------------------------

        expected_name = kwargs.get(
            "expected_name"
        )

        if expected_name:

            name_valid = fuzzy_match(
                expected_name,
                extracted_name,
                threshold=60
            )

            extracted[
                "name_match"
            ] = name_valid

            if not name_valid:

                return {

                    "valid": False,

                    "message":
                        "Aadhaar detected, but the "
                        "name does not match.",

                    "extracted":
                        extracted,

                }

        # ----------------------------------------------------
        # Expected phone check
        # ----------------------------------------------------

        expected_phone = kwargs.get(
            "expected_phone"
        )

        if expected_phone and extracted_phone:

            phone_valid = phone_match(
                expected_phone,
                extracted_phone
            )

            extracted[
                "phone_match"
            ] = phone_valid

        return {

            "valid": True,

            "message":
                "Aadhaar document verified successfully.",

            "extracted":
                extracted,

        }

    # --------------------------------------------------------
    # BAR COUNCIL
    # --------------------------------------------------------

    if document_type == "bar_council":

        normalized = normalize_text(
            text
        )

        keywords = [

            "bar council",
            "bar council of india",
            "advocate",
            "enrollment",

        ]

        detected = any(
            keyword in normalized
            for keyword in keywords
        )

        if not detected:

            return {

                "valid": False,

                "message":
                    "This does not appear to be "
                    "a Bar Council document.",

                "extracted":
                    extracted,

            }

        expected_name = kwargs.get(
            "expected_name"
        )

        if expected_name and extracted_name:

            extracted[
                "name_match"
            ] = fuzzy_match(
                expected_name,
                extracted_name,
                threshold=60
            )

        return {

            "valid": True,

            "message":
                "Bar Council document detected successfully.",

            "extracted":
                extracted,

        }

    # --------------------------------------------------------
    # FIRM REGISTRATION
    # --------------------------------------------------------

    if document_type == "firm_registration":

        normalized = normalize_text(
            text
        )

        keywords = [

            "registration",
            "firm",
            "company",
            "incorporation",

        ]

        detected = any(
            keyword in normalized
            for keyword in keywords
        )

        if not detected:

            return {

                "valid": False,

                "message":
                    "Firm registration document "
                    "could not be identified.",

                "extracted":
                    extracted,

            }

        expected_firm_name = kwargs.get(
            "expected_firm_name"
        )

        if (
            expected_firm_name
            and extracted_firm_name
        ):

            extracted[
                "firm_name_match"
            ] = fuzzy_match(
                expected_firm_name,
                extracted_firm_name,
                threshold=60
            )

        expected_registration_no = (
            kwargs.get(
                "expected_registration_no"
            )
        )

        if (
            expected_registration_no
            and extracted_registration_number
        ):

            extracted[
                "registration_number_match"
            ] = fuzzy_match(
                expected_registration_no,
                extracted_registration_number,
                threshold=70
            )

        return {

            "valid": True,

            "message":
                "Firm registration document "
                "detected successfully.",

            "extracted":
                extracted,

        }

    # --------------------------------------------------------
    # FIR
    # --------------------------------------------------------

    if document_type == "fir":

        normalized = normalize_text(
            text
        )

        keywords = [

            "first information report",
            "fir",
            "police station",
            "complainant",

        ]

        detected = any(
            keyword in normalized
            for keyword in keywords
        )

        if not detected:

            return {

                "valid": False,

                "message":
                    "This document does not appear "
                    "to be an FIR.",

                "extracted":
                    extracted,

            }

        return {

            "valid": True,

            "message":
                "FIR document detected successfully.",

            "extracted":
                extracted,

        }

    # --------------------------------------------------------
    # LEGAL NOTICE
    # --------------------------------------------------------

    if document_type == "notice":

        normalized = normalize_text(
            text
        )

        keywords = [

            "legal notice",
            "notice",
            "whereas",
            "hereby",

        ]

        detected = any(
            keyword in normalized
            for keyword in keywords
        )

        if not detected:

            return {

                "valid": False,

                "message":
                    "This document does not appear "
                    "to be a legal notice.",

                "extracted":
                    extracted,

            }

        return {

            "valid": True,

            "message":
                "Legal notice detected successfully.",

            "extracted":
                extracted,

        }

    # --------------------------------------------------------
    # GENERIC DOCUMENT
    # --------------------------------------------------------

    return {

        "valid": True,

        "message":
            "Document text extracted successfully.",

        "extracted":
            extracted,

    }