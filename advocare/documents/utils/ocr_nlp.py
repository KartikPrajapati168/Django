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

# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

TESSERACT_CMD = os.getenv("TESSERACT_CMD")


def configure_tesseract():
    """
    Configure Tesseract for both Windows and Linux/Render.
    """

    # --------------------------------------------------------
    # 1. Environment variable
    # --------------------------------------------------------

    if TESSERACT_CMD:
        if os.path.exists(TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
            print("✅ Tesseract from environment variable:")
            print(TESSERACT_CMD)
            return

    # --------------------------------------------------------
    # 2. Windows
    # --------------------------------------------------------

    windows_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in windows_paths:

        if os.path.exists(path):

            pytesseract.pytesseract.tesseract_cmd = path

            print("✅ Windows Tesseract found:")
            print(path)

            return

    # --------------------------------------------------------
    # 3. Linux / Render
    # --------------------------------------------------------

    linux_tesseract = shutil.which("tesseract")

    if linux_tesseract:

        pytesseract.pytesseract.tesseract_cmd = (
            linux_tesseract
        )

        print("✅ Linux Tesseract found:")
        print(linux_tesseract)

        return

    print(
        "⚠️ Tesseract executable was not found during configuration."
    )


configure_tesseract()


# ============================================================
# OCR LANGUAGE
# ============================================================

REQUESTED_OCR_LANG = os.getenv(
    "OCR_LANG",
    "eng+guj"
)


def get_ocr_language():
    """
    Select the best available Tesseract language.

    Preferred:
        eng+guj

    Fallback:
        eng
    """

    try:

        installed_languages = pytesseract.get_languages(
            config=""
        )

        print(
            "Available Tesseract languages:",
            installed_languages
        )

        requested = REQUESTED_OCR_LANG.split("+")

        # All requested languages available
        if all(
            language in installed_languages
            for language in requested
        ):

            print(
                "✅ OCR language:",
                REQUESTED_OCR_LANG
            )

            return REQUESTED_OCR_LANG

        # English available
        if "eng" in installed_languages:

            print(
                f"⚠️ {REQUESTED_OCR_LANG} unavailable."
            )

            print(
                "Using English OCR."
            )

            return "eng"

    except Exception as e:

        print(
            "⚠️ Could not detect OCR languages:",
            repr(e)
        )

    return "eng"


OCR_LANG = get_ocr_language()


# ============================================================
# TESSERACT CHECK
# ============================================================

def check_tesseract():
    """
    Check whether Tesseract is available.
    """

    try:

        version = pytesseract.get_tesseract_version()

        print("========================================")
        print("TESSERACT CHECK")
        print("VERSION:", version)
        print(
            "PATH:",
            pytesseract.pytesseract.tesseract_cmd
        )
        print("LANGUAGE:", OCR_LANG)
        print("========================================")

        return True

    except Exception as e:

        print(
            "❌ Tesseract check failed:",
            repr(e)
        )

        return False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_grayscale(image):
    """
    Convert image to grayscale and improve contrast.
    """

    image = image.convert("L")

    enhancer = ImageEnhance.Contrast(
        image
    )

    image = enhancer.enhance(1.8)

    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


def preprocess_threshold(image):
    """
    Create high contrast black/white version.
    """

    image = preprocess_grayscale(
        image
    )

    threshold = 150

    image = image.point(
        lambda pixel: (
            255
            if pixel > threshold
            else 0
        )
    )

    return image


# ============================================================
# OCR SINGLE IMAGE
# ============================================================

def run_ocr(image, psm):

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

    except Exception as e:

        print(
            f"❌ OCR PSM {psm} failed:",
            repr(e)
        )

        return ""


# ============================================================
# OCR IMAGE
# ============================================================

def extract_text_from_image(file_path):
    """
    OCR JPG/JPEG/PNG using multiple image versions
    and multiple Tesseract page segmentation modes.
    """

    print("========================================")
    print("IMAGE OCR STARTED")
    print("FILE:", file_path)
    print("LANGUAGE:", OCR_LANG)
    print("========================================")

    try:

        original = Image.open(
            file_path
        )

        print(
            "IMAGE SIZE:",
            original.size
        )

        # ----------------------------------------------------
        # Create multiple versions
        # ----------------------------------------------------

        grayscale = preprocess_grayscale(
            original.copy()
        )

        threshold = preprocess_threshold(
            original.copy()
        )

        all_text = []

        # ----------------------------------------------------
        # PASS 1
        # Original image
        # ----------------------------------------------------

        print(
            "🔎 OCR original image"
        )

        for psm in [6, 11, 12]:

            text = run_ocr(
                original,
                psm
            )

            if text.strip():

                print(
                    f"Original PSM {psm}:",
                    len(text),
                    "characters"
                )

                all_text.append(text)

        # ----------------------------------------------------
        # PASS 2
        # Grayscale
        # ----------------------------------------------------

        print(
            "🔎 OCR grayscale image"
        )

        for psm in [6, 11, 12]:

            text = run_ocr(
                grayscale,
                psm
            )

            if text.strip():

                print(
                    f"Grayscale PSM {psm}:",
                    len(text),
                    "characters"
                )

                all_text.append(text)

        # ----------------------------------------------------
        # PASS 3
        # Threshold
        # ----------------------------------------------------

        print(
            "🔎 OCR threshold image"
        )

        for psm in [6, 11, 12]:

            text = run_ocr(
                threshold,
                psm
            )

            if text.strip():

                print(
                    f"Threshold PSM {psm}:",
                    len(text),
                    "characters"
                )

                all_text.append(text)

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        final_text = "\n".join(
            all_text
        )

        final_text = final_text.strip()

        print("========================================")
        print(
            "FINAL IMAGE OCR CHARACTERS:",
            len(final_text)
        )
        print("========================================")

        if not final_text:

            raise Exception(
                "No readable text was found in image."
            )

        return final_text

    except pytesseract.TesseractNotFoundError:

        raise Exception(
            "Tesseract OCR is not installed or "
            "cannot be found."
        )

    except Exception as e:

        print(
            "❌ Image OCR error:",
            repr(e)
        )

        raise Exception(
            f"Image OCR failed: {str(e)}"
        )


# ============================================================
# OCR PDF
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Convert PDF pages into images using Poppler
    and perform multiple OCR passes.
    """

    print("========================================")
    print("PDF OCR STARTED")
    print("FILE:", file_path)
    print("LANGUAGE:", OCR_LANG)
    print("========================================")

    try:

        # ----------------------------------------------------
        # Check Poppler
        # ----------------------------------------------------

        pdftoppm = shutil.which(
            "pdftoppm"
        )

        if not pdftoppm:

            raise Exception(
                "Poppler is not installed. "
                "Install poppler-utils on Render."
            )

        print(
            "✅ Poppler:",
            pdftoppm
        )

        # ----------------------------------------------------
        # Convert PDF
        # ----------------------------------------------------

        images = pdf2image.convert_from_path(
            file_path,
            dpi=300,
            fmt="jpeg"
        )

        print(
            "PDF PAGES:",
            len(images)
        )

        all_text = []

        # ----------------------------------------------------
        # Process each page
        # ----------------------------------------------------

        for page_number, original in enumerate(
            images,
            start=1
        ):

            print(
                "========================================"
            )

            print(
                f"🔎 PROCESSING PDF PAGE {page_number}"
            )

            print(
                "========================================"
            )

            grayscale = preprocess_grayscale(
                original.copy()
            )

            threshold = preprocess_threshold(
                original.copy()
            )

            # Original
            for psm in [6, 11, 12]:

                text = run_ocr(
                    original,
                    psm
                )

                if text.strip():

                    print(
                        f"Page {page_number} "
                        f"Original PSM {psm}: "
                        f"{len(text)} characters"
                    )

                    all_text.append(
                        text
                    )

            # Grayscale
            for psm in [6, 11, 12]:

                text = run_ocr(
                    grayscale,
                    psm
                )

                if text.strip():

                    print(
                        f"Page {page_number} "
                        f"Gray PSM {psm}: "
                        f"{len(text)} characters"
                    )

                    all_text.append(
                        text
                    )

            # Threshold
            for psm in [6, 11, 12]:

                text = run_ocr(
                    threshold,
                    psm
                )

                if text.strip():

                    print(
                        f"Page {page_number} "
                        f"Threshold PSM {psm}: "
                        f"{len(text)} characters"
                    )

                    all_text.append(
                        text
                    )

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        final_text = "\n".join(
            all_text
        ).strip()

        print("========================================")
        print(
            "FINAL PDF OCR CHARACTERS:",
            len(final_text)
        )
        print("========================================")

        if not final_text:

            raise Exception(
                "No readable text was found in PDF."
            )

        return final_text

    except Exception as e:

        print(
            "❌ PDF OCR error:",
            repr(e)
        )

        raise Exception(
            f"PDF OCR failed: {str(e)}"
        )


# ============================================================
# MAIN OCR FUNCTION
# ============================================================

def extract_text_from_file(file_path):
    """
    Main document OCR function.

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

    extension = os.path.splitext(
        file_path
    )[1].lower()

    print("========================================")
    print("DOCUMENT OCR")
    print("FILE:", file_path)
    print("EXTENSION:", extension)
    print("========================================")

    if not check_tesseract():

        raise Exception(
            "Tesseract OCR is not available."
        )

    if extension in [
        ".jpg",
        ".jpeg",
        ".png"
    ]:

        return extract_text_from_image(
            file_path
        )

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    raise Exception(
        "Unsupported document format. "
        "Only PDF, JPG, JPEG and PNG are supported."
    )


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    if not text:
        return ""

    # --------------------------------------------------------
    # Name: Kartik Prajapati
    # --------------------------------------------------------

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

            return match.group(
                1
            ).strip()

    # --------------------------------------------------------
    # Fallback line detection
    # --------------------------------------------------------

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

        if all(
            re.match(
                r"^[A-Za-z][A-Za-z\.]*$",
                word
            )
            for word in words
        ):

            # Avoid common headings
            ignored = {
                "government of india",
                "unique identification authority",
                "date of birth",
                "aadhaar card",
            }

            if cleaned.lower() not in ignored:

                return cleaned

    return ""


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(text):

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
        "vastrapur",
        "pincode",
        "pin code",
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in address_keywords
        ):

            return line

    # Generic fallback
    for line in lines:

        line = line.strip()

        if len(line) > 15:

            if re.search(
                r"\d{3,6}",
                line
            ):

                return line

    return ""


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text):

    if not text:
        return ""

    # +91 9876543210
    match = re.search(
        r"(?:\+91[\s\-]?)?"
        r"([6-9]\d{9})",
        text
    )

    if match:

        return match.group(
            1
        )

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

    if tokens:

        return tokens[0]

    return ""


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
    expected_type
):

    if not expected_type:

        return ""

    value = str(
        expected_type
    ).strip().lower()

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
        "registration certificate":
            "firm_registration",
    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# AADHAAR KEYWORD NORMALIZATION
