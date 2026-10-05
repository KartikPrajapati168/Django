# ============================================================
# document_verifier.py
# ============================================================

import re

from fuzzywuzzy import fuzz

from .ocr_nlp import (
    extract_text_from_file,
    extract_name,
    extract_address,
    extract_phone,
    extract_firm_name,
    extract_registration_number,
    normalize_text,
    normalize_document_type,
    detect_aadhaar_document,
)


# ============================================================
# SAFE PREVIEW
# ============================================================

def safe_ocr_preview(text, limit=500):

    if not text:

        return ""

    preview = text[:limit]

    # Mask 12 digit numbers
    preview = re.sub(
        r"\d{4}[\s\-]?\d{4}[\s\-]?\d{4}",
        "[ID-NUMBER-MASKED]",
        preview
    )

    return preview


# ============================================================
# FUZZY MATCH
# ============================================================

def fuzzy_match(
    expected,
    actual,
    threshold=70
):

    expected = normalize_text(
        expected
    )

    actual = normalize_text(
        actual
    )

    if not expected or not actual:

        return False, 0

    score = fuzz.token_set_ratio(
        expected,
        actual
    )

    return (
        score >= threshold,
        score
    )


# ============================================================
# PHONE MATCH
# ============================================================

def phone_match(
    expected,
    actual
):

    expected_digits = re.sub(
        r"\D",
        "",
        str(expected or "")
    )

    actual_digits = re.sub(
        r"\D",
        "",
        str(actual or "")
    )

    if (
        len(expected_digits) > 10
        and expected_digits.startswith("91")
    ):

        expected_digits = (
            expected_digits[-10:]
        )

    if (
        len(actual_digits) > 10
        and actual_digits.startswith("91")
    ):

        actual_digits = (
            actual_digits[-10:]
        )

    if not expected_digits:

        return False

    if not actual_digits:

        return False

    return (
        expected_digits
        == actual_digits
    )


# ============================================================
# BAR COUNCIL
# ============================================================

def verify_bar_council(
    text,
    **kwargs
):

    lower = text.lower()

    if not (
        "bar council" in lower
        or
        (
            "advocate" in lower
            and
            re.search(
                r"\b\d{4,6}\b",
                text
            )
        )
    ):

        return {
            "valid": False,
            "message":
                "Document does not appear to be "
                "a Bar Council certificate.",
            "extracted": {},
        }

    extracted_name = extract_name(
        text
    )

    extracted_address = extract_address(
        text
    )

    extracted_phone = extract_phone(
        text
    )

    expected_name = kwargs.get(
        "expected_name"
    )

    expected_address = kwargs.get(
        "expected_address"
    )

    expected_phone = kwargs.get(
        "expected_phone"
    )

    errors = []

    if expected_name:

        valid, score = fuzzy_match(
            expected_name,
            extracted_name,
            threshold=65
        )

        if not valid:

            errors.append(
                f"Name mismatch. "
                f"Expected '{expected_name}', "
                f"found '{extracted_name or 'nothing'}' "
                f"(score {score})"
            )

    if expected_address:

        valid, score = fuzzy_match(
            expected_address,
            extracted_address,
            threshold=55
        )

        if not valid:

            errors.append(
                f"Address mismatch. "
                f"Expected '{expected_address}', "
                f"found '{extracted_address or 'nothing'}' "
                f"(score {score})"
            )

    if expected_phone:

        if not phone_match(
            expected_phone,
            extracted_phone
        ):

            errors.append(
                f"Phone mismatch. "
                f"Expected '{expected_phone}', "
                f"found '{extracted_phone or 'nothing'}'"
            )

    if errors:

        return {
            "valid": False,
            "message": "; ".join(errors),
            "extracted": {
                "name":
                    extracted_name,

                "address":
                    extracted_address,

                "phone":
                    extracted_phone,
            },
        }

    return {
        "valid": True,

        "message":
            "Bar Council certificate "
            "verified successfully.",

        "extracted": {

            "name":
                extracted_name,

            "address":
                extracted_address,

            "phone":
                extracted_phone,
        },
    }


# ============================================================
# FIRM REGISTRATION
# ============================================================

