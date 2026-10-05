import os
import re
import shutil
import traceback

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from fuzzywuzzy import fuzz


# ============================================================
# CONFIGURATION
# ============================================================

# Local Windows:
# You can set TESSERACT_CMD environment variable if required.
#
# Render/Docker:
# Docker installs tesseract-ocr and Linux automatically
# finds /usr/bin/tesseract.

TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# Start with English.
# Later you can use:
# OCR_LANG=eng+guj
#
OCR_LANG = os.getenv(
    "OCR_LANG",
    "eng"
)


# Maximum image dimensions before OCR.
# This keeps Render memory usage lower.
MAX_IMAGE_WIDTH = 1800
MAX_IMAGE_HEIGHT = 1800


# PDF rendering DPI.
# 200 is enough for most Aadhaar documents
# and is much lighter than 300 DPI.
PDF_DPI = 200


# ============================================================
# SYSTEM CHECKS
# ============================================================

def check_tesseract():
    """
    Check whether Tesseract is available.
    """

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


def check_poppler():
    """
    Check whether Poppler utilities are available.
    """

    pdftoppm = shutil.which(
        "pdftoppm"
    )

    if pdftoppm:

        print(
            "Poppler found:",
            pdftoppm
        )

        return True

    print(
        "Poppler pdftoppm was not found."
    )

    return False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def resize_image(image):
    """
    Resize very large images to reduce memory usage.
    """

    original_size = image.size

    if (
        image.width <= MAX_IMAGE_WIDTH
        and
        image.height <= MAX_IMAGE_HEIGHT
    ):
        return image

    image.thumbnail(
        (
            MAX_IMAGE_WIDTH,
            MAX_IMAGE_HEIGHT
        ),
        Image.Resampling.LANCZOS
    )

    print(
        "Image resized:",
        original_size,
        "->",
        image.size
    )

    return image


def preprocess_image(image):
    """
    Basic grayscale + contrast + sharpening.

    Kept intentionally lightweight for Render.
    """

    gray = image.convert("L")

    gray = ImageEnhance.Contrast(
        gray
    ).enhance(1.5)

    gray = gray.filter(
        ImageFilter.SHARPEN
    )

    return gray


# ============================================================
# OCR
# ============================================================

def run_ocr(image, psm=6):
    """
    Run Tesseract OCR.
    """

    print(
        f"Starting Tesseract OCR with PSM {psm}..."
    )

    try:

        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=f"--oem 3 --psm {psm}"
        )

        print(
            f"Tesseract OCR finished with PSM {psm}."
        )

        return text or ""

    except pytesseract.TesseractNotFoundError as e:

        print(
            "TESSERACT NOT FOUND"
        )

        raise RuntimeError(
            "Tesseract OCR is not installed "
            "or cannot be found on the server."
        ) from e

    except Exception as e:

        print(
            "TESSERACT ERROR:",
            repr(e)
        )

        raise RuntimeError(
            f"Tesseract OCR failed: {str(e)}"
        ) from e


# ============================================================
# IMAGE TEXT EXTRACTION
# ============================================================

