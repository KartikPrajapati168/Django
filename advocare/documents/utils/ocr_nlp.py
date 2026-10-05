# ============================================================
# document_verifier.py
# ============================================================
import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
from fuzzywuzzy import fuzz

# Optional (text-based PDFs)
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


# ============================================================
# CONFIGURATION
# ============================================================

# 🔴 Uncomment & set for Windows (or set via env var TESSERACT_CMD)
pytesseract.pytesseract.tesseract_cmd = (
    os.getenv("TESSERACT_CMD")
    or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Use 'guj+eng' only if Gujarati trained data is installed.
OCR_LANG = os.getenv("OCR_LANG", "eng")


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """Grayscale + contrast + light sharpen for better OCR."""
    gray = image.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(2.0)
    gray = gray.filter(ImageFilter.SHARPEN)
    return gray


def preprocess_threshold(image):
    """High-contrast black/white version."""
    gray = preprocess_image(image)
    return gray.point(lambda p: 255 if p > 140 else 0)


# ============================================================
# OCR HELPERS
# ============================================================

def run_ocr(image, psm=6):
    try:
        return pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=f"--oem 3 --psm {psm}",
        ) or ""
    except Exception as e:
        print(f"⚠️ OCR failed (psm={psm}): {e}")
        return ""


def extract_text_from_image(file_path):
    """Multi-pass OCR on JPG / JPEG / PNG."""
    image = Image.open(file_path)
    variants = [
        image,
        preprocess_image(image.copy()),
        preprocess_threshold(image.copy()),
    ]

    chunks = []
    for variant in variants:
        for psm in (6, 11, 12):
            text = run_ocr(variant, psm=psm)
            if text.strip():
                chunks.append(text)

    return "\n".join(chunks).strip()


def extract_text_from_pdf(file_path):
    """Try PyPDF2 first, fallback to OCR via pdf2image."""
    full_text = ""

    # 1. Text-based PDF
    if PYPDF2_AVAILABLE:
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n"
        except Exception as e:
            print(f"⚠️ PyPDF2 failed: {e}")

    # 2. Scanned PDF → OCR
    if not full_text.strip():
        try:
            images = pdf2image.convert_from_path(file_path, dpi=300)
            chunks = []
            for img in images:
                for variant in (
                    img,
                    preprocess_image(img.copy()),
                    preprocess_threshold(img.copy()),
                ):
                    for psm in (6, 11, 12):
                        t = run_ocr(variant, psm=psm)
                        if t.strip():
                            chunks.append(t)
            full_text = "\n".join(chunks)
        except Exception as e:
            print(f"⚠️ pdf2image OCR failed: {e}")

    return full_text.strip()


def extract_text_from_file(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".jpg", ".jpeg", ".png"):
        return extract_text_from_image(file_path)
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    raise Exception("Unsupported format. Use PDF / JPG / JPEG / PNG.")


# ============================================================
# FIELD EXTRACTION HELPERS
# ============================================================

def extract_name(text):
    if not text:
        return ""
    patterns = [
        r"\bName\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,80})",
        r"\bName\s+([A-Za-z][A-Za-z\s\.]{2,80})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    ignored = {
        "government of india",
        "unique identification authority",
        "date of birth",
        "aadhaar card",
        "aadhar card",
    }
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r"[^A-Za-z\s\.]", "", line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and all(
            re.match(r"^[A-Za-z][A-Za-z\.]*$", w) for w in words
        ):
            if cleaned.lower() not in ignored:
                return cleaned
    return ""


def extract_address(text):
    if not text:
        return ""
    keywords = [
        "address", "road", "street", "nagar", "nagari", "apartment",
        "society", "flat", "floor", "ahmedabad", "gujarat", "sola",
        "naranpura", "kalupur", "chandkheda", "bodakdev",
        "vastrapur", "pincode", "pin code",
    ]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(k in lower for k in keywords):
            return line

    # fallback: line with digits + length > 15
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 15 and re.search(r"\d{3,6}", line):
            return line
    return ""


