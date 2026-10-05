# import os
# import re
# import pytesseract
# from PIL import Image
# import pdf2image
# from fuzzywuzzy import fuzz

# # ========== CONFIGURATION ==========
# # 🔴 UNCOMMENT AND SET YOUR TESSERACT PATH (Windows example)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # For Gujarati + English: 'guj+eng'
# OCR_LANG = 'eng'

# # ========== HELPER: Extract text from image/PDF ==========
# def extract_text_from_file(file_path):
#     """Extract text with detailed error reporting."""
#     ext = os.path.splitext(file_path)[1].lower()
#     text = ""
#     try:
#         if ext in ['.jpg', '.jpeg', '.png']:
#             image = Image.open(file_path)
#             # Use a good configuration for single text block
#             custom_config = r'--oem 3 --psm 6'
#             text = pytesseract.image_to_string(image, lang=OCR_LANG, config=custom_config)
#         elif ext == '.pdf':
#             images = pdf2image.convert_from_path(file_path, dpi=300)
#             for img in images:
#                 text += pytesseract.image_to_string(img, lang=OCR_LANG) + "\n"
#         else:
#             return ""
#     except pytesseract.TesseractNotFoundError:
#         raise Exception("Tesseract not found. Please install Tesseract OCR and set the correct path.")
#     except Exception as e:
#         # Log the error for debugging (will appear in Django console)
#         print(f"OCR extraction error: {str(e)}")
#         raise Exception(f"OCR failed: {str(e)}")
#     return text.strip()

# # ========== EXTRACTION FUNCTIONS ==========
# def extract_name(text):
#     # Try "Name:" pattern
#     match = re.search(r'Name[:\s]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     # Fallback: lines that look like a name (2-4 capitalized words)
#     lines = text.split('\n')
#     for line in lines:
#         line = line.strip()
#         if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line):
#             return line
#     return ""

# def extract_address(text):
#     lines = text.split('\n')
#     for line in lines:
#         if re.search(r'\d+.*(Road|Street|Nagari|Apartment|Sola|Naranpura|Ahmedabad)', line, re.IGNORECASE):
#             return line.strip()
#     return ""

# def extract_phone(text):
#     match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
#     return match.group(0) if match else ""

# def extract_firm_name(text):
#     match = re.search(r'Firm Name[:\s]+([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
#     return match.group(1).strip() if match else ""

# def extract_registration_number(text):
#     match = re.search(r'Registration Number[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     tokens = re.findall(r'\b[A-Za-z0-9\-]{6,}\b', text)
#     return tokens[0] if tokens else ""

# # ========== MAIN VERIFICATION FUNCTION ==========
# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}
    
#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}
    
#     text_lower = text.lower()
    
#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
        
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
        
#         errors = []
#         if expected_name:
#             if not extracted_name:
#                 errors.append("Could not extract name from document.")
#             elif fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
#         if expected_address:
#             if not extracted_address:
#                 errors.append("Could not extract address from document.")
#             elif fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number from document.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}
    
#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
        
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
        
#         errors = []
#         if expected_firm:
#             if not extracted_firm:
#                 errors.append("Could not extract firm name from document.")
#             elif fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm}'")
#         if expected_reg:
#             if not extracted_reg:
#                 errors.append("Could not extract registration number from document.")
#             elif expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}
    
#     # ----- ID PROOF -----
#     elif expected_type == 'id_proof':
#         expected_name = kwargs.get('expected_name', '')
#         id_keywords = ['aadhaar', 'aadhar', 'pan', 'passport', 'आधार', 'આધાર']
#         keyword_found = any(k in text_lower for k in id_keywords)
        
#         extracted_name = extract_name(text)
#         errors = []
#         if not keyword_found:
#             errors.append("Document does not appear to be a valid ID proof (missing Aadhar/PAN/Passport keywords).")
#         if expected_name:
#             if not extracted_name:
#                 errors.append("Could not extract name from ID proof.")
#             elif fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "ID proof verified successfully."}
    
#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}
























# import os
# import re
# import pytesseract
# from PIL import Image
# import pdf2image
# from fuzzywuzzy import fuzz

# # ========== CONFIGURATION ==========
# # Set Tesseract path if not in PATH (Windows example)
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # For Gujarati + English, use: lang='guj+eng'
# # For English only: lang='eng'
# OCR_LANG = 'eng'  # change to 'guj+eng' if you need Gujarati support

# # ========== HELPER: Extract text from image/PDF ==========
# def extract_text_from_file(file_path):
#     """Extract text from image or PDF with detailed error logging."""
#     ext = os.path.splitext(file_path)[1].lower()
#     text = ""
#     try:
#         if ext in ['.jpg', '.jpeg', '.png']:
#             image = Image.open(file_path)
#             # Add OCR configuration for better accuracy
#             custom_config = r'--oem 3 --psm 6'
#             text = pytesseract.image_to_string(image, lang=OCR_LANG, config=custom_config)
#         elif ext == '.pdf':
#             # Convert PDF to images
#             images = pdf2image.convert_from_path(file_path, dpi=300)
#             for img in images:
#                 text += pytesseract.image_to_string(img, lang=OCR_LANG) + "\n"
#         else:
#             return ""  # unsupported format
#     except pytesseract.TesseractNotFoundError:
#         raise Exception("Tesseract is not installed or not in PATH. Please install Tesseract OCR.")
#     except Exception as e:
#         print(f"OCR error: {e}")
#         return ""
#     return text.strip()

# # ========== EXTRACTION FUNCTIONS ==========
# def extract_name(text):
#     # First try "Name:" pattern
#     match = re.search(r'Name[:\s]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
    
#     # Then look for lines that look like a full name (2-4 words, each capitalized)
#     lines = text.split('\n')
#     for line in lines:
#         line = line.strip()
#         # Exclude lines that are all caps or contain digits
#         if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line):
#             return line
#     return ""

# def extract_address(text):
#     """Extract address (looks for numbers, street, city, pin)."""
#     # Simple: lines containing digits and words like 'Road', 'Street', 'Ahmedabad'
#     lines = text.split('\n')
#     for line in lines:
#         if re.search(r'\d+.*(Road|Street|Nagari|Apartment|Sola|Naranpura)', line, re.IGNORECASE):
#             return line.strip()
#     return ""

# def extract_phone(text):
#     """Extract phone number (Indian mobile/landline)."""
#     # Match 10-digit or +91-XXXXXXXXXX
#     match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
#     if match:
#         return match.group(0)
#     return ""

# def extract_firm_name(text):
#     """Extract firm name from registration certificate."""
#     # Look for "Firm Name:" pattern
#     match = re.search(r'Firm Name[:\s]+([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     return ""

# def extract_registration_number(text):
#     """Extract registration number (e.g., GUJ-123456, sdfghjklm8523)."""
#     # Alphanumeric with possible hyphens
#     match = re.search(r'Registration Number[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     # Fallback: any alphanumeric string that looks like a reg no (length > 5)
#     tokens = re.findall(r'\b[A-Za-z0-9\-]{6,}\b', text)
#     if tokens:
#         return tokens[0]
#     return ""