def extract_text_from_image(file_path):
    """
    Extract text from JPG/JPEG/PNG.

    Render-friendly:
    - Resize large images
    - Only 2 OCR passes
    """

    print("==========================================")
    print("IMAGE OCR START")
    print("File:", file_path)

    try:

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        image = Image.open(
            file_path
        )

        print(
            "Original image size:",
            image.size
        )

        print(
            "Original image mode:",
            image.mode
        )

        # ----------------------------------------------------
        # Convert image mode
        # ----------------------------------------------------

        if image.mode not in (
            "RGB",
            "L"
        ):

            image = image.convert(
                "RGB"
            )

        # ----------------------------------------------------
        # Resize large image
        # ----------------------------------------------------

        image = resize_image(
            image
        )

        print(
            "OCR image size:",
            image.size
        )

        texts = []

        # ====================================================
        # OCR PASS 1
        # Original image
        # ====================================================

        print(
            "Running OCR pass 1..."
        )

        text1 = run_ocr(
            image,
            psm=6
        )

        print(
            "OCR pass 1 characters:",
            len(text1)
        )

        if text1.strip():

            texts.append(
                text1
            )

        # ====================================================
        # OCR PASS 2
        # Grayscale / contrast
        # ====================================================

        print(
            "Running OCR pass 2..."
        )

        processed = preprocess_image(
            image.copy()
        )

        text2 = run_ocr(
            processed,
            psm=11
        )

        print(
            "OCR pass 2 characters:",
            len(text2)
        )

        if text2.strip():

            texts.append(
                text2
            )

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        final_text = "\n".join(
            texts
        ).strip()

        print(
            "FINAL OCR CHARACTERS:",
            len(final_text)
        )

        print(
            "IMAGE OCR COMPLETED"
        )

        print("==========================================")

        return final_text

    except Exception as e:

        print("==========================================")
        print("IMAGE OCR ERROR")
        print(
            "Error type:",
            type(e).__name__
        )
        print(
            "Error:",
            str(e)
        )

        traceback.print_exc()

        print("==========================================")

        raise RuntimeError(
            f"Image OCR failed: {str(e)}"
        ) from e


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF.

    First tries PyPDF2 for text-based PDFs.

    If no text is found:
    PDF pages are converted to images using Poppler,
    then OCR is performed.
    """

    print("==========================================")
    print("PDF OCR START")
    print("File:", file_path)

    full_text = ""

    # ========================================================
    # STEP 1: Try PyPDF2
    # ========================================================

    if PyPDF2 is not None:

        try:

            print(
                "Trying PyPDF2 text extraction..."
            )

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

                page_texts = []

                for page in reader.pages:

                    page_text = (
                        page.extract_text()
                        or ""
                    )

                    if page_text.strip():

                        page_texts.append(
                            page_text
                        )

                full_text = "\n".join(
                    page_texts
                ).strip()

            print(
                "PyPDF2 extracted characters:",
                len(full_text)
            )

        except Exception as e:

            print(
                "PyPDF2 failed:",
                repr(e)
            )

    # ========================================================
    # If PDF already contains text
    # ========================================================

    if full_text:

        print(
            "PDF text extraction successful."
        )

        print(
            "=========================================="
        )

        return full_text

    # ========================================================
    # STEP 2: OCR scanned PDF
    # ========================================================

    print(
        "No usable PDF text found."
    )

    print(
        "Starting PDF -> image conversion..."
    )

    if not check_poppler():

        raise RuntimeError(
            "Poppler is not installed. "
            "Install poppler-utils in Docker."
        )

    try:

        images = pdf2image.convert_from_path(
            file_path,
            dpi=PDF_DPI
        )

    except Exception as e:

        print(
            "PDF conversion failed:",
            repr(e)
        )

        traceback.print_exc()

        raise RuntimeError(
            "Could not convert PDF to image. "
            "Make sure Poppler is installed."
        ) from e

    print(
        "PDF converted pages:",
        len(images)
    )

    all_text = []

    # ========================================================
    # OCR each page
    # ========================================================

    for page_number, image in enumerate(
        images,
        start=1
    ):

        print(
            f"Processing PDF page {page_number}..."
        )

        image = resize_image(
            image
        )

        # ----------------------------------------------
        # Pass 1
        # ----------------------------------------------

        text1 = run_ocr(
            image,
            psm=6
        )

        if text1.strip():

            all_text.append(
                text1
            )

        # ----------------------------------------------
        # Pass 2
        # ----------------------------------------------

        processed = preprocess_image(
            image.copy()
        )

        text2 = run_ocr(
            processed,
            psm=11
        )

        if text2.strip():

            all_text.append(
                text2
            )

    full_text = "\n".join(
        all_text
    ).strip()

    print(
        "FINAL PDF OCR CHARACTERS:",
        len(full_text)
    )

    print(
        "PDF OCR COMPLETED"
    )

    print(
        "=========================================="
    )

    return full_text


# ============================================================
# GENERIC FILE TEXT EXTRACTION
# ============================================================

def extract_text_from_file(file_path):
    """
    Detect extension and extract text.
    """

    extension = os.path.splitext(
        file_path
    )[1].lower()

    print(
        "Processing extension:",
        extension
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
        "Unsupported file type. "
        "Use PDF, JPG, JPEG or PNG."
    )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Normalize OCR/user text for comparison.
    """

    if not value:

        return ""

    value = str(
        value
    )

    value = value.lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = re.sub(
        r"[^\w\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def fuzzy_match(
    expected,
    actual,
    threshold=65
):
    """
    Fuzzy comparison for OCR text.
    """

    if not expected or not actual:

        return False

    expected_normalized = normalize_text(
        expected
    )

    actual_normalized = normalize_text(
        actual
    )

    if not expected_normalized:
        return False

    if not actual_normalized:
        return False

    score = fuzz.partial_ratio(
        expected_normalized,
        actual_normalized
    )

    print(
        "Fuzzy comparison:",
        expected_normalized,
        "|",
        actual_normalized,
        "| score:",
        score
    )

    return score >= threshold