def verify_firm_registration(
    text,
    **kwargs
):

    lower = text.lower()

    valid_document = (

        "registrar of firms" in lower

        or

        (
            "firm name" in lower
            and
            "registration" in lower
        )

        or

        (
            "registration certificate"
            in lower
        )
    )

    if not valid_document:

        return {
            "valid": False,

            "message":
                "Document does not appear to be "
                "a firm registration certificate.",

            "extracted": {},
        }

    extracted_firm = (
        extract_firm_name(text)
    )

    extracted_reg = (
        extract_registration_number(
            text
        )
    )

    expected_firm = kwargs.get(
        "expected_firm_name"
    )

    expected_reg = kwargs.get(
        "expected_registration_no"
    )

    errors = []

    if expected_firm:

        valid, score = fuzzy_match(
            expected_firm,
            extracted_firm,
            threshold=65
        )

        if not valid:

            errors.append(
                f"Firm name mismatch. "
                f"Expected '{expected_firm}', "
                f"found '{extracted_firm or 'nothing'}' "
                f"(score {score})"
            )

    if expected_reg:

        expected_normalized = (
            normalize_text(
                expected_reg
            )
        )

        actual_normalized = (
            normalize_text(
                extracted_reg
            )
        )

        if (
            not actual_normalized
            or
            expected_normalized
            != actual_normalized
        ):

            errors.append(
                f"Registration number mismatch. "
                f"Expected '{expected_reg}', "
                f"found '{extracted_reg or 'nothing'}'"
            )

    if errors:

        return {
            "valid": False,
            "message": "; ".join(errors),

            "extracted": {

                "firm_name":
                    extracted_firm,

                "registration_number":
                    extracted_reg,
            },
        }

    return {
        "valid": True,

        "message":
            "Firm registration verified "
            "successfully.",

        "extracted": {

            "firm_name":
                extracted_firm,

            "registration_number":
                extracted_reg,
        },
    }


# ============================================================
# AADHAAR / ID PROOF
# ============================================================

def verify_aadhaar(
    text,
    **kwargs
):

    # --------------------------------------------------------
    # Detect Aadhaar
    # --------------------------------------------------------

    if not detect_aadhaar_document(
        text
    ):

        return {

            "valid": False,

            "message":
                "Document does not appear to be "
                "a valid Aadhaar / ID proof.",

            "extracted": {},
        }

    # --------------------------------------------------------
    # Extract name
    # --------------------------------------------------------

    extracted_name = extract_name(
        text
    )

    expected_name = kwargs.get(
        "expected_name"
    )

    # --------------------------------------------------------
    # Name verification
    # --------------------------------------------------------

    if expected_name:

        valid, score = fuzzy_match(
            expected_name,
            extracted_name,
            threshold=65
        )

        if not valid:

            return {

                "valid": False,

                "message":
                    f"Name mismatch. "
                    f"Expected '{expected_name}', "
                    f"found "
                    f"'{extracted_name or 'nothing'}' "
                    f"(score {score}).",

                "extracted": {

                    "name":
                        extracted_name,
                },
            }

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return {

        "valid": True,

        "message":
            "Aadhaar / ID proof verified "
            "successfully.",

        "extracted": {

            "name":
                extracted_name,
        },
    }


# ============================================================
# PAN
# ============================================================

def verify_pan(
    text,
    **kwargs
):

    lower = text.lower()

    pan_match = re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        text.upper()
    )

    keyword_found = (
        "income tax" in lower
        or
        "permanent account number"
        in lower
    )

    if not (
        keyword_found
        or
        pan_match
    ):

        return {

            "valid": False,

            "message":
                "Document does not appear "
                "to be a PAN card.",

            "extracted": {},
        }

    extracted_name = extract_name(
        text
    )

    expected_name = kwargs.get(
        "expected_name"
    )

    if expected_name:

        valid, score = fuzzy_match(
            expected_name,
            extracted_name,
            threshold=65
        )

        if not valid:

            return {

                "valid": False,

                "message":
                    f"Name mismatch. "
                    f"Expected '{expected_name}', "
                    f"found "
                    f"'{extracted_name or 'nothing'}'.",

                "extracted": {

                    "name":
                        extracted_name,

                    "pan_number":
                        pan_match.group(0)
                        if pan_match
                        else "",
                },
            }

    return {

        "valid": True,

        "message":
            "PAN document verified successfully.",

        "extracted": {

            "name":
                extracted_name,

            "pan_number":
                pan_match.group(0)
                if pan_match
                else "",
        },
    }


# ============================================================
# PASSPORT
# ============================================================

