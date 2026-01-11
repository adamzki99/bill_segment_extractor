import sys
import re
import json
import pdfplumber

from decimal import Decimal, getcontext
from datetime import datetime

def parse_amount_from_end(text: str):
    """Parse out the amount from a string like 20241030 PRIX EIGANES 587893 83 STAVANGER 24,85"""
    # Find the last occurrence of "-" or start from the end
    dash_pos = text.rfind("-")
    search_start = dash_pos + 1 if dash_pos != -1 else 0
    
    # Extract the substring we need to search
    suffix = text[search_start:]
    
    # Build a list of valid number characters
    valid_chars = []
    for char in reversed(suffix):
        if char.isdigit() or char in " ,.":
            valid_chars.append(char)
        elif valid_chars:  # Stop at first invalid char after finding valid ones
            break
    
    if not valid_chars:
        return None
    
    # Reverse back and normalize
    buffer = ''.join(reversed(valid_chars))
    normalized = buffer.replace(" ", "").replace(",", ".")
    
    try:
        return Decimal(normalized)
    except ValueError:
        return None
    
def text_between_first_space_and_last_minus(text: str) -> str | None:
    """Parse out the merchant name from a string like 20241030 PRIX EIGANES 587893 83 STAVANGER 24,85"""
    # Find first space
    first_space = text.find(" ")
    if first_space == -1:
        return None

    # Find last negative sign
    last_minus = text.rfind("-")
    if last_minus == -1 or last_minus <= first_space:
        return None

    return text[first_space + 1:last_minus]


def is_valid_yyyymmdd(date_str: str) -> bool:
    '''Check if a string, containing of 8 numbers, is a valid date'''
    # Must be exactly 8 digits
    if not date_str.isdigit() or len(date_str) != 8:
        return False

    try:
        # Attempt to parse using YYYYMMDD format
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False

def parse_nordea_pdf(pdf_path):
    
    transactions = []
    full_text_lines = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text_lines.extend(text.split('\n'))

        for i, line in enumerate(full_text_lines):
            match = is_valid_yyyymmdd(line.split(' ')[0])
            if match:
                date_raw = line.split(' ')[0]
                merchant = text_between_first_space_and_last_minus(line)
                
                if merchant is None:
                    continue

                amount = parse_amount_from_end(line)
                
                # Format date to YYYY-MM-DD
                formatted_date = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"

                transactions.append({
                    "date": formatted_date,
                    "purchase_place": merchant,
                    "amount": -1 * amount,
                    "currency": "SEK"
                })

        return json.dumps(transactions, default=str, indent=4, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_file_path = sys.argv[1]
    
    result = parse_nordea_pdf(pdf_file_path)
    print(result)