# ============================================================
# AADHAAR DETECTION
# ============================================================

def detect_aadhaar_keyword(text):
    """
    Detect Aadhaar-related words.

    OCR can make mistakes, so fuzzy matching is used.
    """

    if not text:

        return False

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

            print(
                "Aadhaar keyword detected:",
                keyword
            )

            return True

    # --------------------------------------------------------
    # Fuzzy line matching
    # --------------------------------------------------------

    for line in normalized.split("\n"):

        line = line.strip()

        if not line:
            continue

        for keyword in (
            "aadhaar",
            "aadhar",
            "uidai",
        ):

            score = fuzz.partial_ratio(
                keyword,
                line
            )

            if score >= 70:

                print(
                    "Fuzzy Aadhaar keyword detected:",
                    keyword,
                    score
                )

                return True

    return False


def detect_aadhaar_number(text):
    """
    Detect 12-digit Aadhaar number.

    Spaces may occur between groups.
    """

    if not text:

        return False

    # Example:
    # 1234 5678 9012
    grouped_pattern = (
        r"\b\d{4}[\s\-]+\d{4}[\s\-]+\d{4}\b"
    )

    if re.search(
        grouped_pattern,
        text
    ):

        return True

    # Example:
    # 123456789012
    compact_pattern = (
        r"\b\d{12}\b"
    )

    if re.search(
        compact_pattern,
        text
    ):

        return True

    return False


def detect_aadhaar_document(text):
    """
    Aadhaar is considered detected if:
    - Aadhaar keyword exists, OR
    - a 12 digit Aadhaar-like number exists.
    """

    keyword_found = (
        detect_aadhaar_keyword(
            text
        )
    )

    number_found = (
        detect_aadhaar_number(
            text
        )
    )

    print(
        "Aadhaar keyword:",
        keyword_found
    )

    print(
        "Aadhaar number:",
        number_found
    )

    return (
        keyword_found
        or
        number_found
    )


# ============================================================
# FIELD EXTRACTION
# ============================================================

def extract_name(text):
    """
    Try to extract name from OCR text.
    """

    if not text:
        return ""

    patterns = [

        r"\bname\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",

        r"\bname\s+([A-Za-z][A-Za-z .]{2,80})",

        r"\bto\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,80})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = (
                match.group(1)
                .strip()
            )

            value = re.sub(
                r"\s+",
                " ",
                value
            )

            return value

    # --------------------------------------------------------
    # Line based fallback
    # --------------------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):

        if re.search(
            r"\bname\b",
            line,
            re.IGNORECASE
        ):

            # Name: Rahul Patel
            parts = re.split(
                r"name\s*[:\-]?\s*",
                line,
                flags=re.IGNORECASE
            )

            if len(parts) > 1:

                candidate = (
                    parts[1].strip()
                )

                if candidate:

                    return candidate

            # Name on next line
            if index + 1 < len(lines):

                candidate = (
                    lines[index + 1]
                )

                if re.match(
                    r"^[A-Za-z .]{3,80}$",
                    candidate
                ):

                    return candidate

    return ""