# # ========== MAIN VERIFICATION FUNCTION ==========
# def verify_document(file_path, expected_type, **kwargs):
#     """
#     expected_type: 'bar_council', 'firm_registration', 'id_proof'
#     kwargs may contain: expected_name, expected_address, expected_phone,
#                         expected_firm_name, expected_registration_no
#     """
#     text = extract_text_from_file(file_path)
#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}
    
#     # Normalize text (lowercase, remove extra spaces)
#     text_lower = text.lower()
    
#     # ----- BAR COUNCIL CERTIFICATE -----
#     if expected_type == 'bar_council':
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
        
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
        
#         errors = []
#         if expected_name and extracted_name:
#             if fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
#         elif expected_name and not extracted_name:
#             errors.append("Could not extract name from document.")
        
#         if expected_address and extracted_address:
#             if fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address}'")
#         elif expected_address and not extracted_address:
#             errors.append("Could not extract address from document.")
        
#         if expected_phone and extracted_phone:
#             # Normalize phone numbers (remove spaces, +91)
#             exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#             ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#             if exp_phone != ext_phone:
#                 errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         elif expected_phone and not extracted_phone:
#             errors.append("Could not extract phone number from document.")
        
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}
    
#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         expected_firm_name = kwargs.get('expected_firm_name', '')
#         expected_reg_no = kwargs.get('expected_registration_no', '')
        
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
        
#         errors = []
#         if expected_firm_name and extracted_firm:
#             if fuzz.partial_ratio(expected_firm_name.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm_name}', found '{extracted_firm}'")
#         elif expected_firm_name and not extracted_firm:
#             errors.append("Could not extract firm name from document.")
        
#         if expected_reg_no and extracted_reg:
#             if expected_reg_no.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg_no}', found '{extracted_reg}'")
#         elif expected_reg_no and not extracted_reg:
#             errors.append("Could not extract registration number from document.")
        
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}
    
#     # ----- ID PROOF (Aadhar, PAN, Passport) -----
#     elif expected_type == 'id_proof':
#         expected_name = kwargs.get('expected_name', '')
        
#         # First, check if document contains Aadhar, PAN, or Passport keywords
#         id_keywords = ['aadhaar', 'aadhar', 'pan', 'passport', 'आधार', 'આધાર']
#         keyword_found = any(keyword in text_lower for keyword in id_keywords)
        
#         extracted_name = extract_name(text)
        
#         errors = []
#         if not keyword_found:
#             errors.append("Document does not appear to be a valid ID proof (missing Aadhar/PAN/Passport keywords).")
        
#         if expected_name and extracted_name:
#             if fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
#         elif expected_name and not extracted_name:
#             errors.append("Could not extract name from ID proof.")
        
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "ID proof verified successfully."}
    
#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}



import os
import re
import shutil

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
from fuzzywuzzy import fuzz


# ============================================================
# CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# TESSERACT CONFIGURATION
# ------------------------------------------------------------
# Local Windows:
#   C:\Program Files\Tesseract-OCR\tesseract.exe
#
# Render/Linux:
#   /usr/bin/tesseract
#
# We first check environment variable TESSERACT_CMD.
# If not present, we automatically search for tesseract.
# ------------------------------------------------------------

TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if TESSERACT_CMD:
    if os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    # Windows
    windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(windows_tesseract):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract

    # Linux / Render
    elif shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")


# ------------------------------------------------------------
# OCR LANGUAGE
# ------------------------------------------------------------
#
# Default:
#     eng+guj
#
# If Gujarati language data is not installed, automatically
# fallback to English.
# ------------------------------------------------------------

DEFAULT_OCR_LANG = os.getenv("OCR_LANG", "eng+guj")


def get_ocr_language():
    """
    Check installed Tesseract languages and select
    the best available OCR language.
    """

    try:
        installed_languages = pytesseract.get_languages(config="")

        print("Available Tesseract languages:", installed_languages)

        # User explicitly configured OCR_LANG
        requested_languages = DEFAULT_OCR_LANG.split("+")

        # If all requested languages are installed
        if all(lang in installed_languages for lang in requested_languages):
            return DEFAULT_OCR_LANG

        # Gujarati unavailable -> English fallback
        if "eng" in installed_languages:
            print(
                f"WARNING: '{DEFAULT_OCR_LANG}' not available. "
                "Falling back to 'eng'."
            )
            return "eng"

    except Exception as e:
        print("Could not detect Tesseract languages:", e)

    # Final fallback
    return "eng"


OCR_LANG = get_ocr_language()


# ============================================================
# HELPER - CHECK TESSERACT
# ============================================================

def check_tesseract():
    """
    Verify that Tesseract OCR is installed and accessible.
    """

    try:
        version = pytesseract.get_tesseract_version()

        print("========================================")
        print("TESSERACT VERSION:", version)
        print("TESSERACT PATH:", pytesseract.pytesseract.tesseract_cmd)
        print("OCR LANGUAGE:", OCR_LANG)
        print("========================================")

        return True

    except Exception as e:
        print("❌ Tesseract check failed:", repr(e))
        return False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """
    Improve OCR accuracy.

    Steps:
    1. Convert to grayscale
    2. Increase contrast
    3. Sharpen image
    4. Apply binary threshold
    """

    # Convert image to grayscale
    image = image.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    # Binary threshold
    threshold = 150

    image = image.point(
        lambda p: 255 if p > threshold else 0
    )

    return image


# ============================================================
# OCR FOR IMAGE
# ============================================================

def extract_text_from_image(file_path):
    """
    Extract OCR text from JPG/JPEG/PNG image.
    """

    try:
        print("========================================")
        print("OCR IMAGE:", file_path)
        print("OCR LANGUAGE:", OCR_LANG)
        print("========================================")

        image = Image.open(file_path)

        print(
            "Image size:",
            image.size
        )

        image = preprocess_image(image)

        # PSM 11 works better for documents containing
        # multiple separated text blocks.
        custom_config = r"--oem 3 --psm 11"

        text = pytesseract.image_to_string(
            image,
            lang=OCR_LANG,
            config=custom_config
        )

        print("OCR characters:", len(text))

        return text.strip()

    except pytesseract.TesseractNotFoundError:
        raise Exception(
            "Tesseract OCR is not installed or cannot be found."
        )

    except Exception as e:
        print("❌ Image OCR error:", repr(e))

        raise Exception(
            f"Image OCR failed: {str(e)}"
        )