# ============================================================

def compact_ocr_text(text):

    if not text:
        return ""

    text = str(
        text
    ).lower()

    # Remove spaces and punctuation
    return re.sub(
        r"[^a-z0-9\u0900-\u097F\u0A80-\u0AFF]",
        "",
        text
    )


# ============================================================
# AADHAAR KEYWORD DETECTION
# ============================================================

def detect_aadhaar_keyword(text):
    """
    Robust Aadhaar keyword detection.
    Handles OCR variations such as:
    AADHAAR
    AADHAR
    ADHAAR
    AADHER
    UIDAI
    Gujarati Aadhaar text
    """

    if not text:
        return False

    text_lower = text.lower()

    # --------------------------------------------------------
    # 1. Direct keywords
    # --------------------------------------------------------

    direct_keywords = [
        "aadhaar",
        "aadhar",
        "adhar",
        "adhaar",
        "aadher",
        "aaadhar",
        "aadhaarr",
        "uidai",
        "unique identification authority of india",
        "unique identification authority",
    ]

    for keyword in direct_keywords:

        if keyword in text_lower:

            print(
                "✅ Aadhaar keyword detected:",
                keyword
            )

            return True

    # --------------------------------------------------------
    # 2. Remove spaces / punctuation
    # --------------------------------------------------------

    compact_text = re.sub(
        r"[^a-z0-9]",
        "",
        text_lower
    )

    compact_keywords = [
        "aadhaar",
        "aadhar",
        "adhar",
        "adhaar",
        "aadher",
        "aaadhar",
        "uidai",
        "uniqueidentificationauthorityofindia",
        "uniqueidentificationauthority",
    ]

    for keyword in compact_keywords:

        if keyword in compact_text:

            print(
                "✅ Aadhaar compact keyword detected:",
                keyword
            )

            return True

    # --------------------------------------------------------
    # 3. OCR common mistakes
    # --------------------------------------------------------

    ocr_variations = [
        "aadhaar",
        "aadhar",
        "adhar",
        "adhaar",
        "aadher",
        "aaadhar",
        "aadhaer",
        "aadhaar",
        "aadharr",
        "aadharr",
    ]

    words = re.findall(
        r"[A-Za-z]+",
        text_lower
    )

    for word in words:

        if len(word) < 4:
            continue

        for target in ocr_variations:

            score = fuzz.ratio(
                word,
                target
            )

            if score >= 75:

                print(
                    "✅ Aadhaar fuzzy match:",
                    word,
                    "→",
                    target,
                    "score:",
                    score
                )

                return True

    # --------------------------------------------------------
    # 4. UIDAI
    # --------------------------------------------------------

    if "uidai" in text_lower:

        print(
            "✅ Aadhaar detected through UIDAI."
        )

        return True

    # --------------------------------------------------------
    # 5. Unique Identification Authority
    # --------------------------------------------------------

    if (
        "unique identification authority" in text_lower
        or
        "uniqueidentificationauthority" in compact_text
    ):

        print(
            "✅ Aadhaar detected through "
            "Unique Identification Authority."
        )

        return True

    print(
        "❌ Aadhaar keyword not detected."
    )

    return False