def extract_address(text):
    """
    Try to extract address.
    """

    if not text:
        return ""

    patterns = [

        r"\baddress\s*[:\-]\s*(.{10,250})",

        r"\bresident\s+of\s*[:\-]\s*(.{10,250})",

        r"\baddr\s*[:\-]\s*(.{10,250})",
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


def extract_phone(text):
    """
    Extract Indian phone number.
    """

    if not text:
        return ""

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

            phone = re.sub(
                r"\D",
                "",
                match.group(0)
            )

            if phone.startswith("91") and len(phone) == 12:

                phone = phone[2:]

            return phone

    return ""


def extract_firm_name(text):
    """
    Try to extract law firm name.
    """

    if not text:
        return ""

    patterns = [

        r"\bfirm\s*name\s*[:\-]\s*(.{2,150})",

        r"\blaw\s+firm\s*[:\-]\s*(.{2,150})",

        r"\bfirm\s*[:\-]\s*(.{2,150})",
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


def extract_registration_number(text):
    """
    Try to extract registration/certificate number.
    """

    if not text:
        return ""

    patterns = [

        r"\bregistration\s*(?:no|number)?\s*[:\-]\s*([A-Za-z0-9\/\-_]{3,50})",

        r"\breg\.?\s*(?:no|number)?\s*[:\-]\s*([A-Za-z0-9\/\-_]{3,50})",

        r"\bcertificate\s*(?:no|number)?\s*[:\-]\s*([A-Za-z0-9\/\-_]{3,50})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
            )

    return ""


# ============================================================
# PHONE COMPARISON
# ============================================================

def phone_match(
    expected,
    actual
):
    """
    Compare phone numbers.
    """

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

    if expected_digits.startswith("91"):

        expected_digits = (
            expected_digits[-10:]
        )

    if actual_digits.startswith("91"):

        actual_digits = (
            actual_digits[-10:]
        )

    return (
        expected_digits
        and actual_digits
        and
        expected_digits == actual_digits
    )


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

def normalize_document_type(
    expected_type
):
    """
    Normalize frontend document type.
    """

    if not expected_type:

        return ""

    value = normalize_text(
        expected_type
    )

    mapping = {

        "aadhar": "aadhar",
        "aadhaar": "aadhar",
        "aadhaar card": "aadhar",
        "aadhar card": "aadhar",
        "id proof": "aadhar",

        "bar council": "bar_council",
        "bar council certificate": "bar_council",
        "bar registration": "bar_council",

        "firm registration": "firm_registration",
        "firm registration certificate":
            "firm_registration",

        "registration certificate":
            "firm_registration",

        "fir": "fir",

        "notice": "notice",

        "legal notice": "notice",
    }

    return mapping.get(
        value,
        value.replace(
            " ",
            "_"
        )
    )


# ============================================================
# GENERIC DOCUMENT KEYWORD CHECK
# ============================================================

def contains_any_keyword(
    text,
    keywords
):
    """
    Check whether OCR text contains any keyword.
    """

    normalized = normalize_text(
        text
    )

    for keyword in keywords:

        if (
            normalize_text(
                keyword
            )
            in normalized
        ):

            return True

    return False


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

    This function:
    1. OCRs the document.
    2. Detects document type.
    3. Extracts fields.
    4. Compares expected information.
    """

    print("==========================================")
    print("VERIFY DOCUMENT START")
    print("File:", file_path)
    print("Expected type:", expected_type)
    print("==========================================")

    # ========================================================
    # Validate file
    # ========================================================

    if not file_path:

        return {
            "valid": False,
            "message": "Document file is required.",
            "extracted": {},
        }

    if not os.path.exists(
        file_path
    ):

        return {
            "valid": False,
            "message": "Temporary document file was not found.",
            "extracted": {},
        }

    try:

        file_size = os.path.getsize(
            file_path
        )

        print(
            "Document size:",
            file_size
        )

    except Exception:

        file_size = 0

    if file_size == 0:

        return {
            "valid": False,
            "message": "Uploaded document is empty.",
            "extracted": {},
        }

    # ========================================================
    # OCR
    # ========================================================

    try:

        print(
            "Starting document text extraction..."
        )

        text = extract_text_from_file(
            file_path
        )

    except Exception as e:

        print(
            "DOCUMENT OCR FAILED:",
            repr(e)
        )

        traceback.print_exc()

        return {
            "valid": False,
            "message": str(e),
            "extracted": {},
        }

    # ========================================================
    # No OCR text
    # ========================================================

    if not text or not text.strip():

        print(
            "OCR returned EMPTY TEXT."
        )

        return {
            "valid": False,
            "message":
                "Could not read document. "
                "Upload a clear image/PDF.",
            "extracted": {},
        }

    # ========================================================
    # Debug OCR information
    # ========================================================

    print("==========================================")
    print("OCR TEXT LENGTH:", len(text))
    print("OCR TEXT PREVIEW:")
    print(
        text[:3000]
    )
    print("==========================================")

    # ========================================================
    # Normalize expected type
    # ========================================================

    document_type = normalize_document_type(
        expected_type
    )

    print(
        "Normalized document type:",
        document_type
    )

    # ========================================================
    # Extract common fields
    # ========================================================

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

        "registration_no":
            extracted_registration_number,
    }

    print(
        "EXTRACTED DATA:",
        extracted
    )

    # ========================================================
    # Verification result
    # ========================================================

    valid = True

    messages = []

    # ========================================================
    # AADHAAR
    # ========================================================

    if document_type == "aadhar":

        print(
            "Running Aadhaar verification..."
        )

        aadhaar_detected = (
            detect_aadhaar_document(
                text
            )
        )

        extracted[
            "aadhaar_detected"
        ] = aadhaar_detected

        if not aadhaar_detected:

            valid = False

            messages.append(
                "Aadhaar document could not be detected."
            )

        # ----------------------------------------------------
        # Expected name
        # ----------------------------------------------------

        expected_name = kwargs.get(
            "expected_name"
        )

        if expected_name:

            name_ok = fuzzy_match(
                expected_name,
                extracted_name,
                threshold=60
            )

            extracted[
                "name_match"
            ] = name_ok

            if not name_ok:

                # Try against complete OCR text
                name_ok = fuzzy_match(
                    expected_name,
                    text,
                    threshold=70
                )

                extracted[
                    "name_match"
                ] = name_ok

            if not name_ok:

                valid = False

                messages.append(
                    "Name could not be verified against Aadhaar."
                )

        # ----------------------------------------------------
        # Expected phone
        # ----------------------------------------------------

        expected_phone = kwargs.get(
            "expected_phone"
        )

        if expected_phone:

            phone_ok = phone_match(
                expected_phone,
                extracted_phone
            )

            extracted[
                "phone_match"
            ] = phone_ok

            if not phone_ok:

                valid = False

                messages.append(
                    "Phone number could not be verified."
                )

    # ========================================================
    # BAR COUNCIL
    # ========================================================

    elif document_type == "bar_council":

        print(
            "Running Bar Council verification..."
        )

        bar_keywords = [

            "bar council",

            "bar council of india",

            "state bar council",

            "advocate",

            "enrollment",

            "enrolment",

            "certificate of enrolment",

            "legal practitioner",
        ]

        detected = contains_any_keyword(
            text,
            bar_keywords
        )

        extracted[
            "bar_council_detected"
        ] = detected

        if not detected:

            valid = False

            messages.append(
                "Bar Council document could not be detected."
            )

        expected_name = kwargs.get(
            "expected_name"
        )

        if expected_name:

            name_ok = fuzzy_match(
                expected_name,
                text,
                threshold=60
            )

            extracted[
                "name_match"
            ] = name_ok

            if not name_ok:

                valid = False

                messages.append(
                    "Name could not be verified."
                )

        expected_registration_no = (
            kwargs.get(
                "expected_registration_no"
            )
        )

        if expected_registration_no:

            registration_ok = fuzzy_match(
                expected_registration_no,
                text,
                threshold=65
            )

            extracted[
                "registration_match"
            ] = registration_ok

            if not registration_ok:

                valid = False

                messages.append(
                    "Registration number could not be verified."
                )

    # ========================================================
    # FIRM REGISTRATION
    # ========================================================

    elif document_type == "firm_registration":

        print(
            "Running Firm Registration verification..."
        )

        firm_keywords = [

            "firm registration",

            "registration certificate",

            "registrar of firms",

            "registered firm",

            "partnership firm",

            "registration no",

            "registration number",
        ]

        detected = contains_any_keyword(
            text,
            firm_keywords
        )

        extracted[
            "firm_registration_detected"
        ] = detected

        if not detected:

            valid = False

            messages.append(
                "Firm registration document could not be detected."
            )

        expected_firm_name = (
            kwargs.get(
                "expected_firm_name"
            )
        )

        if expected_firm_name:

            firm_match = fuzzy_match(
                expected_firm_name,
                text,
                threshold=60
            )

            extracted[
                "firm_name_match"
            ] = firm_match

            if not firm_match:

                valid = False

                messages.append(
                    "Firm name could not be verified."
                )

        expected_registration_no = (
            kwargs.get(
                "expected_registration_no"
            )
        )

        if expected_registration_no:

            registration_match = fuzzy_match(
                expected_registration_no,
                text,
                threshold=65
            )

            extracted[
                "registration_match"
            ] = registration_match

            if not registration_match:

                valid = False

                messages.append(
                    "Registration number could not be verified."
                )

    # ========================================================
    # FIR
    # ========================================================

    elif document_type == "fir":

        print(
            "Running FIR verification..."
        )

        fir_keywords = [

            "first information report",

            "first information",

            "fir",

            "police station",

            "police",

            "complainant",

            "crime number",

            "fir no",

            "fir number",
        ]

        detected = contains_any_keyword(
            text,
            fir_keywords
        )

        extracted[
            "fir_detected"
        ] = detected

        if not detected:

            valid = False

            messages.append(
                "FIR document could not be detected."
            )

    # ========================================================
    # NOTICE
    # ========================================================

    elif document_type == "notice":

        print(
            "Running Legal Notice verification..."
        )

        notice_keywords = [

            "legal notice",

            "notice",

            "whereas",

            "hereby",

            "advocate",

            "legal",

            "subject",
        ]

        detected = contains_any_keyword(
            text,
            notice_keywords
        )

        extracted[
            "notice_detected"
        ] = detected

        if not detected:

            valid = False

            messages.append(
                "Legal notice could not be detected."
            )

    # ========================================================
    # UNKNOWN DOCUMENT TYPE
    # ========================================================

    else:

        print(
            "Unknown document type:",
            document_type
        )

        # For unknown types we don't reject purely
        # because the backend doesn't know the type.
        # OCR has successfully completed.

        extracted[
            "document_type_detected"
        ] = document_type

    # ========================================================
    # Final response
    # ========================================================

    if valid:

        message = (
            "Document verified successfully."
        )

    else:

        if messages:

            message = " ".join(
                messages
            )

        else:

            message = (
                "Document verification failed."
            )

    result = {

        "valid": valid,

        "message": message,

        "extracted": extracted,

        # Useful during development.
        # If you don't want OCR text returned
        # to frontend later, remove this field.
        "ocr_text": text[:5000],
    }

    print("==========================================")
    print(
        "DOCUMENT VERIFICATION RESULT:"
    )
    print(
        "Valid:",
        valid
    )
    print(
        "Message:",
        message
    )
    print("==========================================")

    return result