# ============================================================
# OCR FOR PDF
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Convert PDF pages to images using Poppler and then
    perform OCR on every page.
    """

    try:
        print("========================================")
        print("OCR PDF:", file_path)
        print("OCR LANGUAGE:", OCR_LANG)
        print("========================================")

        # Check Poppler
        pdftoppm_path = shutil.which("pdftoppm")

        if not pdftoppm_path:
            raise Exception(
                "Poppler is not installed. "
                "Install poppler-utils on Render/Linux."
            )

        print("Poppler path:", pdftoppm_path)

        # Convert PDF pages into images
        images = pdf2image.convert_from_path(
            file_path,
            dpi=300,
            fmt="jpeg"
        )

        print(
            f"✅ PDF converted into {len(images)} image(s)"
        )

        full_text = ""

        for index, img in enumerate(images):

            print(
                f"🔎 Processing PDF page {index + 1}"
            )

            img = preprocess_image(img)

            text = pytesseract.image_to_string(
                img,
                lang=OCR_LANG,
                config=r"--oem 3 --psm 11"
            )

            print(
                f"✅ Page {index + 1} OCR characters:",
                len(text)
            )

            full_text += text + "\n"

        return full_text.strip()

    except Exception as e:

        print("❌ PDF OCR error:", repr(e))

        raise Exception(
            f"PDF OCR failed: {str(e)}"
        )


# ============================================================
# EXTRACT TEXT FROM IMAGE / PDF
# ============================================================

def extract_text_from_file(file_path):
    """
    Main OCR function.

    Supported:
        JPG
        JPEG
        PNG
        PDF
    """

    if not os.path.exists(file_path):
        raise Exception(
            f"File does not exist: {file_path}"
        )

    ext = os.path.splitext(file_path)[1].lower()

    print("========================================")
    print("DOCUMENT OCR STARTED")
    print("FILE:", file_path)
    print("EXTENSION:", ext)
    print("========================================")

    # Check Tesseract
    if not check_tesseract():
        raise Exception(
            "Tesseract OCR is not available on the server."
        )

    try:

        if ext in [".jpg", ".jpeg", ".png"]:

            text = extract_text_from_image(
                file_path
            )

        elif ext == ".pdf":

            text = extract_text_from_pdf(
                file_path
            )

        else:

            raise Exception(
                "Unsupported document format. "
                "Only PDF, JPG, JPEG and PNG are supported."
            )

        text = text.strip()

        print("========================================")
        print("FINAL OCR TEXT LENGTH:", len(text))
        print("========================================")

        if not text:
            raise Exception(
                "No readable text was found in the document."
            )

        return text

    except Exception as e:

        print("❌ OCR extraction error:", repr(e))

        raise Exception(
            f"OCR failed: {str(e)}"
        )


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):
    """
    Extract person's name from OCR text.
    """

    if not text:
        return ""

    # Name: Kartik Prajapati
    match = re.search(
        r"\bName\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,80})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Name without colon
    match = re.search(
        r"\bName\s+([A-Za-z][A-Za-z\s\.]{2,80})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Fallback: find lines that look like a person's name
    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove common OCR symbols
        cleaned = re.sub(
            r"[^A-Za-z\s\.]",
            "",
            line
        ).strip()

        words = cleaned.split()

        if 2 <= len(words) <= 4:

            if all(
                re.match(
                    r"^[A-Za-z][A-Za-z\.]*$",
                    word
                )
                for word in words
            ):
                return cleaned

    return ""


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(text):
    """
    Try to extract address from OCR text.
    """

    if not text:
        return ""

    lines = text.splitlines()

    address_keywords = [
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
        "vastrapur"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        if any(
            keyword in line_lower
            for keyword in address_keywords
        ):
            return line

    # Generic fallback
    for line in lines:

        line = line.strip()

        if re.search(r"\d{3,6}", line):

            if len(line) > 15:
                return line

    return ""


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text):
    """
    Extract Indian mobile number.
    """

    if not text:
        return ""

    # +91 9876543210
    match = re.search(
        r"(?:\+91[\s\-]?)?([6-9]\d{9})",
        text
    )

    if match:

        phone = match.group(1)

        return phone

    return ""


# ============================================================
# FIRM NAME EXTRACTION
# ============================================================

def extract_firm_name(text):
    """
    Extract firm/company name.
    """

    if not text:
        return ""

    patterns = [
        r"\bFirm\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)",
        r"\bCompany\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)",
        r"\bOrganization\s*Name\s*[:\-]\s*([A-Za-z0-9\s\.\-&]+)"
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
# REGISTRATION NUMBER EXTRACTION
# ============================================================

def extract_registration_number(text):
    """
    Extract registration number.
    """

    if not text:
        return ""

    patterns = [
        r"Registration\s*(?:No|Number)?\s*[:\-]\s*([A-Za-z0-9\-\/]+)",
        r"Reg\.?\s*(?:No|Number)?\s*[:\-]\s*([A-Za-z0-9\-\/]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    # Generic fallback
    tokens = re.findall(
        r"\b[A-Za-z0-9\-\/]{6,}\b",
        text
    )

    if tokens:
        return tokens[0]

    return ""


# ============================================================
# DOCUMENT KEYWORD CHECK
# ============================================================

def contains_id_keyword(text_lower):
    """
    Detect Aadhaar / PAN / Passport keywords.
    """

    if not text_lower:
        return False

    keywords = [
        "aadhaar",
        "aadhar",
        "adhar",
        "pan",
        "passport",
        "आधार",
        "આધાર"
    ]

    # Exact match
    for keyword in keywords:

        if keyword in text_lower:
            return True

    # Fuzzy match
    for keyword in [
        "aadhaar",
        "aadhar",
        "adhar"
    ]:

        score = fuzz.partial_ratio(
            keyword,
            text_lower
        )

        if score >= 80:
            return True

    return False


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value):
    """
    Normalize text before comparison.
    """

    if value is None:
        return ""

    value = str(value).lower()

    # Remove extra spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Remove punctuation
    value = re.sub(
        r"[^a-z0-9\s]",
        "",
        value
    )

    return value.strip()


# ============================================================
# FUZZY TEXT MATCH
# ============================================================

def fuzzy_match(expected, actual, threshold=70):
    """
    Compare expected value with OCR value.
    """

    expected = normalize_text(expected)
    actual = normalize_text(actual)

    if not expected or not actual:
        return False, 0

    score = fuzz.token_set_ratio(
        expected,
        actual
    )

    return score >= threshold, score


# ============================================================
# PHONE MATCH
# ============================================================

def phone_match(expected, actual):
    """
    Compare phone numbers by digits only.
    """

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

    # Remove +91 prefix
    if expected_digits.startswith("91") and len(expected_digits) > 10:
        expected_digits = expected_digits[-10:]

    if actual_digits.startswith("91") and len(actual_digits) > 10:
        actual_digits = actual_digits[-10:]

    if not expected_digits or not actual_digits:
        return False

    return expected_digits == actual_digits


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

def normalize_document_type(expected_type):
    """
    Normalize document type coming from frontend.
    """

    if not expected_type:
        return ""

    value = str(expected_type).strip().lower()

    aliases = {
        "aadhar": "aadhaar",
        "adhar": "aadhaar",
        "aadhaar card": "aadhaar",
        "aadhar card": "aadhaar",

        "pan card": "pan",

        "passport copy": "passport",

        "firm": "firm_registration",
        "firm registration": "firm_registration",
        "registration": "firm_registration",
        "registration certificate": "firm_registration",
    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# DOCUMENT KEYWORD VALIDATION
# ============================================================

def validate_document_type(text, expected_type):
    """
    Check whether OCR text appears to belong to the
    expected document type.
    """

    text_lower = text.lower()

    document_type = normalize_document_type(
        expected_type
    )

    if document_type == "aadhaar":

        keywords = [
            "aadhaar",
            "aadhar",
            "adhar",
            "uidai",
            "आधार",
            "આધાર"
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    if document_type == "pan":

        keywords = [
            "income tax",
            "income-tax",
            "permanent account number",
            "pan"
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    if document_type == "passport":

        keywords = [
            "passport",
            "republic of india",
            "nationality",
            "place of birth"
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    if document_type == "firm_registration":

        keywords = [
            "registration",
            "registered",
            "firm",
            "company",
            "certificate",
            "llp",
            "gst"
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    # Unknown type
    return True


# ============================================================
# MAIN DOCUMENT VERIFICATION
# ============================================================

def verify_document(
    file_path,
    expected_type,
    expected_name=None,
    expected_address=None,
    expected_phone=None,
    expected_firm_name=None,
    expected_registration_no=None
):
    """
    Main document verification function.

    Returns a dictionary suitable for Django REST Framework.
    """

    print("========================================")
    print("DOCUMENT VERIFICATION STARTED")
    print("FILE:", file_path)
    print("EXPECTED TYPE:", expected_type)
    print("========================================")

    try:

        # ----------------------------------------------------
        # 1. OCR
        # ----------------------------------------------------

        text = extract_text_from_file(
            file_path
        )

        if not text:

            return {
                "success": False,
                "verified": False,
                "error": "Could not read document."
            }

        print("========================================")
        print("OCR TEXT")
        print(text[:3000])
        print("========================================")

        text_lower = text.lower()

        # ----------------------------------------------------
        # 2. DOCUMENT TYPE
        # ----------------------------------------------------

        document_type = normalize_document_type(
            expected_type
        )

        document_type_valid = validate_document_type(
            text,
            document_type
        )

        # ----------------------------------------------------
        # 3. EXTRACT INFORMATION
        # ----------------------------------------------------

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

        extracted_registration_no = (
            extract_registration_number(text)
        )

        # ----------------------------------------------------
        # 4. MATCH RESULTS
        # ----------------------------------------------------

        name_verified = None
        name_score = None

        address_verified = None
        address_score = None

        phone_verified = None

        firm_verified = None
        firm_score = None

        registration_verified = None

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if expected_name:

            name_verified, name_score = fuzzy_match(
                expected_name,
                extracted_name,
                threshold=65
            )

        # ----------------------------------------------------
        # ADDRESS
        # ----------------------------------------------------

        if expected_address:

            address_verified, address_score = fuzzy_match(
                expected_address,
                extracted_address,
                threshold=55
            )

        # ----------------------------------------------------
        # PHONE
        # ----------------------------------------------------

        if expected_phone:

            phone_verified = phone_match(
                expected_phone,
                extracted_phone
            )

        # ----------------------------------------------------
        # FIRM NAME
        # ----------------------------------------------------

        if expected_firm_name:

            firm_verified, firm_score = fuzzy_match(
                expected_firm_name,
                extracted_firm_name,
                threshold=65
            )

        # ----------------------------------------------------
        # REGISTRATION NUMBER
        # ----------------------------------------------------

        if expected_registration_no:

            expected_reg = normalize_text(
                expected_registration_no
            )

            actual_reg = normalize_text(
                extracted_registration_no
            )

            registration_verified = (
                expected_reg != ""
                and actual_reg != ""
                and (
                    expected_reg == actual_reg
                    or expected_reg in actual_reg
                    or actual_reg in expected_reg
                )
            )

        # ----------------------------------------------------
        # 5. DETERMINE FINAL VERIFICATION
        # ----------------------------------------------------

        verification_checks = []

        # Document type
        verification_checks.append(
            document_type_valid
        )

        # Only add checks when frontend supplied
        # expected values.

        if expected_name:
            verification_checks.append(
                bool(name_verified)
            )

        if expected_address:
            verification_checks.append(
                bool(address_verified)
            )

        if expected_phone:
            verification_checks.append(
                bool(phone_verified)
            )

        if expected_firm_name:
            verification_checks.append(
                bool(firm_verified)
            )

        if expected_registration_no:
            verification_checks.append(
                bool(registration_verified)
            )

        # At least one check must exist
        if verification_checks:

            verified = all(
                verification_checks
            )

        else:

            # If no expected information was provided,
            # only OCR/document type is used.
            verified = bool(
                document_type_valid
            )

        # ----------------------------------------------------
        # 6. RESULT
        # ----------------------------------------------------

        result = {
            "success": True,

            "verified": verified,

            "document_type": document_type,

            "document_type_valid": document_type_valid,

            "extracted_data": {
                "name": extracted_name,
                "address": extracted_address,
                "phone": extracted_phone,
                "firm_name": extracted_firm_name,
                "registration_number": extracted_registration_no,
            },

            "verification": {
                "name": {
                    "verified": name_verified,
                    "score": name_score,
                },

                "address": {
                    "verified": address_verified,
                    "score": address_score,
                },

                "phone": {
                    "verified": phone_verified,
                },

                "firm_name": {
                    "verified": firm_verified,
                    "score": firm_score,
                },

                "registration_number": {
                    "verified": registration_verified,
                },
            },

            "ocr_text": text,
        }

        print("========================================")
        print("DOCUMENT VERIFICATION RESULT")
        print(result)
        print("========================================")

        return result

    except Exception as e:

        print("========================================")
        print("❌ DOCUMENT VERIFICATION FAILED")
        print("ERROR:", repr(e))
        print("========================================")

        return {
            "success": False,
            "verified": False,
            "error": str(e),
        }

# ========== MAIN VERIFICATION ==========
# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}

#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

#     # 🔴 DEBUG: Print extracted text to console (remove in production)
#     print(f"=== Extracted Text for {expected_type} ===\n{text}\n=== END ===\n")

#     text_lower = text.lower()

#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
        
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
        
#         errors = []
#         if expected_name:
#             if not extracted_name:
#                 errors.append("Could not extract name from document.")
#             elif fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
#         if expected_address:
#             if not extracted_address:
#                 errors.append("Could not extract address from document.")
#             elif fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number from document.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}

#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
        
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
        
#         errors = []
#         if expected_firm:
#             if not extracted_firm:
#                 errors.append("Could not extract firm name from document.")
#             elif fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm}'")
#         if expected_reg:
#             if not extracted_reg:
#                 errors.append("Could not extract registration number from document.")
#             elif expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}

#     # ----- ID PROOF (Aadhaar / PAN / Passport) -----
#     elif expected_type == 'id_proof':
#         expected_name = kwargs.get('expected_name', '')
        
#         keyword_found = contains_id_keyword(text_lower)
#         extracted_name = extract_name(text)
        
#         errors = []
#         if not keyword_found:
#             # Instead of failing immediately, warn but still check name
#             errors.append("Document may not be a standard ID proof (missing Aadhaar/PAN/Passport keywords).")
        
#         if expected_name:
#             if not extracted_name:
#                 errors.append("Could not extract name from ID proof.")
#             elif fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name}'")
        
#         # If name matches, consider it valid even if keywords are fuzzy-missing
#         if errors and (len(errors) == 1 and "Document may not be a standard ID proof" in errors[0] and expected_name and extracted_name and fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) >= 70):
#             # Keyword missing but name matches -> still accept
#             return {"valid": True, "message": "ID proof verified (name matches, though document type not clearly detected)."}
        
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "ID proof verified successfully."}

#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}



# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}

#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

#     # 🔴 DEBUG: Print first 500 chars of extracted text (remove in production)
#     print(f"\n=== Extracted text ({expected_type}) ===\n{text[:500]}\n=== END ===\n")

#     text_lower = text.lower()

#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         # ✅ Use regex to match "bar" and "council" with any whitespace in between
#         if not re.search(r'bar\s+council', text_lower):
#             return {"valid": False, "message": "Document does not appear to be a Bar Council certificate (missing 'bar council' keyword)."}

#         # Optional field validation (name, address, phone) – unchanged
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
#         errors = []
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'")
#         if expected_address:
#             if not extracted_address or fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address or 'nothing'}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}

#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         # ✅ Use regex for "registrar of firms"
#         if not re.search(r'registrar\s+of\s+firms', text_lower):
#             return {"valid": False, "message": "Document does not appear to be a firm registration certificate (missing 'Registrar of Firms' stamp or phrase)."}

#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
#         errors = []
#         if expected_firm:
#             if not extracted_firm or fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm or 'nothing'}'")
#         if expected_reg:
#             if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg or 'nothing'}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}

#     # ----- ID PROOF (Aadhaar) -----
#     elif expected_type == 'id_proof':
#         # ✅ Check for Aadhaar keywords (with or without spaces, case‑insensitive)
#         id_keywords = ['aadhaar', 'aadhar', 'आधार', 'આધાર']
#         keyword_found = any(kw in text_lower for kw in id_keywords)
#         # Also try regex for "aadhaar" with possible typos
#         if not keyword_found and not re.search(r'aad[ha]ar', text_lower):
#             return {"valid": False, "message": "Document does not appear to be an Aadhaar card (missing 'Aadhaar' keyword)."}

#         expected_name = kwargs.get('expected_name', '')
#         extracted_name = extract_name(text)
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 return {"valid": False, "message": f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'"}
#         return {"valid": True, "message": "ID proof (Aadhaar) verified successfully."}

#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}



# import os
# import re
# import pytesseract
# from PIL import Image, ImageEnhance, ImageFilter
# import pdf2image
# from fuzzywuzzy import fuzz
# import cv2
# import numpy as np

# # ========== CONFIGURATION ==========
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# OCR_LANG = 'eng'

# def preprocess_image(image):
#     """Improve OCR for low‑contrast text."""
#     gray = image.convert('L')
#     enhancer = ImageEnhance.Contrast(gray)
#     gray = enhancer.enhance(2.0)
#     img_np = np.array(gray)
#     # Adaptive threshold
#     thresh = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                    cv2.THRESH_BINARY, 11, 2)
#     return Image.fromarray(thresh)

# def extract_text_from_file(file_path):
#     ext = os.path.splitext(file_path)[1].lower()
#     full_text = ""
#     if ext in ['.jpg', '.jpeg', '.png']:
#         image = Image.open(file_path)
#         image = preprocess_image(image)
#         text = pytesseract.image_to_string(image, lang=OCR_LANG, config='--oem 3 --psm 6')
#         full_text = text
#     elif ext == '.pdf':
#         images = pdf2image.convert_from_path(file_path, dpi=400)
#         for img in images:
#             img = preprocess_image(img)
#             text = pytesseract.image_to_string(img, lang=OCR_LANG, config='--oem 3 --psm 6')
#             full_text += text + "\n"
#     return full_text.strip()

# def extract_name(text):
#     match = re.search(r'Name[:\s]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     lines = text.split('\n')
#     for line in lines:
#         if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line.strip()):
#             return line.strip()
#     return ""

# def extract_address(text):
#     lines = text.split('\n')
#     for line in lines:
#         if re.search(r'\d+.*(Road|Street|Nagari|Apartment|Sola|Naranpura|Ahmedabad|kalupur)', line, re.IGNORECASE):
#             return line.strip()
#     return ""

# def extract_phone(text):
#     match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
#     return match.group(0) if match else ""

# def extract_firm_name(text):
#     match = re.search(r'Firm Name[:\s]+([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
#     return match.group(1).strip() if match else ""

# def extract_registration_number(text):
#     match = re.search(r'Registration Number[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     tokens = re.findall(r'\b[A-Za-z0-9\-]{6,}\b', text)
#     return tokens[0] if tokens else ""

# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}

#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

#     text_lower = text.lower()
#     print(f"\n=== Extracted Text ({expected_type}) ===\n{text[:800]}\n=== END ===\n")

#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         # Check for variations: "bar council", "the bar council", "bar\ncouncil"
#         patterns = [
#             r'bar\s+council',
#             r'the\s+bar\s+council',
#             r'bar[\s\n]+council',
#             r'bar\s*council'
#         ]
#         found = any(re.search(p, text_lower) for p in patterns)
#         if not found:
#             # Alternative: look for "advocate" + a number (enrolment) + "enrolment" or "bar association"
#             has_advocate = 'advocate' in text_lower
#             has_number = re.search(r'\b\d{4,6}\b', text)  # e.g., 38870
#             has_enrolment = 'enrolment' in text_lower or 'enrollment' in text_lower
#             if has_advocate or has_number and has_enrolment:
#                 # Accept as bar council
#                 pass
#             else:
#                 return {"valid": False, "message": "Document does not appear to be a Bar Council certificate (missing 'bar council' keyword)."}

#         # Optional field validation (if name/address/phone provided)
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
#         errors = []
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'")
#         if expected_address:
#             if not extracted_address or fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address or 'nothing'}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}

#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         if not re.search(r'registrar\s+of\s+firms', text_lower):
#             # Fallback: must contain both "firm name" and "registration number"
#             if not ('firm name' in text_lower and 'registration number' in text_lower):
#                 return {"valid": False, "message": "Document does not appear to be a firm registration certificate (missing 'Registrar of Firms' phrase)."}

#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
#         errors = []
#         if expected_firm:
#             if not extracted_firm or fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm or 'nothing'}'")
#         if expected_reg:
#             if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg or 'nothing'}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}

#     # ----- ID PROOF (Aadhaar) -----
#     elif expected_type == 'id_proof':
#         id_keywords = ['aadhaar', 'aadhar', 'आधार', 'આધાર']
#         keyword_found = any(kw in text_lower for kw in id_keywords)
#         if not keyword_found and not re.search(r'aad[ha]ar', text_lower):
#             return {"valid": False, "message": "Document does not appear to be an Aadhaar card (missing 'Aadhaar' keyword)."}

#         expected_name = kwargs.get('expected_name', '')
#         extracted_name = extract_name(text)
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 return {"valid": False, "message": f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'"}
#         return {"valid": True, "message": "ID proof (Aadhaar) verified successfully."}

#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}





# WORKING BEFORE





# import os
# import re
# import pytesseract
# from PIL import Image, ImageEnhance
# import pdf2image
# from fuzzywuzzy import fuzz
# import cv2
# import numpy as np
# import PyPDF2   # add this: pip install PyPDF2

# # ========== CONFIGURATION ==========
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# OCR_LANG = 'eng'

# def preprocess_image(image):
#     """Improve OCR for low‑contrast text."""
#     gray = image.convert('L')
#     enhancer = ImageEnhance.Contrast(gray)
#     gray = enhancer.enhance(2.0)
#     img_np = np.array(gray)
#     thresh = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                    cv2.THRESH_BINARY, 11, 2)
#     return Image.fromarray(thresh)

# def extract_text_from_file(file_path):
#     """Extract text from image or PDF. Uses PyPDF2 first for text‑based PDFs,
#        then falls back to OCR (pdf2image + Tesseract) if needed."""
#     ext = os.path.splitext(file_path)[1].lower()
#     full_text = ""

