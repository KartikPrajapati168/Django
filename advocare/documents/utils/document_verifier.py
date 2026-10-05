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
# NORMALIZE
# ============================================================

def normalize_text(value):

    if not value:

        return ""

    value = str(
        value
    ).lower()

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

    if not expected or not actual:

        return False

    expected = normalize_text(
        expected
    )

    actual = normalize_text(
        actual
    )

    if not expected or not actual:

        return False

    if expected in actual:

        return True

    score = fuzz.token_set_ratio(
        expected,
        actual
    )

    return score >= threshold


# ============================================================
# PHONE
# ============================================================

def normalize_phone(phone):

    if not phone:

        return ""

    digits = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if (
        digits.startswith("91")
        and
        len(digits) == 12
    ):

        digits = digits[-10:]

    return digits


def phone_match(
    expected,
    actual
):

    expected = normalize_phone(
        expected
    )

    actual = normalize_phone(
        actual
    )

    return (
        bool(expected)
        and
        bool(actual)
        and
        expected == actual
    )


# ============================================================
# AADHAAR
# ============================================================

def detect_aadhaar_keyword(
    text
):

    normalized = normalize_text(
        text
    )

    keywords = [
        "aadhaar",
        "aadhar",
        "uidai",
        "unique identification",
    ]

    for keyword in keywords:

        if normalize_text(
            keyword
        ) in normalized:

            return True

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


def detect_aadhaar_number(
    text
):

    if not text:

        return False

    matches = re.findall(
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        text
    )

    return bool(
        matches
    )


def detect_aadhaar_document(
    text
):

    return (
        detect_aadhaar_keyword(text)
        or
        detect_aadhaar_number(text)
    )


# ============================================================
# DOCUMENT TYPE
# ============================================================

def normalize_document_type(
    document_type
):

    if not document_type:

        return ""

    value = normalize_text(
        document_type
    )

    aliases = {

        "aadhaar":
            "aadhaar",

        "aadhar":
            "aadhaar",

        "aadhaar card":
            "aadhaar",

        "id proof":
            "aadhaar",

        "identity proof":
            "aadhaar",

        "bar council":
            "bar_council",

        "bar council certificate":
            "bar_council",

        "bar council id":
            "bar_council",

        "firm registration":
            "firm_registration",

        "firm registration certificate":
            "firm_registration",

        "registration certificate":
            "firm_registration",

        "fir":
            "fir",

        "first information report":
            "fir",

        "notice":
            "notice",
    }

    return aliases.get(
        value,
        value.replace(
            " ",
            "_"
        )
    )


# ============================================================
# DOCUMENT DETECTION
# ============================================================

def detect_bar_council(
    text
):

    normalized = normalize_text(
        text
    )

    keywords = [
        "bar council",
        "bar counsil",
        "bar council of india",
        "state bar council",
        "advocate",
    ]

    return any(
        normalize_text(keyword)
        in normalized
        for keyword in keywords
    )


def detect_firm_registration(
    text
):

    normalized = normalize_text(
        text
    )

    keywords = [
        "firm registration",
        "registration certificate",
        "registered firm",
        "registration number",
        "registration no",
        "firm",
    ]

    return any(
        normalize_text(keyword)
        in normalized
        for keyword in keywords
    )


def detect_fir(
    text
):

    normalized = normalize_text(
        text
    )

    keywords = [
        "first information report",
        "fir",
        "police station",
        "fir number",
        "fir no",
    ]

    return any(
        normalize_text(keyword)
        in normalized
        for keyword in keywords
    )


def detect_notice(
    text
):

    normalized = normalize_text(
        text
    )

    keywords = [
        "legal notice",
        "notice",
        "hereby notice",
        "advocate notice",
    ]

    return any(
        normalize_text(keyword)
        in normalized
        for keyword in keywords
    )


def detect_document_type(
    text,
    expected_type
):

    expected_type = normalize_document_type(
        expected_type
    )

    if expected_type == "aadhaar":

        return detect_aadhaar_document(
            text
        )

    if expected_type == "bar_council":

        return detect_bar_council(
            text
        )

    if expected_type == "firm_registration":

        return detect_firm_registration(
            text
        )

    if expected_type == "fir":

        return detect_fir(
            text
        )

    if expected_type == "notice":

        return detect_notice(
            text
        )

    return True


# ============================================================
# MAIN VERIFICATION
# ============================================================

def verify_document(
    file_path,
    expected_type,
    **kwargs
):

    expected_type = normalize_document_type(
        expected_type
    )

    if not expected_type:

        return {
            "valid": False,
            "message":
                "Document type is required.",
            "extracted": {},
        }

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    try:

        text = extract_text_from_file(
            file_path
        )

    except Exception as e:

        print(
            "OCR/FILE EXTRACTION ERROR:",
            repr(e)
        )

        return {
            "valid": False,
            "message":
                str(e),
            "extracted": {},
        }

    # --------------------------------------------------------
    # Empty OCR
    # --------------------------------------------------------

    if not text or not text.strip():

        return {
            "valid": False,
            "message":
                "Could not read document. "
                "Upload a clear image/PDF.",
            "extracted": {},
        }

    text = text.strip()

    print(
        "OCR TEXT LENGTH:",
        len(text)
    )

    print(
        "OCR TEXT:"
    )

    print(
        text[:5000]
    )

    # --------------------------------------------------------
    # Extract fields
    # --------------------------------------------------------

    extracted = {

        "name":
            extract_name(text),

        "address":
            extract_address(text),

        "phone":
            extract_phone(text),

        "firm_name":
            extract_firm_name(text),

        "registration_number":
            extract_registration_number(text),
    }

    print(
        "EXTRACTED:",
        extracted
    )

    # --------------------------------------------------------
    # Detect document
    # --------------------------------------------------------

    if not detect_document_type(
        text,
        expected_type
    ):

        return {
            "valid": False,

            "message":
                "Uploaded document does not appear "
                "to be the selected document type.",

            "extracted":
                extracted,
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
    # Checks
    # --------------------------------------------------------

    checks = {}

    if expected_name:

        checks["name"] = fuzzy_match(
            expected_name,
            extracted["name"],
            70
        )

    if expected_address:

        checks["address"] = fuzzy_match(
            expected_address,
            extracted["address"],
            60
        )

    if expected_phone:

        checks["phone"] = phone_match(
            expected_phone,
            extracted["phone"]
        )

    if expected_firm_name:

        checks["firm_name"] = fuzzy_match(
            expected_firm_name,
            extracted["firm_name"],
            65
        )

    if expected_registration_no:

        expected_reg = normalize_text(
            expected_registration_no
        )

        actual_reg = normalize_text(
            extracted["registration_number"]
        )

        checks[
            "registration_number"
        ] = (
            bool(expected_reg)
            and
            bool(actual_reg)
            and
            (
                expected_reg == actual_reg
                or
                expected_reg in actual_reg
                or
                actual_reg in expected_reg
            )
        )

    # --------------------------------------------------------
    # No expected fields
    # --------------------------------------------------------

    if not checks:

        return {
            "valid": True,
            "message":
                "Document read successfully.",
            "extracted":
                extracted,
            "checks": {},
        }

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    valid = all(
        checks.values()
    )

    failed_checks = [
        key
        for key, value
        in checks.items()
        if not value
    ]

    return {
        "valid": valid,

        "message":
            (
                "Document verified successfully."
                if valid
                else
                "Document was read, but some details "
                "could not be verified."
            ),

        "extracted":
            extracted,

        "checks":
            checks,

        "failed_checks":
            failed_checks,
    }