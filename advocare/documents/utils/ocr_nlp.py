# ============================================================
# ocr_nlp.py
# ============================================================

import os
import re
import shutil
import traceback

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
from fuzzywuzzy import fuzz


# ============================================================
# CONFIGURATION
# ============================================================

DEBUG_OCR = os.getenv("DEBUG_OCR", "false").lower() == "true"


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

def configure_tesseract():
    """
    Automatically configure Tesseract for:

    Windows:
        C:\\Program Files\\Tesseract-OCR\\tesseract.exe

    Linux / Render:
        /usr/bin/tesseract

    Or use:
        TESSERACT_CMD
    environment variable.
    """

    # --------------------------------------------------------
    # 1. Environment variable
    # --------------------------------------------------------

    env_path = os.getenv("TESSERACT_CMD")

    if env_path:

        env_path = env_path.strip()

        if os.path.isfile(env_path):

            pytesseract.pytesseract.tesseract_cmd = env_path

            print(
                "✅ Tesseract configured from environment:"
            )
            print(env_path)

            return env_path

        print(
            "⚠️ TESSERACT_CMD was provided but file does not exist:"
        )
        print(env_path)

    # --------------------------------------------------------
    # 2. Windows
    # --------------------------------------------------------

    windows_paths = [

        r"C:\Program Files\Tesseract-OCR\tesseract.exe",

        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",

    ]

    for path in windows_paths:

        if os.path.isfile(path):

            pytesseract.pytesseract.tesseract_cmd = path

            print(
                "✅ Windows Tesseract found:"
            )
            print(path)

            return path

    # --------------------------------------------------------
    # 3. Linux / Render
    # --------------------------------------------------------

    linux_path = shutil.which("tesseract")

    if linux_path:

        pytesseract.pytesseract.tesseract_cmd = (
            linux_path
        )

        print(
            "✅ Linux Tesseract found:"
        )
        print(linux_path)

        return linux_path

    # --------------------------------------------------------
    # 4. Not found
    # --------------------------------------------------------

    print(
        "❌ Tesseract executable was NOT found."
    )

    return None


TESSERACT_PATH = configure_tesseract()


# ============================================================
# OCR LANGUAGE
# ============================================================

REQUESTED_OCR_LANG = os.getenv(
    "OCR_LANG",
    "eng"
)


def get_ocr_language():

    if not TESSERACT_PATH:

        return "eng"

    try:

        languages = pytesseract.get_languages(
            config=""
        )

        print(
            "Available Tesseract languages:",
            languages
        )

        requested = [
            x.strip()
            for x in REQUESTED_OCR_LANG.split("+")
            if x.strip()
        ]

        # ----------------------------------------------------
        # Requested languages available
        # ----------------------------------------------------

        if requested and all(
            language in languages
            for language in requested
        ):

            print(
                "✅ OCR language:",
                "+".join(requested)
            )

            return "+".join(requested)

        # ----------------------------------------------------
        # English fallback
        # ----------------------------------------------------

        if "eng" in languages:

            print(
                "⚠️ Requested OCR language unavailable."
            )

            print(
                "Using English OCR."
            )

            return "eng"

    except Exception as e:

        print(
            "⚠️ Language detection failed:",
            repr(e)
        )

    return "eng"


OCR_LANG = get_ocr_language()


# ============================================================
# TESSERACT HEALTH CHECK
# ============================================================

def check_tesseract():

    try:

        if not TESSERACT_PATH:

            raise Exception(
                "Tesseract executable not found."
            )

        version = (
            pytesseract.get_tesseract_version()
        )

        print(
            "========================================"
        )

        print(
            "TESSERACT CHECK"
        )

        print(
            "PATH:",
            pytesseract.pytesseract.tesseract_cmd
        )

        print(
            "VERSION:",
            version
        )

        print(
            "LANGUAGE:",
            OCR_LANG
        )

        print(
            "========================================"
        )

        return True

    except Exception as e:

        print(
            "❌ Tesseract check failed:"
        )

        print(
            repr(e)
        )

        return False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_grayscale(image):

    image = image.convert("L")

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.8)

    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