#     if ext in ['.jpg', '.jpeg', '.png']:
#         image = Image.open(file_path)
#         image = preprocess_image(image)
#         full_text = pytesseract.image_to_string(image, lang=OCR_LANG, config='--oem 3 --psm 6')

#     elif ext == '.pdf':
#         # First try PyPDF2 (fast, no poppler needed)
#         try:
#             with open(file_path, 'rb') as f:
#                 reader = PyPDF2.PdfReader(f)
#                 for page in reader.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         full_text += page_text + "\n"
#         except Exception as e:
#             print(f"PyPDF2 extraction failed: {e}")

#         # If PyPDF2 returned nothing (scanned PDF), fallback to OCR
#         if not full_text.strip():
#             try:
#                 images = pdf2image.convert_from_path(file_path, dpi=400)
#                 for img in images:
#                     img = preprocess_image(img)
#                     text = pytesseract.image_to_string(img, lang=OCR_LANG, config='--oem 3 --psm 6')
#                     full_text += text + "\n"
#             except Exception as e:
#                 print(f"pdf2image OCR failed: {e} (poppler may be missing)")
#                 # If poppler is missing, return empty and let the caller handle
#                 return ""

#     return full_text.strip()

# # ---------- Helper extraction functions ----------
# def extract_name(text):
#     match = re.search(r'Name[:\s]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     lines = text.split('\n')
#     for line in lines:
#         if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line.strip()):
#             return line.strip()
#     return ""

