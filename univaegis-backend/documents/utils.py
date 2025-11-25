import os
import re
from typing import Dict, Any

from django.conf import settings
from pdf2image import convert_from_path
from PIL import Image
import pytesseract


def get_poppler_path() -> str:
    """
    Get Poppler path (mainly for Windows).
    We will read it from settings if available.
    """
    return getattr(settings, "POPPLER_PATH", None)


def is_pdf(file_path: str) -> bool:
    return file_path.lower().endswith(".pdf")


def run_ocr_on_image(image: Image.Image) -> str:
    """
    Run Tesseract OCR on a PIL Image and return extracted text.
    """
    # You can tune config for better accuracy later.
    text = pytesseract.image_to_string(image)
    return text


def ocr_file(file_path: str) -> str:
    """
    Run OCR on a file.

    - If PDF: convert pages to images using pdf2image, then OCR each page.
    - If image: open with PIL and run OCR.
    """
    if is_pdf(file_path):
        # For PDF: convert first 2 pages to images
        poppler_path = get_poppler_path()
        if poppler_path:
            pages = convert_from_path(file_path, dpi=200, first_page=1, last_page=2, poppler_path=poppler_path)
        else:
            # On Linux/Mac, poppler is usually on PATH, so poppler_path not needed
            pages = convert_from_path(file_path, dpi=200, first_page=1, last_page=2)

        all_text = []
        for page in pages:
            page_text = run_ocr_on_image(page)
            all_text.append(page_text)
        return "\n".join(all_text)

    else:
        # Assume it's an image (JPG/PNG)
        image = Image.open(file_path).convert("RGB")
        return run_ocr_on_image(image)


def compute_confidence_placeholder(text: str) -> float:
    """
    Placeholder confidence function.

    For now, return a dummy value based on length of text.
    Later, you could integrate real confidence scores
    from Tesseract or a ML model.
    """
    if not text:
        return 0.0
    # simple heuristic: more text => higher confidence, between 0.3 and 0.9
    length = len(text)
    if length < 100:
        return 0.3
    elif length < 500:
        return 0.6
    else:
        return 0.8


def extract_academic_fields(text: str) -> Dict[str, Any]:
    """
    Extract fields from academic documents:
    - Student Name
    - University/School
    - Course Name
    - Percentage or GPA
    - Year of Passing
    """
    t = text.replace("\r", "\n")

    # Percentage like "85%" or "85.5 %"
    percentage = None
    m = re.search(r"(\d{1,3}(?:\.\d+)?)[\s]*%+", t)
    if m:
        percentage = float(m.group(1))
    else:
        m = re.search(r"(percentage|marks|scored)[\s:\-]*([0-9]{1,3}(?:\.\d+)?)", t, re.IGNORECASE)
        if m:
            percentage = float(m.group(2))

    # GPA like "GPA: 8.5"
    gpa = None
    m = re.search(r"\bGPA[:\s]*([0-9]\.?[0-9]?)\b", t, re.IGNORECASE)
    if m:
        try:
            gpa = float(m.group(1))
        except ValueError:
            gpa = None

    # Year of Passing (4 digits, prefer patterns with labels)
    year_of_passing = None
    m = re.search(
        r"(Year of Passing|Passed in|Passing Year|Class of)[\s:\-]*([12][0-9]{3})",
        t,
        re.IGNORECASE,
    )
    if m:
        year_of_passing = int(m.group(2))
    else:
        # fallback: look for a reasonable year (1990-2099)
        m = re.search(r"\b(19[9][0-9]|20[0-9]{2})\b", t)
        if m:
            year_of_passing = int(m.group(1))

    # Student Name: "Name: John Doe" or similar
    student_name = None
    m = re.search(
        r"(Student Name|Name of Student|Name)[:\s\-]{1,10}([A-Z][A-Za-z ,.'-]{1,80})",
        t,
    )
    if m:
        student_name = m.group(2).strip()
    else:
        for line in t.splitlines():
            if "name" in line.lower() and len(line.split()) <= 7:
                parts = re.split(r":|-", line)
                if len(parts) >= 2:
                    candidate = parts[1].strip()
                    if len(candidate) > 2:
                        student_name = candidate
                        break

    # University / College / School
    university = None
    m = re.search(
        r"(University|College|Institute|School)[:\s\-]{1,10}(.{3,120})",
        t,
        re.IGNORECASE,
    )
    if m:
        university = m.group(2).strip().split("\n")[0]

    # Course / Program / Degree
    course = None
    m = re.search(
        r"(Course|Program|Programme|Degree)[:\s\-]{1,10}(.{2,80})",
        t,
        re.IGNORECASE,
    )
    if m:
        course = m.group(2).strip().split("\n")[0]

    return {
        "doc_type": "academic",
        "student_name": student_name,
        "university": university,
        "course": course,
        "percentage": percentage,
        "gpa": gpa,
        "year_of_passing": year_of_passing,
    }


def extract_financial_fields(text: str) -> Dict[str, Any]:
    """
    Extract fields from financial documents like bank statement / FD:
    - Bank Name
    - Account Holder Name
    - Available Balance or FD Amount
    - Date (one main date)
    """
    t = text.replace("\r", "\n")

    # Bank name (very heuristic)
    bank_name = None
    m = re.search(r"(Bank of [A-Za-z ]+|[A-Za-z ]+ Bank)", t)
    if m:
        bank_name = m.group(0).strip()

    # Account holder: "Account Holder: John Doe" or "A/c Name: ..."
    account_holder = None
    m = re.search(
        r"(Account Holder|Account Name|A/c Name|A/c Holder)[:\s\-]{1,10}(.{2,80})",
        t,
        re.IGNORECASE,
    )
    if m:
        account_holder = m.group(2).strip().split("\n")[0]

    # Balance or FD amount: look for "Available Balance" or "Balance" or "Amount"
    available_balance = None
    m = re.search(
        r"(Available Balance|Balance|FD Amount|Deposit Amount)[:\s\-]*([0-9,]+\.\d{2}|[0-9,]+)",
        t,
        re.IGNORECASE,
    )
    if m:
        amount_str = m.group(2).replace(",", "")
        try:
            available_balance = float(amount_str)
        except ValueError:
            available_balance = None

    # Date: simple pattern DD/MM/YYYY or YYYY-MM-DD
    date = None
    m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", t)
    if m:
        date = m.group(1)
    else:
        m = re.search(r"\b(20[0-9]{2}-\d{2}-\d{2})\b", t)
        if m:
            date = m.group(1)

    return {
        "doc_type": "financial",
        "bank_name": bank_name,
        "account_holder": account_holder,
        "available_balance": available_balance,
        "date": date,
    }


def extract_fields(doc_type: str, text: str) -> Dict[str, Any]:
    """
    Entry point: choose correct extraction based on doc_type.
    Add a small raw_text_snippet for debugging.
    """
    if not text:
        return {"error": "No text extracted from document."}

    if doc_type == "academic":
        base = extract_academic_fields(text)
    else:
        base = extract_financial_fields(text)

    base["raw_text_snippet"] = text[:300]
    return base