def preprocess_threshold(image):

    image = preprocess_grayscale(
        image
    )

    return image.point(
        lambda pixel:
        255 if pixel > 150 else 0
    )


def upscale_image(image):

    width, height = image.size

    # Don't make already huge images unnecessarily huge
    if width >= 1800:

        return image

    return image.resize(
        (
            width * 2,
            height * 2
        )
    )


# ============================================================
# SINGLE OCR
# ============================================================

def run_ocr(
    image,
    psm=6
):

    if not TESSERACT_PATH:

        raise Exception(
            "Tesseract OCR is not installed."
        )

    config = (
        f"--oem 3 --psm {psm}"
    )

    try:

        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=config
        )

        return text or ""

    except pytesseract.TesseractNotFoundError:

        raise Exception(
            "Tesseract executable was not found."
        )

    except Exception as e:

        print(
            f"❌ OCR PSM {psm} failed:"
        )

        print(
            repr(e)
        )

        # IMPORTANT:
        # Do not silently hide OCR errors.
        raise


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_ocr_text(text):

    if not text:

        return ""

    # Normalize Windows/Linux line endings
    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]{3,}",
        " ",
        text
    )

    return text.strip()


# ============================================================
# OCR IMAGE
# ============================================================

def extract_text_from_image(
    file_path
):

    print(
        "========================================"
    )

    print(
        "IMAGE OCR STARTED"
    )

    print(
        "FILE:",
        file_path
    )

    print(
        "LANGUAGE:",
        OCR_LANG
    )

    print(
        "========================================"
    )

    try:

        image = Image.open(
            file_path
        )

        image.load()

        print(
            "IMAGE SIZE:",
            image.size
        )

        print(
            "IMAGE MODE:",
            image.mode
        )

        # ----------------------------------------------------
        # Upscale
        # ----------------------------------------------------

        upscaled = upscale_image(
            image.copy()
        )

        # ----------------------------------------------------
        # Variants
        # ----------------------------------------------------

        variants = [

            (
                "original",
                upscaled
            ),

            (
                "grayscale",
                preprocess_grayscale(
                    upscaled.copy()
                )
            ),

            (
                "threshold",
                preprocess_threshold(
                    upscaled.copy()
                )
            ),

        ]

        collected = []

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        for name, variant in variants:

            print(
                f"🔎 OCR variant: {name}"
            )

            for psm in [6, 11, 12]:

                text = run_ocr(
                    variant,
                    psm
                )

                if text.strip():

                    print(
                        f"✅ {name} / PSM {psm}: "
                        f"{len(text)} chars"
                    )

                    collected.append(
                        text
                    )

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        final_text = clean_ocr_text(
            "\n".join(collected)
        )

        print(
            "========================================"
        )

        print(
            "FINAL OCR CHARACTERS:",
            len(final_text)
        )

        print(
            "========================================"
        )

        if not final_text:

            raise Exception(
                "Tesseract completed but no readable "
                "text was detected."
            )

        if DEBUG_OCR:

            print(
                "OCR PREVIEW:"
            )

            print(
                final_text[:1000]
            )

        return final_text

    except Exception as e:

        print(
            "❌ IMAGE OCR ERROR:"
        )

        print(
            repr(e)
        )

        if DEBUG_OCR:

            traceback.print_exc()

        raise Exception(
            f"Image OCR failed: {str(e)}"
        )


# ============================================================
# OCR PDF
# ============================================================