# def extract_address(text):
#     lines = text.split('\n')
#     for line in lines:
#         if re.search(r'\d+.*(Road|Street|Nagari|Apartment|Sola|Naranpura|Ahmedabad|kalupur)', line, re.IGNORECASE):
#             return line.strip()
#     return ""

# def extract_phone(text):
#     match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
#     return match.group(0) if match else ""

# def extract_firm_name(text):
#     match = re.search(r'Firm Name[:\s]+([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
#     return match.group(1).strip() if match else ""

# def extract_registration_number(text):
#     match = re.search(r'Registration Number[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     tokens = re.findall(r'\b[A-Za-z0-9\-]{6,}\b', text)
#     return tokens[0] if tokens else ""

# # ---------- Main verification function ----------
# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}

#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

#     text_lower = text.lower()
#     print(f"\n=== Extracted Text ({expected_type}) ===\n{text[:800]}\n=== END ===\n")

#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         patterns = [
#             r'bar\s+council',
#             r'the\s+bar\s+council',
#             r'bar[\s\n]+council',
#             r'bar\s*council'
#         ]
#         found = any(re.search(p, text_lower) for p in patterns)
#         if not found:
#             has_advocate = 'advocate' in text_lower
#             has_number = re.search(r'\b\d{4,6}\b', text)
#             has_enrolment = 'enrolment' in text_lower or 'enrollment' in text_lower
#             if has_advocate or has_number and has_enrolment:
#                 pass
#             else:
#                 return {"valid": False, "message": "Document does not appear to be a Bar Council certificate (missing 'bar council' keyword)."}