def verify_passport(
    text,
    **kwargs
):

    lower = text.lower()

    passport_found = any(
        keyword in lower
        for keyword in [

            "passport",

            "republic of india",

            "nationality",

            "place of birth",

        ]
    )

    if not passport_found:

        return {

            "valid": False,

            "message":
                "Document does not appear "
                "to be a passport.",

            "extracted": {},
        }

    extracted_name = extract_name(
        text
    )

    expected_name = kwargs.get(
        "expected_name"
    )

    if expected_name:

        valid, score = fuzzy_match(
            expected_name,
            extracted_name,
            threshold=65
        )

        if not valid:

            return {

                "valid": False,

                "message":
                    f"Name mismatch. "
                    f"Expected '{expected_name}', "
                    f"found "
                    f"'{extracted_name or 'nothing'}'.",

                "extracted": {

                    "name":
                        extracted_name,
                },
            }

    return {

        "valid": True,

        "message":
            "Passport verified successfully.",

        "extracted": {

            "name":
                extracted_name,
        },
    }


# ============================================================
# FIR
# ============================================================

def verify_fir(
    text
):

    lower = text.lower()

    if (
        "fir" not in lower
        and
        "first information report"
        not in lower
    ):

        return {

            "valid": False,

            "message":
                "Document does not appear "
                "to be an FIR.",

            "extracted": {},
        }

    return {

        "valid": True,

        "message":
            "FIR verified successfully.",

        "extracted": {},
    }


# ============================================================
# LEGAL NOTICE
# ============================================================

def verify_notice(
    text
):

    lower = text.lower()

    if "notice" not in lower:

        return {

            "valid": False,

            "message":
                "Document does not appear "
                "to be a legal notice.",

            "extracted": {},
        }

    return {

        "valid": True,

        "message":
            "Legal notice verified successfully.",

        "extracted": {},
    }


# ============================================================
# MAIN VERIFY DOCUMENT
# ============================================================

def verify_document(
    file_path,
    expected_type,
    **kwargs
):

    print(
        "========================================"
    )

    print(
        "DOCUMENT VERIFICATION STARTED"
    )

    print(
        "FILE:",
        file_path
    )

    print(
        "EXPECTED TYPE:",
        expected_type
    )

    print(
        "========================================"
    )

    # ========================================================
    # 1. OCR
    # ========================================================

    try:

        text = extract_text_from_file(
            file_path
        )

    except Exception as e:

        print(
            "❌ OCR / DOCUMENT ERROR:"
        )

        print(
            repr(e)
        )

        return {

            "valid": False,

            "message":
                f"Document processing failed: {str(e)}",

            "extracted": {},
        }

    # ========================================================
    # 2. EMPTY OCR
    # ========================================================

    if not text:

        return {

            "valid": False,

            "message":
                "Could not read document. "
                "Upload a clear image/PDF.",

            "extracted": {},
        }

    # ========================================================
    # 3. OCR DEBUG
    # ========================================================

    print(
        "========================================"
    )

    print(
        "OCR SUCCESS"
    )

    print(
        "OCR CHARACTERS:",
        len(text)
    )

    print(
        "OCR PREVIEW:",
        safe_ocr_preview(text)
    )

    print(
        "========================================"
    )

    # ========================================================
    # 4. DOCUMENT TYPE
    # ========================================================

    doc_type = normalize_document_type(
        expected_type
    )

    print(
        "NORMALIZED DOCUMENT TYPE:",
        doc_type
    )

    # ========================================================
    # 5. VERIFY
    # ========================================================

    if doc_type in (
        "aadhaar",
        "id_proof",
    ):

        result = verify_aadhaar(
            text,
            **kwargs
        )

    elif doc_type == "pan":

        result = verify_pan(
            text,
            **kwargs
        )

    elif doc_type == "passport":

        result = verify_passport(
            text,
            **kwargs
        )

    elif doc_type == "bar_council":

        result = verify_bar_council(
            text,
            **kwargs
        )

    elif doc_type == "firm_registration":

        result = verify_firm_registration(
            text,
            **kwargs
        )

    elif doc_type == "fir":

        result = verify_fir(
            text
        )

    elif doc_type == "notice":

        result = verify_notice(
            text
        )

    else:

        return {

            "valid": False,

            "message":
                f"Unsupported document type: "
                f"{expected_type}",

            "extracted": {},
        }

    # ========================================================
    # 6. FINAL RESULT
    # ========================================================

    print(
        "========================================"
    )

    print(
        "DOCUMENT VERIFICATION RESULT"
    )

    print(
        "VALID:",
        result.get(
            "valid",
            False
        )
    )

    print(
        "MESSAGE:",
        result.get(
            "message",
            ""
        )
    )

    print(
        "========================================"
    )

    return result