# ============================================================
# AADHAAR NUMBER DETECTION
# ============================================================

def detect_aadhaar_number(text):

    if not text:

        return False

    # --------------------------------------------------------
    # 123456789012
    # --------------------------------------------------------

    direct_matches = re.findall(
        r"(?<!\d)\d{12}(?!\d)",
        text
    )

    if direct_matches:

        print(
            "✅ 12-digit Aadhaar-like number detected."
        )

        return True

    # --------------------------------------------------------
    # 1234 5678 9012
    # --------------------------------------------------------

    spaced = re.search(
        r"(?<!\d)"
        r"\d{4}"
        r"[\s\-]+"
        r"\d{4}"
        r"[\s\-]+"
        r"\d{4}"
        r"(?!\d)",
        text
    )

    if spaced:

        print(
            "✅ Spaced 12-digit Aadhaar-like number detected."
        )

        return True

    return False


# ============================================================
# AADHAAR DOCUMENT DETECTION
# ============================================================

def detect_aadhaar_document(text):

    if not text:
        return False

    print("========================================")
    print("AADHAAR DOCUMENT DETECTION")
    print("========================================")

    text_lower = text.lower()

    # --------------------------------------------------------
    # SIGNAL 1: Aadhaar keyword
    # --------------------------------------------------------

    keyword_found = detect_aadhaar_keyword(text)

    # --------------------------------------------------------
    # SIGNAL 2: Aadhaar number
    # --------------------------------------------------------

    aadhaar_number_found = detect_aadhaar_number(text)

    # --------------------------------------------------------
    # SIGNAL 3: UIDAI
    # --------------------------------------------------------

    uidai_found = (
        "uidai" in text_lower
        or
        "unique identification authority" in text_lower
    )

    # --------------------------------------------------------
    # SIGNAL 4: Government of India
    # --------------------------------------------------------

    government_india_found = (
        "government of india" in text_lower
        or
        "govt of india" in text_lower
    )

    # --------------------------------------------------------
    # SIGNAL 5: Aadhaar-specific phrases
    # --------------------------------------------------------

    aadhaar_phrase_found = any(
        phrase in text_lower
        for phrase in [
            "aadhar is proof",
            "aadhaar is proof",
            "aadhaar is unique",
            "aadhaar number",
            "your aadhaar",
            "aadhar number",
            "your aadhar",
            "aadhaar letter",
            "aadhaar services",
            "aadhaar card",
        ]
    )

    print("Keyword:", keyword_found)
    print("Aadhaar Number:", aadhaar_number_found)
    print("UIDAI:", uidai_found)
    print("Government of India:", government_india_found)
    print("Aadhaar Phrase:", aadhaar_phrase_found)

    # --------------------------------------------------------
    # Strong detection
    # --------------------------------------------------------

    if keyword_found:
        print("✅ Aadhaar detected through keyword.")
        return True

    if uidai_found and aadhaar_number_found:
        print("✅ Aadhaar detected through UIDAI + number.")
        return True

    if aadhaar_phrase_found:
        print("✅ Aadhaar detected through Aadhaar phrase.")
        return True

    # --------------------------------------------------------
    # Supporting signals
    # --------------------------------------------------------

    supporting_signals = sum([
        aadhaar_number_found,
        uidai_found,
        government_india_found,
        aadhaar_phrase_found,
    ])

    print(
        "Supporting signals:",
        supporting_signals
    )

    if supporting_signals >= 2:

        print(
            "✅ Aadhaar detected using "
            "multiple supporting signals."
        )

        return True

    print(
        "❌ Aadhaar document not detected."
    )

    return False