def extract_phone(text):
    if not text:
        return ""
    m = re.search(r"(?:\+91[\s\-]?)?([6-9]\d{9})", text)
    return m.group(1) if m else ""


def extract_firm_name(text):
    if not text:
        return ""
    for p in [
        r"\bFirm\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)",
        r"\bCompany\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)",
        r"\bOrganization\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def extract_registration_number(text):
    if not text:
        return ""
    for p in [
        r"Registration\s*(?:No|Number)?\s*[:\-]\s*([A-Za-z0-9\-\/]+)",
        r"Reg\.?\s*(?:No|Number)?\s*[:\-]\s*([A-Za-z0-9\-\/]+)",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    tokens = re.findall(r"\b[A-Za-z0-9\-\/]{6,}\b", text)
    return tokens[0] if tokens else ""


# ============================================================
# AADHAAR DETECTION (ROBUST)
# ============================================================

def detect_aadhaar_keyword(text):
    """
    Detect 'Aadhaar' with OCR-friendly fuzzy matching.
    Handles:
      aadhaar, aadhar, adhar, adhaar, aadher, aaadhar,
      aadhaer, aadharr, uidai, unique identification authority
    """
    if not text:
        return False

    lower = text.lower()

    # 1. Direct substring checks
    direct = [
        "aadhaar", "aadhar", "adhar", "adhaar", "aadher",
        "aaadhar", "aadhaer", "uidai",
        "unique identification authority of india",
        "unique identification authority",
    ]
    for kw in direct:
        if kw in lower:
            print(f"✅ Aadhaar keyword: '{kw}'")
            return True

    # 2. Compact (spaces/punct removed)
    compact = re.sub(r"[^a-z0-9]", "", lower)
    for kw in [
        "aadhaar", "aadhar", "adhar", "adhaar", "aadher",
        "aaadhar", "uidai", "uniqueidentificationauthority",
    ]:
        if kw in compact:
            print(f"✅ Aadhaar compact keyword: '{kw}'")
            return True

    # 3. Fuzzy word-level matching (OCR mistakes)
    variations = [
        "aadhaar", "aadhar", "adhar", "adhaar",
        "aadher", "aaadhar", "aadhaer", "aadharr",
    ]
    for word in re.findall(r"[A-Za-z]{4,}", lower):
        for target in variations:
            score = fuzz.ratio(word, target)
            if score >= 78:
                print(f"✅ Aadhaar fuzzy: {word} → {target} ({score})")
                return True

    return False


def detect_aadhaar_number(text):
    """12-digit Aadhaar-like number (plain or spaced)."""
    if not text:
        return False
    if re.search(r"(?<!\d)\d{12}(?!\d)", text):
        return True
    if re.search(
        r"(?<!\d)\d{4}[\s\-]+\d{4}[\s\-]+\d{4}(?!\d)", text
    ):
        return True
    return False


def detect_aadhaar_document(text):
    """
    Multi-signal Aadhaar detection.
    Returns True if any strong signal OR ≥2 weak signals.
    """
    if not text:
        return False

    lower = text.lower()

    keyword_found = detect_aadhaar_keyword(text)
    number_found = detect_aadhaar_number(text)

    uidai_found = (
        "uidai" in lower
        or "unique identification authority" in lower
    )
    govt_india_found = (
        "government of india" in lower
        or "govt of india" in lower
        or "भारत सरकार" in text
    )
    aadhaar_phrase_found = any(p in lower for p in [
        "aadhaar is proof",
        "aadhar is proof",
        "aadhaar number",
        "aadhar number",
        "your aadhaar",
        "your aadhar",
        "aadhaar card",
        "aadhar card",
        "aadhaar letter",
        "aadhaar services",
        "आधार",
        "આધાર",
    ])

    print(
        f"   Aadhaar signals → "
        f"keyword={keyword_found}, number={number_found}, "
        f"uidai={uidai_found}, govt={govt_india_found}, "
        f"phrase={aadhaar_phrase_found}"
    )

    # Strong signals
    if keyword_found:
        return True
    if uidai_found and number_found:
        return True
    if aadhaar_phrase_found:
        return True

    # Weak signals: need ≥ 2
    weak = sum([
        number_found,
        uidai_found,
        govt_india_found,
        aadhaar_phrase_found,
    ])
    return weak >= 2


# ============================================================
# FUZZY / PHONE MATCHING
# ============================================================

def normalize_text(value):
    if value is None:
        return ""
    value = str(value).lower()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", "", value)
    return value.strip()


def fuzzy_match(expected, actual, threshold=70):
    e = normalize_text(expected)
    a = normalize_text(actual)
    if not e or not a:
        return False, 0
    score = fuzz.token_set_ratio(e, a)
    return score >= threshold, score


def phone_match(expected, actual):
    e = re.sub(r"\D", "", str(expected or ""))
    a = re.sub(r"\D", "", str(actual or ""))
    if e.startswith("91") and len(e) > 10:
        e = e[-10:]
    if a.startswith("91") and len(a) > 10:
        a = a[-10:]
    return bool(e) and bool(a) and e == a


# ============================================================
# DOCUMENT TYPE NORMALIZER
# ============================================================

def normalize_document_type(doc_type):
    if not doc_type:
        return ""
    value = str(doc_type).strip().lower()
    aliases = {
        "aadhar": "aadhaar",
        "adhar": "aadhaar",
        "aadhaar card": "aadhaar",
        "aadhar card": "aadhaar",
        "aadhaarcard": "aadhaar",
        "pan card": "pan",
        "passport copy": "passport",
        "firm": "firm_registration",
        "firm registration": "firm_registration",
        "registration": "firm_registration",
        "registration certificate": "firm_registration",
        "id proof": "id_proof",
    }
    return aliases.get(value, value)


# ============================================================
# MAIN VERIFICATION FUNCTION
# ============================================================

def verify_document(file_path, expected_type, **kwargs):
    """
    kwargs supported:
        expected_name, expected_address, expected_phone,
        expected_firm_name, expected_registration_no
    Returns:
        {"valid": bool, "message": str, "extracted": {...}}
    """
    try:
        text = extract_text_from_file(file_path)
    except Exception as e:
        return {"valid": False, "message": str(e), "extracted": {}}

    if not text:
        return {
            "valid": False,
            "message": "Could not read document. Upload a clear image/PDF.",
            "extracted": {},
        }

    print(f"\n=== OCR Preview ({expected_type}) ===\n{text[:600]}\n=== END ===\n")

    lower = text.lower()
    doc_type = normalize_document_type(expected_type)

    # --------------------------------------------------------
    # BAR COUNCIL
    # --------------------------------------------------------
    if doc_type == "bar_council":
        if not re.search(r"bar\s*council", lower):
            if not ("advocate" in lower and re.search(r"\b\d{4,6}\b", text)):
                return {
                    "valid": False,
                    "message": "Document does not appear to be a Bar Council certificate.",
                    "extracted": {},
                }

        expected_name = kwargs.get("expected_name", "")
        expected_address = kwargs.get("expected_address", "")
        expected_phone = kwargs.get("expected_phone", "")

        extracted_name = extract_name(text)
        extracted_address = extract_address(text)
        extracted_phone = extract_phone(text)

        errors = []
        if expected_name:
            if not extracted_name or fuzz.partial_ratio(
                expected_name.lower(), extracted_name.lower()
            ) < 70:
                errors.append(
                    f"Name mismatch: expected '{expected_name}', "
                    f"found '{extracted_name or 'nothing'}'"
                )
        if expected_address:
            if not extracted_address or fuzz.partial_ratio(
                expected_address.lower(), extracted_address.lower()
            ) < 60:
                errors.append(
                    f"Address mismatch: expected '{expected_address}', "
                    f"found '{extracted_address or 'nothing'}'"
                )
        if expected_phone:
            if not extracted_phone:
                errors.append("Could not extract phone number.")
            else:
                e = re.sub(r"\D", "", expected_phone)[-10:]
                a = re.sub(r"\D", "", extracted_phone)[-10:]
                if e != a:
                    errors.append(
                        f"Phone mismatch: expected '{expected_phone}', "
                        f"found '{extracted_phone}'"
                    )

        if errors:
            return {"valid": False, "message": "; ".join(errors), "extracted": {}}

        return {
            "valid": True,
            "message": "Bar Council certificate verified successfully.",
            "extracted": {
                "name": extracted_name,
                "address": extracted_address,
                "phone": extracted_phone,
            },
        }

    # --------------------------------------------------------
    # FIRM REGISTRATION
    # --------------------------------------------------------
    if doc_type == "firm_registration":
        if not re.search(r"registrar\s+of\s+firms", lower):
            if not ("firm name" in lower and "registration number" in lower):
                return {
                    "valid": False,
                    "message": "Not a firm registration certificate "
                               "(missing 'Registrar of Firms').",
                    "extracted": {},
                }

        expected_firm = kwargs.get("expected_firm_name", "")
        expected_reg = kwargs.get("expected_registration_no", "")

        extracted_firm = extract_firm_name(text)
        extracted_reg = extract_registration_number(text)

        errors = []
        if expected_firm:
            if not extracted_firm or fuzz.partial_ratio(
                expected_firm.lower(), extracted_firm.lower()
            ) < 70:
                errors.append(
                    f"Firm name mismatch: expected '{expected_firm}', "
                    f"found '{extracted_firm or 'nothing'}'"
                )
        if expected_reg:
            if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
                errors.append(
                    f"Registration number mismatch: expected '{expected_reg}', "
                    f"found '{extracted_reg or 'nothing'}'"
                )

        if errors:
            return {"valid": False, "message": "; ".join(errors), "extracted": {}}

        return {
            "valid": True,
            "message": "Firm registration verified successfully.",
            "extracted": {
                "firm_name": extracted_firm,
                "registration_number": extracted_reg,
            },
        }

    # --------------------------------------------------------
    # ID PROOF / AADHAAR
    # --------------------------------------------------------
    if doc_type in ("id_proof", "aadhaar"):
        if not detect_aadhaar_document(text):
            return {
                "valid": False,
                "message": "Document does not appear to be a valid "
                           "Aadhaar / ID proof.",
                "extracted": {},
            }

        expected_name = kwargs.get("expected_name", "")
        extracted_name = extract_name(text)

        if expected_name:
            if not extracted_name or fuzz.partial_ratio(
                expected_name.lower(), extracted_name.lower()
            ) < 70:
                return {
                    "valid": False,
                    "message": f"Name mismatch: expected '{expected_name}', "
                               f"found '{extracted_name or 'nothing'}'",
                    "extracted": {"name": extracted_name},
                }

        return {
            "valid": True,
            "message": "Aadhaar / ID proof verified successfully.",
            "extracted": {"name": extracted_name},
        }

    # --------------------------------------------------------
    # FIR
    # --------------------------------------------------------
    if doc_type == "fir":
        if "fir" not in lower and "first information report" not in lower:
            return {
                "valid": False,
                "message": "Document does not appear to be an FIR.",
                "extracted": {},
            }
        return {
            "valid": True,
            "message": "FIR verified successfully.",
            "extracted": {},
        }

    # --------------------------------------------------------
    # LEGAL NOTICE
    # --------------------------------------------------------
    if doc_type == "notice":
        if "notice" not in lower:
            return {
                "valid": False,
                "message": "Document does not appear to be a legal notice.",
                "extracted": {},
            }
        return {
            "valid": True,
            "message": "Legal notice verified successfully.",
            "extracted": {},
        }

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------
    return {
        "valid": False,
        "message": f"Unsupported document type: {expected_type}",
        "extracted": {},
    }