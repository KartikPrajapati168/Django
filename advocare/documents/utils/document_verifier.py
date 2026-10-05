import re

from fuzzywuzzy import fuzz

from .ocr_nlp import (
    extract_text_from_file,
    extract_name,
    extract_address,
    extract_phone,
    extract_firm_name,
    extract_registration_number,
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Normalize text for comparison.
    """

    if not value:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# FUZZY MATCH
# ============================================================

def fuzzy_match(
    expected,
    actual,
    threshold=70
):
    """
    Compare expected and OCR extracted values.
    """

    if not expected or not actual:
        return False

    expected_normalized = normalize_text(
        expected
    )

    actual_normalized = normalize_text(
        actual
    )

    if not expected_normalized or not actual_normalized:
        return False

    if expected_normalized in actual_normalized:
        return True

    score = fuzz.token_set_ratio(
        expected_normalized,
        actual_normalized
    )

    return score >= threshold


# ============================================================
# PHONE MATCH
# ============================================================

def normalize_phone(phone):
    if not phone:
        return ""

    digits = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if digits.startswith("91") and len(digits) == 12:
        digits = digits[-10:]

    return digits


def phone_match(expected, actual):
    expected = normalize_phone(expected)
    actual = normalize_phone(actual)

    if not expected or not actual:
        return False

    return expected == actual


# ============================================================
# AADHAAR DETECTION
# ============================================================

def detect_aadhaar_keyword(text):
    """
    Detect Aadhaar-related words.

    OCR can produce:
        Aadhaar
        Aadhar
        Aadhaar Card
        Unique Identification
        UIDAI
    """

    normalized = normalize_text(text)

    keywords = [
        "aadhaar",
        "aadhar",
        "uidai",
        "unique identification",
        "unique identification authority",
    ]

    for keyword in keywords:

        if normalize_text(keyword) in normalized:
            return True

    # Fuzzy keyword detection
    words = normalized.split()

    for word in words:

        if fuzz.ratio(
            word,
            "aadhaar"
        ) >= 75:

            return True

        if fuzz.ratio(
            word,
            "aadhar"
        ) >= 75:

            return True

    return False


def detect_aadhaar_number(text):
    """
    Detect 12-digit Aadhaar number.

    Supports spaces:
        1234 5678 9012

    and continuous:
        123456789012
    """

    if not text:
        return False

    # Remove obvious non-digit separators
    matches = re.findall(
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        text
    )

    return bool(matches)


def detect_aadhaar_document(text):
    """
    Aadhaar document is considered detected when either:
        - Aadhaar keyword exists
        - 12 digit Aadhaar-like number exists
    """

    return (
        detect_aadhaar_keyword(text)
        or detect_aadhaar_number(text)
    )


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

def normalize_document_type(document_type):
    if not document_type:
        return ""

    value = normalize_text(
        document_type
    )

    aliases = {

        "aadhaar": "aadhaar",
        "aadhar": "aadhaar",
        "aadhaar card": "aadhaar",

        "id proof": "aadhaar",
        "identity proof": "aadhaar",

        "bar council": "bar_council",
        "bar council certificate": "bar_council",
        "bar council id": "bar_council",

        "firm registration": "firm_registration",
        "firm registration certificate": "firm_registration",
        "registration certificate": "firm_registration",

        "fir": "fir",
        "first information report": "fir",

        "notice": "notice",
        "legal notice": "notice",
    }

    return aliases.get(
        value,
        value.replace(" ", "_")
    )


# ============================================================
# BAR COUNCIL DETECTION
# ============================================================

def detect_bar_council(text):
    normalized = normalize_text(text)

    keywords = [
        "bar council",
        "bar counsil",
        "bar council of india",
        "state bar council",
        "advocate",
    ]

    for keyword in keywords:

        if normalize_text(keyword) in normalized:
            return True

    return False


# ============================================================
# FIRM REGISTRATION DETECTION
# ============================================================

def detect_firm_registration(text):
    normalized = normalize_text(text)

    keywords = [
        "firm registration",
        "registration certificate",
        "registered firm",
        "registration number",
        "registration no",
        "firm",
    ]

    for keyword in keywords:

        if normalize_text(keyword) in normalized:
            return True

    return False


# ============================================================
# FIR DETECTION
# ============================================================

def detect_fir(text):
    normalized = normalize_text(text)

    keywords = [
        "first information report",
        "fir",
        "police station",
        "fir number",
        "fir no",
    ]

    for keyword in keywords:

        if normalize_text(keyword) in normalized:
            return True

    return False


# ============================================================
# NOTICE DETECTION
# ============================================================

def detect_notice(text):
    normalized = normalize_text(text)

    keywords = [
        "legal notice",
        "notice",
        "hereby notice",
        "advocate notice",
    ]

    for keyword in keywords:

        if normalize_text(keyword) in normalized:
            return True

    return False


# ============================================================
# GENERIC DOCUMENT DETECTION
# ============================================================

def detect_document_type(
    text,
    expected_type
):
    expected_type = normalize_document_type(
        expected_type
    )

    if expected_type == "aadhaar":
        return detect_aadhaar_document(text)

    if expected_type == "bar_council":
        return detect_bar_council(text)

    if expected_type == "firm_registration":
        return detect_firm_registration(text)

    if expected_type == "fir":
        return detect_fir(text)

    if expected_type == "notice":
        return detect_notice(text)

    # If unknown document type,
    # don't automatically reject solely because
    # there is no detector.
    return True


# ============================================================
# VERIFY DOCUMENT
# ============================================================

def verify_document(
    file_path,
    expected_type,
    **kwargs
):
    """
    Main document verification function.
    """

    expected_type = normalize_document_type(
        expected_type
    )

    # --------------------------------------------------------
    # Validate document type
    # --------------------------------------------------------

    if not expected_type:

        return {
            "valid": False,
            "message": "Document type is required.",
            "extracted": {},
        }

    # --------------------------------------------------------
    # OCR / Text extraction
    # --------------------------------------------------------

    try:

        text = extract_text_from_file(
            file_path
        )

    except Exception as e:

        print(
            f"DOCUMENT OCR ERROR: {repr(e)}"
        )

        return {
            "valid": False,
            "message": str(e),
            "extracted": {},
        }

    # --------------------------------------------------------
    # No text
    # --------------------------------------------------------

    if not text or not text.strip():

        return {
            "valid": False,
            "message": (
                "Could not read document. "
                "Upload a clear image/PDF."
            ),
            "extracted": {},
        }

    # --------------------------------------------------------
    # Clean OCR text
    # --------------------------------------------------------

    text = text.strip()

    print(
        "========== OCR TEXT START =========="
    )

    print(
        text[:5000]
    )

    print(
        "=========== OCR TEXT END ==========="
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
        extract_registration_number(text)
    )

    extracted = {
        "name": extracted_name,
        "address": extracted_address,
        "phone": extracted_phone,
        "firm_name": extracted_firm_name,
        "registration_number": (
            extracted_registration_number
        ),
    }

    # --------------------------------------------------------
    # Document type detection
    # --------------------------------------------------------

    document_detected = detect_document_type(
        text,
        expected_type
    )

    if not document_detected:

        return {
            "valid": False,
            "message": (
                "Uploaded document does not appear "
                "to be the selected document type."
            ),
            "extracted": extracted,
        }

    # --------------------------------------------------------
    # Expected values
    # --------------------------------------------------------

    expected_name = kwargs.get(
        "expected_name"
    )

    expected_address = kwargs.get(
        "expected_address"
    )

    expected_phone = kwargs.get(
        "expected_phone"
    )

    expected_firm_name = kwargs.get(
        "expected_firm_name"
    )

    expected_registration_no = kwargs.get(
        "expected_registration_no"
    )

    # --------------------------------------------------------
    # Validation results
    # --------------------------------------------------------

    checks = {}

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if expected_name:

        checks["name"] = fuzzy_match(
            expected_name,
            extracted_name,
            threshold=70
        )

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    if expected_address:

        checks["address"] = fuzzy_match(
            expected_address,
            extracted_address,
            threshold=60
        )

    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if expected_phone:

        checks["phone"] = phone_match(
            expected_phone,
            extracted_phone
        )

    # --------------------------------------------------------
    # FIRM NAME
    # --------------------------------------------------------

    if expected_firm_name:

        checks["firm_name"] = fuzzy_match(
            expected_firm_name,
            extracted_firm_name,
            threshold=65
        )

    # --------------------------------------------------------
    # REGISTRATION NUMBER
    # --------------------------------------------------------

    if expected_registration_no:

        expected_reg = normalize_text(
            expected_registration_no
        )

        actual_reg = normalize_text(
            extracted_registration_number
        )

        checks["registration_number"] = (
            bool(expected_reg)
            and bool(actual_reg)
            and (
                expected_reg == actual_reg
                or expected_reg in actual_reg
                or actual_reg in expected_reg
            )
        )

    # --------------------------------------------------------
    # If no expected fields were supplied
    # --------------------------------------------------------

    if not checks:

        return {
            "valid": True,
            "message": (
                "Document read successfully."
            ),
            "extracted": extracted,
            "checks": {},
        }

    # --------------------------------------------------------
    # Overall result
    # --------------------------------------------------------

    valid = all(
        checks.values()
    )

    failed_checks = [
        key
        for key, value in checks.items()
        if not value
    ]

    if valid:

        message = (
            "Document verified successfully."
        )

    else:

        message = (
            "Document was read, but some details "
            "could not be verified."
        )

    return {
        "valid": valid,
        "message": message,
        "extracted": extracted,
        "checks": checks,
        "failed_checks": failed_checks,
    }