#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
#         errors = []
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'")
#         if expected_address:
#             if not extracted_address or fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address or 'nothing'}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}

#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         if not re.search(r'registrar\s+of\s+firms', text_lower):
#             if not ('firm name' in text_lower and 'registration number' in text_lower):
#                 return {"valid": False, "message": "Document does not appear to be a firm registration certificate (missing 'Registrar of Firms' phrase)."}

#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
#         errors = []
#         if expected_firm:
#             if not extracted_firm or fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm or 'nothing'}'")
#         if expected_reg:
#             if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg or 'nothing'}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}

#     # ----- AADHAAR / ID PROOF -----
#     elif expected_type in ['id_proof', 'aadhar']:
#         if not any(kw in text_lower for kw in ['aadhaar', 'aadhar']):
#             return {"valid": False, "message": "Document does not appear to be an Aadhaar card (missing 'aadhar' keyword)."}

#         expected_name = kwargs.get('expected_name', '')
#         if expected_name:
#             extracted_name = extract_name(text)
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 return {"valid": False, "message": f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'"}
#         return {"valid": True, "message": "Aadhaar card verified successfully."}

#     # ----- FIR (First Information Report) -----
#     elif expected_type == 'fir':
#         if 'fir' not in text_lower:
#             return {"valid": False, "message": "Document does not appear to be an FIR (missing 'FIR' keyword)."}
#         return {"valid": True, "message": "FIR verified successfully."}

#     # ----- LEGAL NOTICE -----
#     elif expected_type == 'notice':
#         if 'notice' not in text_lower:
#             return {"valid": False, "message": "Document does not appear to be a legal notice (missing 'NOTICE' keyword)."}
#         return {"valid": True, "message": "Legal notice verified successfully."}

#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}


# def verify_document(file_path, expected_type, **kwargs):
#     try:
#         text = extract_text_from_file(file_path)
#     except Exception as e:
#         return {"valid": False, "message": str(e)}

#     if not text:
#         return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

#     text_lower = text.lower()

#     # ----- BAR COUNCIL -----
#     if expected_type == 'bar_council':
#         # ✅ Must contain "bar council" keyword
#         if 'bar council' not in text_lower:
#             return {"valid": False, "message": "Document does not appear to be a Bar Council certificate (missing 'bar council' keyword)."}

#         # Optional field validation (name, address, phone) – keep as before
#         expected_name = kwargs.get('expected_name', '')
#         expected_address = kwargs.get('expected_address', '')
#         expected_phone = kwargs.get('expected_phone', '')
#         extracted_name = extract_name(text)
#         extracted_address = extract_address(text)
#         extracted_phone = extract_phone(text)
#         errors = []
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'")
#         if expected_address:
#             if not extracted_address or fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
#                 errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address or 'nothing'}'")
#         if expected_phone:
#             if not extracted_phone:
#                 errors.append("Could not extract phone number.")
#             else:
#                 exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
#                 ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
#                 if exp_phone != ext_phone:
#                     errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Bar Council certificate verified successfully."}

#     # ----- FIRM REGISTRATION -----
#     elif expected_type == 'firm_registration':
#         # ✅ Must contain "registrar of firms" keyword (case‑insensitive)
#         if 'registrar of firms' not in text_lower:
#             return {"valid": False, "message": "Document does not appear to be a firm registration certificate (missing 'Registrar of Firms' stamp or phrase)."}

#         expected_firm = kwargs.get('expected_firm_name', '')
#         expected_reg = kwargs.get('expected_registration_no', '')
#         extracted_firm = extract_firm_name(text)
#         extracted_reg = extract_registration_number(text)
#         errors = []
#         if expected_firm:
#             if not extracted_firm or fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
#                 errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm or 'nothing'}'")
#         if expected_reg:
#             if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
#                 errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg or 'nothing'}'")
#         if errors:
#             return {"valid": False, "message": "; ".join(errors)}
#         return {"valid": True, "message": "Firm registration verified successfully."}

#     # ----- ID PROOF (Aadhaar / PAN / Passport) -----
#     elif expected_type == 'id_proof':
#         # ✅ Must contain "aadhaar" or "aadhar" keyword (exact word, not just fuzzy)
#         id_keywords = ['aadhaar', 'aadhar', 'आधार', 'આધાર']
#         keyword_found = any(kw in text_lower for kw in id_keywords)
#         if not keyword_found:
#             return {"valid": False, "message": "Document does not appear to be an Aadhaar card (missing 'Aadhaar' keyword)."}

#         expected_name = kwargs.get('expected_name', '')
#         extracted_name = extract_name(text)
#         if expected_name:
#             if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
#                 return {"valid": False, "message": f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'"}
#         return {"valid": True, "message": "ID proof (Aadhaar) verified successfully."}

#     else:
#         return {"valid": False, "message": f"Unsupported document type: {expected_type}"}












import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
from fuzzywuzzy import fuzz
import PyPDF2

# ========== CONFIGURATION ==========
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
OCR_LANG = 'eng'

def preprocess_image(image):
    """Improve OCR for low‑contrast text using PIL only (no OpenCV)."""
    # Convert to grayscale
    gray = image.convert('L')
    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    # Apply a simple threshold using PIL (values > 128 become white)
    gray = gray.point(lambda p: 255 if p > 128 else 0)
    return gray

def extract_text_from_file(file_path):
    """Extract text from image or PDF. Uses PyPDF2 first for text‑based PDFs,
       then falls back to OCR (pdf2image + Tesseract) if needed."""
    ext = os.path.splitext(file_path)[1].lower()
    full_text = ""

    if ext in ['.jpg', '.jpeg', '.png']:
        try:
            image = Image.open(file_path)
            image = preprocess_image(image)
            full_text = pytesseract.image_to_string(image, lang=OCR_LANG, config='--oem 3 --psm 6')
        except Exception as e:
            return f"Error processing image: {e}"

    elif ext == '.pdf':
        # First try PyPDF2 (fast, no poppler needed)
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")

        # If PyPDF2 returned nothing (scanned PDF), fallback to OCR
        if not full_text.strip():
            try:
                images = pdf2image.convert_from_path(file_path, dpi=400)
                for img in images:
                    img = preprocess_image(img)
                    text = pytesseract.image_to_string(img, lang=OCR_LANG, config='--oem 3 --psm 6')
                    full_text += text + "\n"
            except Exception as e:
                print(f"pdf2image OCR failed: {e} (poppler may be missing)")
                return ""

    return full_text.strip()

# ---------- Helper extraction functions (unchanged) ----------
def extract_name(text):
    match = re.search(r'Name[:\s]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    lines = text.split('\n')
    for line in lines:
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line.strip()):
            return line.strip()
    return ""

def extract_address(text):
    lines = text.split('\n')
    for line in lines:
        if re.search(r'\d+.*(Road|Street|Nagari|Apartment|Sola|Naranpura|Ahmedabad|kalupur)', line, re.IGNORECASE):
            return line.strip()
    return ""

def extract_phone(text):
    match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
    return match.group(0) if match else ""

def extract_firm_name(text):
    match = re.search(r'Firm Name[:\s]+([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_registration_number(text):
    match = re.search(r'Registration Number[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    tokens = re.findall(r'\b[A-Za-z0-9\-]{6,}\b', text)
    return tokens[0] if tokens else ""

# ---------- Main verification function (unchanged except removed OpenCV reference) ----------
def verify_document(file_path, expected_type, **kwargs):
    try:
        text = extract_text_from_file(file_path)
    except Exception as e:
        return {"valid": False, "message": str(e)}

    if not text:
        return {"valid": False, "message": "Could not read document. Please upload a clear image/PDF."}

    text_lower = text.lower()
    print(f"\n=== Extracted Text ({expected_type}) ===\n{text[:800]}\n=== END ===\n")

    # ----- BAR COUNCIL -----
    if expected_type == 'bar_council':
        patterns = [
            r'bar\s+council',
            r'the\s+bar\s+council',
            r'bar[\s\n]+council',
            r'bar\s*council'
        ]
        found = any(re.search(p, text_lower) for p in patterns)
        if not found:
            has_advocate = 'advocate' in text_lower
            has_number = re.search(r'\b\d{4,6}\b', text)
            has_enrolment = 'enrolment' in text_lower or 'enrollment' in text_lower
            if has_advocate or has_number and has_enrolment:
                pass
            else:
                return {"valid": False, "message": "Document does not appear to be a Bar Council certificate (missing 'bar council' keyword)."}

        expected_name = kwargs.get('expected_name', '')
        expected_address = kwargs.get('expected_address', '')
        expected_phone = kwargs.get('expected_phone', '')
        extracted_name = extract_name(text)
        extracted_address = extract_address(text)
        extracted_phone = extract_phone(text)
        errors = []
        if expected_name:
            if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
                errors.append(f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'")
        if expected_address:
            if not extracted_address or fuzz.partial_ratio(expected_address.lower(), extracted_address.lower()) < 60:
                errors.append(f"Address mismatch: expected '{expected_address}', found '{extracted_address or 'nothing'}'")
        if expected_phone:
            if not extracted_phone:
                errors.append("Could not extract phone number.")
            else:
                exp_phone = re.sub(r'\D', '', expected_phone)[-10:]
                ext_phone = re.sub(r'\D', '', extracted_phone)[-10:]
                if exp_phone != ext_phone:
                    errors.append(f"Phone mismatch: expected '{expected_phone}', found '{extracted_phone}'")
        if errors:
            return {"valid": False, "message": "; ".join(errors)}
        return {"valid": True, "message": "Bar Council certificate verified successfully."}

    # ----- FIRM REGISTRATION -----
    elif expected_type == 'firm_registration':
        if not re.search(r'registrar\s+of\s+firms', text_lower):
            if not ('firm name' in text_lower and 'registration number' in text_lower):
                return {"valid": False, "message": "Document does not appear to be a firm registration certificate (missing 'Registrar of Firms' phrase)."}

        expected_firm = kwargs.get('expected_firm_name', '')
        expected_reg = kwargs.get('expected_registration_no', '')
        extracted_firm = extract_firm_name(text)
        extracted_reg = extract_registration_number(text)
        errors = []
        if expected_firm:
            if not extracted_firm or fuzz.partial_ratio(expected_firm.lower(), extracted_firm.lower()) < 70:
                errors.append(f"Firm name mismatch: expected '{expected_firm}', found '{extracted_firm or 'nothing'}'")
        if expected_reg:
            if not extracted_reg or expected_reg.lower() != extracted_reg.lower():
                errors.append(f"Registration number mismatch: expected '{expected_reg}', found '{extracted_reg or 'nothing'}'")
        if errors:
            return {"valid": False, "message": "; ".join(errors)}
        return {"valid": True, "message": "Firm registration verified successfully."}

    # ----- AADHAAR / ID PROOF -----
    elif expected_type in ['id_proof', 'aadhar']:
        if not any(kw in text_lower for kw in ['aadhaar', 'aadhar']):
            return {"valid": False, "message": "Document does not appear to be an Aadhaar card (missing 'aadhar' keyword)."}

        expected_name = kwargs.get('expected_name', '')
        if expected_name:
            extracted_name = extract_name(text)
            if not extracted_name or fuzz.partial_ratio(expected_name.lower(), extracted_name.lower()) < 70:
                return {"valid": False, "message": f"Name mismatch: expected '{expected_name}', found '{extracted_name or 'nothing'}'"}
        return {"valid": True, "message": "Aadhaar card verified successfully."}

    # ----- FIR (First Information Report) -----
    elif expected_type == 'fir':
        if 'fir' not in text_lower:
            return {"valid": False, "message": "Document does not appear to be an FIR (missing 'FIR' keyword)."}
        return {"valid": True, "message": "FIR verified successfully."}

    # ----- LEGAL NOTICE -----
    elif expected_type == 'notice':
        if 'notice' not in text_lower:
            return {"valid": False, "message": "Document does not appear to be a legal notice (missing 'NOTICE' keyword)."}
        return {"valid": True, "message": "Legal notice verified successfully."}

    else:
        return {"valid": False, "message": f"Unsupported document type: {expected_type}"}






# import os
# import re
# from pdf2image import convert_from_path
# from PyPDF2 import PdfReader
# from PIL import Image
# import spacy
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Load spaCy model (small English)
# nlp = spacy.load("en_core_web_sm")

# def extract_text_from_pdf(pdf_path):
#     """Extract text from PDF using PyPDF2 (fallback to OCR if needed)."""
#     text = ""
#     try:
#         reader = PdfReader(pdf_path)
#         for page in reader.pages:
#             text += page.extract_text() or ""
#     except Exception as e:
#         print(f"PyPDF2 failed: {e}, falling back to OCR")
#         text = ocr_pdf(pdf_path)
#     return text

# def ocr_pdf(pdf_path):
#     """Convert PDF pages to images and run OCR."""
#     images = convert_from_path(pdf_path)
#     text = ""
#     for img in images:
#         text += pytesseract.image_to_string(img)
#     return text

# def extract_text_from_image(image_path):
#     """Run OCR on an image file."""
#     img = Image.open(image_path)
#     return pytesseract.image_to_string(img)

# def extract_text(file_path):
#     """Detect file type and extract text accordingly."""
#     ext = os.path.splitext(file_path)[1].lower()
#     if ext == '.pdf':
#         return extract_text_from_pdf(file_path)
#     elif ext in ['.jpg', '.jpeg', '.png']:
#         return extract_text_from_image(file_path)
#     else:
#         raise ValueError("Unsupported file type")

# def analyze_document(text, expected_type):
#     """
#     NLP analysis:
#     - Validate if document matches expected_type (FIR, notice, aadhar, pan, etc.)
#     - Extract key fields: case_number, court_name, parties, date, etc.
#     Returns dict with 'valid' (bool), 'message', and 'extracted_data'.
#     """
#     text_lower = text.lower()
#     doc = nlp(text[:100000])  # limit text for performance

#     # Define keyword sets for each document type
#     keywords = {
#         'fir': ['first information report', 'fir no', 'police station', 'section', 'ipc', 'crpc', 'offence'],
#         'notice': ['legal notice', 'notice', 'advocate', 'client', 'demand', 'reply within', 'u/s', 'section'],
#         'aadhar': ['aadhar', 'uidai', 'enrolment', 'unique identification'],
#         'pan': ['pan', 'permanent account number', 'income tax', 'department'],
#         'passport': ['passport', 'republic of india', 'date of birth', 'given name', 'surname'],
#         'voter': ['voter id', 'election commission', 'voter', 'epic no'],
#         'driving': ['driving licence', 'license', 'transport', 'motor vehicle'],
#         'bar_council': ['bar council', 'bar council certificate', 'enrolment', 'advocate', 'bar association'],
#         'firm_registration': ['registration', 'firm registration', 'partnership deed', 'certificate of incorporation', 'gst'],
#         'id_proof': ['aadhar', 'pan', 'passport', 'voter id', 'driving license', 'government id'],
#     }
    
#     required_keywords = keywords.get(expected_type, [])
#     if not required_keywords:
#         # Unknown type - accept but warn
#         return {"valid": True, "message": "Document type not specifically checked.", "extracted_data": {}}
    
#     # Check if at least one required keyword exists
#     found = any(kw in text_lower for kw in required_keywords)
#     if not found:
#         return {
#             "valid": False,
#             "message": f"Document does not appear to be a valid {expected_type.upper()}. Missing keywords: {', '.join(required_keywords[:3])}...",
#             "extracted_data": {}
#         }
    
#     # Extract additional metadata (example for FIR)
#     extracted = {}
#     if expected_type == 'fir':
#         # Extract FIR number
#         fir_no_match = re.search(r'(?:fir|first information report)\s*no\.?\s*[:.]?\s*(\d+/\d+)', text_lower)
#         if fir_no_match:
#             extracted['fir_number'] = fir_no_match.group(1)
#         # Extract police station
#         ps_match = re.search(r'police\s+station\s*[:.]?\s*([\w\s]+)', text_lower)
#         if ps_match:
#             extracted['police_station'] = ps_match.group(1).strip()
#         # Extract sections
#         sections = re.findall(r'section\s*(\d+(?:[a-z]|\s*&\s*\d+)*)', text_lower)
#         if sections:
#             extracted['sections'] = sections
    
#     elif expected_type == 'notice':
#         # Extract notice date
#         date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text)
#         if date_match:
#             extracted['notice_date'] = date_match.group(1)
#         # Extract advocate name
#         adv_match = re.search(r'(?:advocate|adv\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
#         if adv_match:
#             extracted['advocate_name'] = adv_match.group(1)
    
#     return {
#         "valid": True,
#         "message": f"Document verified as {expected_type.upper()}.",
#         "extracted_data": extracted
#     }

# def verify_document(file_path, expected_type):
#     """Main function: extract text + NLP analysis."""
#     try:
#         text = extract_text(file_path)
#         if not text.strip():
#             return {"valid": False, "message": "No text could be extracted from the document. Please upload a clear, readable copy."}
#         result = analyze_document(text, expected_type)
#         return result
#     except Exception as e:
#         return {"valid": False, "message": f"Verification error: {str(e)}"}