# ============================================================
# DOCUMENT KEYWORD CHECK
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

    other_keywords = [
        "pan",
        "passport",
    ]

    return any(
        keyword in text_lower
        for keyword in other_keywords
    )


# ============================================================
# DOCUMENT TYPE VALIDATION
# ============================================================

def validate_document_type(
    text,
    expected_type
):

    if not text:

        return False

    document_type = normalize_document_type(
        expected_type
    )

    print("========================================")
    print("DOCUMENT TYPE VALIDATION")
    print("EXPECTED TYPE:", document_type)
    print("========================================")

    # --------------------------------------------------------
    # AADHAAR
    # --------------------------------------------------------

    if document_type == "aadhaar":

        return detect_aadhaar_document(
            text
        )

    # --------------------------------------------------------
    # PAN
    # --------------------------------------------------------

    if document_type == "pan":

        text_lower = text.lower()

        keyword_found = any(
            keyword in text_lower
            for keyword in [
                "income tax",
                "income-tax",
                "permanent account number",
            ]
        )

        pan_number_found = bool(
            re.search(
                r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
                text.upper()
            )
        )

        return (
            keyword_found
            or pan_number_found
        )

    # --------------------------------------------------------
    # PASSPORT
    # --------------------------------------------------------

    if document_type == "passport":

        text_lower = text.lower()

        keywords = [
            "passport",
            "republic of india",
            "nationality",
            "place of birth",
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    # --------------------------------------------------------
    # FIRM REGISTRATION
    # --------------------------------------------------------

    if document_type == "firm_registration":

        text_lower = text.lower()

        keywords = [
            "registration",
            "registered",
            "firm",
            "company",
            "certificate",
            "llp",
            "gst",
        ]

        return any(
            keyword in text_lower
            for keyword in keywords
        )

    # Unknown document type
    return True


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

    # Remove country code
    if (
        expected_digits.startswith("91")
        and len(expected_digits) > 10
    ):

        expected_digits = (
            expected_digits[-10:]
        )

    if (
        actual_digits.startswith("91")
        and len(actual_digits) > 10
    ):

        actual_digits = (
            actual_digits[-10:]
        )

    if not expected_digits or not actual_digits:

        return False

    return (
        expected_digits
        == actual_digits
    )


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

    print("========================================")
    print("DOCUMENT VERIFICATION STARTED")
    print("FILE:", file_path)
    print(
        "EXPECTED TYPE:",
        expected_type
    )
    print("========================================")

    try:

        # ====================================================
        # 1. OCR
        # ====================================================

        text = extract_text_from_file(
            file_path
        )

        if not text:

            return {
                "success": False,
                "verified": False,
                "error": (
                    "Could not read document."
                ),
            }

        print("========================================")
        print(
            "OCR TEXT LENGTH:",
            len(text)
        )
        print("========================================")

        # IMPORTANT:
        # Do NOT print complete OCR text in production.
        # It may contain Aadhaar number/address/DOB.
        #
        # For debugging, only print first 500 chars.
        print(
            "OCR PREVIEW:",
            text[:500]
        )

        # ====================================================
        # 2. DOCUMENT TYPE
        # ====================================================

        document_type = normalize_document_type(
            expected_type
        )

        document_type_valid = (
            validate_document_type(
                text,
                document_type
            )
        )

        # ====================================================
        # 3. EXTRACT INFORMATION
        # ====================================================

        extracted_name = extract_name(
            text
        )

        extracted_address = extract_address(
            text
        )

        extracted_phone = extract_phone(
            text
        )

        extracted_firm_name = (
            extract_firm_name(
                text
            )
        )

        extracted_registration_no = (
            extract_registration_number(
                text
            )
        )

        # ====================================================
        # 4. MATCH RESULTS
        # ====================================================

        name_verified = None
        name_score = None

        address_verified = None
        address_score = None

        phone_verified = None

        firm_verified = None
        firm_score = None

        registration_verified = None

        # ====================================================
        # NAME
        # ====================================================

        if expected_name:

            (
                name_verified,
                name_score
            ) = fuzzy_match(
                expected_name,
                extracted_name,
                threshold=65
            )

        # ====================================================
        # ADDRESS
        # ====================================================

        if expected_address:

            (
                address_verified,
                address_score
            ) = fuzzy_match(
                expected_address,
                extracted_address,
                threshold=55
            )

        # ====================================================
        # PHONE
        # ====================================================

        if expected_phone:

            phone_verified = phone_match(
                expected_phone,
                extracted_phone
            )

        # ====================================================
        # FIRM
        # ====================================================

        if expected_firm_name:

            (
                firm_verified,
                firm_score
            ) = fuzzy_match(
                expected_firm_name,
                extracted_firm_name,
                threshold=65
            )

        # ====================================================
        # REGISTRATION
        # ====================================================

        if expected_registration_no:

            expected_reg = normalize_text(
                expected_registration_no
            )

            actual_reg = normalize_text(
                extracted_registration_no
            )

            registration_verified = (
                bool(expected_reg)
                and bool(actual_reg)
                and (
                    expected_reg
                    == actual_reg
                    or expected_reg
                    in actual_reg
                    or actual_reg
                    in expected_reg
                )
            )

        # ====================================================
        # 5. FINAL VERIFICATION
        # ====================================================

        checks = []

        # Document type must always be valid
        checks.append(
            bool(document_type_valid)
        )

        if expected_name:

            checks.append(
                bool(name_verified)
            )

        if expected_address:

            checks.append(
                bool(address_verified)
            )

        if expected_phone:

            checks.append(
                bool(phone_verified)
            )

        if expected_firm_name:

            checks.append(
                bool(firm_verified)
            )

        if expected_registration_no:

            checks.append(
                bool(registration_verified)
            )

        verified = all(
            checks
        )

        # ====================================================
        # 6. RESULT
        # ====================================================

        result = {

            "success": True,

            "verified": verified,

            "document_type": document_type,

            "document_type_valid":
                document_type_valid,

            "extracted_data": {

                "name":
                    extracted_name,

                "address":
                    extracted_address,

                "phone":
                    extracted_phone,

                "firm_name":
                    extracted_firm_name,

                "registration_number":
                    extracted_registration_no,
            },

            "verification": {

                "name": {
                    "verified":
                        name_verified,
                    "score":
                        name_score,
                },

                "address": {
                    "verified":
                        address_verified,
                    "score":
                        address_score,
                },

                "phone": {
                    "verified":
                        phone_verified,
                },

                "firm_name": {
                    "verified":
                        firm_verified,
                    "score":
                        firm_score,
                },

                "registration_number": {
                    "verified":
                        registration_verified,
                },
            },

            # DO NOT return full OCR text.
            # It can contain sensitive Aadhaar information.
            "ocr_text_available": True,
        }

        print("========================================")
        print(
            "DOCUMENT VERIFICATION RESULT"
        )
        print("VERIFIED:", verified)
        print(
            "DOCUMENT TYPE VALID:",
            document_type_valid
        )
        print("========================================")

        return result

    except Exception as e:

        print("========================================")
        print(
            "❌ DOCUMENT VERIFICATION FAILED"
        )
        print(
            "ERROR:",
            repr(e)
        )
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