def extract_text_from_pdf(
    file_path
):

    print(
        "========================================"
    )

    print(
        "PDF OCR STARTED"
    )

    print(
        "FILE:",
        file_path
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # Check Poppler
    # --------------------------------------------------------

    pdftoppm = shutil.which(
        "pdftoppm"
    )

    if not pdftoppm:

        raise Exception(
            "Poppler is not installed. "
            "Install poppler-utils on Render."
        )

    print(
        "✅ Poppler found:",
        pdftoppm
    )

    try:

        images = pdf2image.convert_from_path(
            file_path,
            dpi=300,
            fmt="jpeg"
        )

    except Exception as e:

        print(
            "❌ PDF conversion failed:"
        )

        print(
            repr(e)
        )

        raise Exception(
            f"PDF conversion failed: {str(e)}"
        )

    print(
        "PDF PAGES:",
        len(images)
    )

    all_text = []

    # --------------------------------------------------------
    # Each page
    # --------------------------------------------------------

    for page_number, image in enumerate(
        images,
        start=1
    ):

        print(
            "========================================"
        )

        print(
            f"PROCESSING PDF PAGE {page_number}"
        )

        print(
            "========================================"
        )

        upscaled = upscale_image(
            image.copy()
        )

        variants = [

            (
                "original",
                upscaled
            ),

            (
                "grayscale",
                preprocess_grayscale(
                    upscaled.copy()
                )
            ),

            (
                "threshold",
                preprocess_threshold(
                    upscaled.copy()
                )
            ),

        ]

        for name, variant in variants:

            for psm in [6, 11, 12]:

                text = run_ocr(
                    variant,
                    psm
                )

                if text.strip():

                    print(
                        f"✅ Page {page_number} "
                        f"{name} PSM {psm}: "
                        f"{len(text)} chars"
                    )

                    all_text.append(
                        text
                    )

    final_text = clean_ocr_text(
        "\n".join(all_text)
    )

    print(
        "========================================"
    )

    print(
        "FINAL PDF OCR CHARACTERS:",
        len(final_text)
    )

    print(
        "========================================"
    )

    if not final_text:

        raise Exception(
            "PDF was converted successfully, "
            "but no readable text was detected."
        )

    if DEBUG_OCR:

        print(
            "OCR PREVIEW:"
        )

        print(
            final_text[:1000]
        )

    return final_text


# ============================================================
# MAIN FILE OCR
# ============================================================

def extract_text_from_file(
    file_path
):

    if not os.path.exists(
        file_path
    ):

        raise Exception(
            f"File does not exist: {file_path}"
        )

    if not check_tesseract():

        raise Exception(
            "Tesseract OCR is not available."
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    print(
        "========================================"
    )

    print(
        "DOCUMENT OCR"
    )

    print(
        "FILE:",
        file_path
    )

    print(
        "EXTENSION:",
        extension
    )

    print(
        "========================================"
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

    raise Exception(
        "Unsupported document format. "
        "Use PDF, JPG, JPEG or PNG."
    )


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    if not text:

        return ""

    patterns = [

        r"\bName\s*[:\-]\s*"
        r"([A-Za-z][A-Za-z\s\.]{2,80})",

        r"\bName\s+"
        r"([A-Za-z][A-Za-z\s\.]{2,80})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(
                1
            ).strip()

            # Stop common OCR labels
            value = re.split(
                r"\b(?:DOB|Date|Address|Year)\b",
                value,
                flags=re.IGNORECASE
            )[0].strip()

            return value

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    ignored = {

        "government of india",

        "government india",

        "unique identification authority",

        "unique identification authority of india",

        "date of birth",

        "aadhaar card",

        "aadhar card",

        "identity card",

    }

    for line in text.splitlines():

        line = line.strip()

        if not line:

            continue

        cleaned = re.sub(
            r"[^A-Za-z\s\.]",
            "",
            line
        ).strip()

        words = cleaned.split()

        if not (
            2 <= len(words) <= 4
        ):

            continue

        if not all(
            re.match(
                r"^[A-Za-z][A-Za-z\.]*$",
                word
            )
            for word in words
        ):

            continue

        if cleaned.lower() in ignored:

            continue

        return cleaned

    return ""


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(text):

    if not text:

        return ""

    keywords = [

        "address",

        "road",

        "street",

        "nagar",

        "nagari",

        "apartment",

        "society",

        "flat",

        "floor",

        "ahmedabad",

        "gujarat",

        "sola",

        "naranpura",

        "kalupur",

        "chandkheda",

        "bodakdev",

        "vastrapur",

        "pincode",

        "pin code",

    ]

    for line in text.splitlines():

        line = line.strip()

        if not line:

            continue

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in keywords
        ):

            return line

    # Fallback
    for line in text.splitlines():

        line = line.strip()

        if (
            len(line) > 15
            and re.search(
                r"\d{3,6}",
                line
            )
        ):

            return line

    return ""


# ============================================================
# PHONE
# ============================================================

def extract_phone(text):

    if not text:

        return ""

    match = re.search(
        r"(?:\+91[\s\-]?)?"
        r"([6-9]\d{9})",
        text
    )

    if match:

        return match.group(1)

    return ""


# ============================================================
# FIRM NAME
# ============================================================

def extract_firm_name(text):

    if not text:

        return ""

    patterns = [

        r"\bFirm\s*Name\s*[:\-]\s*"
        r"([A-Za-z0-9\s\.\-&]+)",

        r"\bCompany\s*Name\s*[:\-]\s*"
        r"([A-Za-z0-9\s\.\-&]+)",

        r"\bOrganization\s*Name\s*[:\-]\s*"
        r"([A-Za-z0-9\s\.\-&]+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(
                1
            ).strip()

    return ""


# ============================================================
# REGISTRATION NUMBER
# ============================================================

def extract_registration_number(text):

    if not text:

        return ""

    patterns = [

        r"Registration\s*"
        r"(?:No|Number)?\s*[:\-]\s*"
        r"([A-Za-z0-9\-\/]+)",

        r"Reg\.?\s*"
        r"(?:No|Number)?\s*[:\-]\s*"
        r"([A-Za-z0-9\-\/]+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(
                1
            ).strip()

    tokens = re.findall(
        r"\b[A-Za-z0-9\-\/]{6,}\b",
        text
    )

    return tokens[0] if tokens else ""


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value):

    if value is None:

        return ""

    value = str(
        value
    ).lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = re.sub(
        r"[^a-z0-9\s]",
        "",
        value
    )

    return value.strip()


# ============================================================
# NORMALIZE DOCUMENT TYPE
# ============================================================

def normalize_document_type(
    doc_type
):

    if not doc_type:

        return ""

    value = str(
        doc_type
    ).strip().lower()

    aliases = {

        "aadhar":
            "aadhaar",

        "adhar":
            "aadhaar",

        "aadhaar card":
            "aadhaar",

        "aadhar card":
            "aadhaar",

        "aadhaarcard":
            "aadhaar",

        "pan card":
            "pan",

        "passport copy":
            "passport",

        "firm":
            "firm_registration",

        "firm registration":
            "firm_registration",

        "registration":
            "firm_registration",

        "registration certificate":
            "firm_registration",

        "id proof":
            "id_proof",

        "id":
            "id_proof",

    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# COMPACT OCR
# ============================================================

def compact_ocr_text(text):

    if not text:

        return ""

    return re.sub(
        r"[^a-z0-9\u0900-\u097F\u0A80-\u0AFF]",
        "",
        str(text).lower()
    )


# ============================================================
# AADHAAR KEYWORD
# ============================================================

def detect_aadhaar_keyword(text):

    if not text:

        return False

    lower = text.lower()

    compact = compact_ocr_text(
        text
    )

    keywords = [

        "aadhaar",

        "aadhar",

        "adhar",

        "adhaar",

        "aadher",

        "aaadhar",

        "aadhaer",

        "aadharr",

        "uidai",

        "uniqueidentificationauthorityofindia",

        "uniqueidentificationauthority",

        "uniqueidentification",

        "आधार",

        "आधारकार्ड",

        "આધાર",

        "આધારકાર્ડ",

    ]

    # Exact / compact
    for keyword in keywords:

        if keyword in compact:

            print(
                "✅ Aadhaar keyword detected:",
                keyword
            )

            return True

    # Fuzzy English words
    variations = [

        "aadhaar",

        "aadhar",

        "adhar",

        "adhaar",

        "aadher",

        "aaadhar",

        "aadhaer",

        "aadharr",

    ]

    words = re.findall(
        r"[A-Za-z]{4,}",
        lower
    )

    for word in words:

        for target in variations:

            score = fuzz.ratio(
                word,
                target
            )

            if score >= 78:

                print(
                    "✅ Aadhaar fuzzy:",
                    word,
                    "->",
                    target,
                    score
                )

                return True

    return False


# ============================================================
# AADHAAR NUMBER
# ============================================================

def detect_aadhaar_number(text):

    if not text:

        return False

    # 123456789012
    if re.search(
        r"(?<!\d)\d{12}(?!\d)",
        text
    ):

        print(
            "✅ 12-digit Aadhaar-like number found."
        )

        return True

    # 1234 5678 9012
    if re.search(
        r"(?<!\d)"
        r"\d{4}"
        r"[\s\-]+"
        r"\d{4}"
        r"[\s\-]+"
        r"\d{4}"
        r"(?!\d)",
        text
    ):

        print(
            "✅ Spaced Aadhaar-like number found."
        )

        return True

    return False


# ============================================================
# AADHAAR DOCUMENT
# ============================================================

def detect_aadhaar_document(text):

    if not text:

        return False

    lower = text.lower()

    keyword_found = (
        detect_aadhaar_keyword(text)
    )

    number_found = (
        detect_aadhaar_number(text)
    )

    uidai_found = (
        "uidai" in lower
        or "unique identification" in lower
    )

    govt_found = (
        "government of india" in lower
        or "govt of india" in lower
        or "भारत सरकार" in text
    )

    aadhaar_phrase = any(
        phrase in lower
        for phrase in [

            "aadhaar number",

            "aadhar number",

            "your aadhaar",

            "your aadhar",

            "aadhaar card",

            "aadhar card",

            "aadhaar letter",

            "aadhaar services",

        ]
    )

    print(
        "========================================"
    )

    print(
        "AADHAAR DETECTION"
    )

    print(
        "keyword:",
        keyword_found
    )

    print(
        "number:",
        number_found
    )

    print(
        "uidai:",
        uidai_found
    )

    print(
        "government:",
        govt_found
    )

    print(
        "phrase:",
        aadhaar_phrase
    )

    print(
        "========================================"
    )

    # Strong signals
    if keyword_found:

        return True

    if number_found and uidai_found:

        return True

    if aadhaar_phrase:

        return True

    # Multiple weak signals
    weak_signals = sum(
        [
            number_found,
            uidai_found,
            govt_found,
            aadhaar_phrase,
        ]
    )

    return weak_signals >= 2


# ============================================================
# DOCUMENT KEYWORD
# ============================================================

def contains_id_keyword(
    text_lower
):

    if not text_lower:

        return False

    if detect_aadhaar_keyword(
        text_lower
    ):

        return True

    return any(
        keyword in text_lower
        for keyword in [
            "pan",
            "passport",
        ]
    )


# ============================================================
# DOCUMENT TYPE VALIDATION
# ============================================================

def validate_document_type(
    text,
    expected_type
):

    document_type = (
        normalize_document_type(
            expected_type
        )
    )

    if document_type in (
        "aadhaar",
        "id_proof",
    ):

        return detect_aadhaar_document(
            text
        )

    if document_type == "pan":

        lower = text.lower()

        return (
            "income tax" in lower
            or
            "permanent account number"
            in lower
            or
            bool(
                re.search(
                    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
                    text.upper()
                )
            )
        )

    if document_type == "passport":

        lower = text.lower()

        return any(
            x in lower
            for x in [
                "passport",
                "republic of india",
                "nationality",
                "place of birth",
            ]
        )

    if document_type == "firm_registration":

        lower = text.lower()

        return any(
            x in lower
            for x in [
                "registrar of firms",
                "registration",
                "registered",
                "firm",
                "certificate",
                "llp",
            ]
        )

    if document_type == "bar_council":

        lower = text.lower()

        return (
            "bar council" in lower
            or
            (
                "advocate" in lower
                and
                bool(
                    re.search(
                        r"\b\d{4,6}\b",
                        text
                    )
                )
            )
        )

    return False