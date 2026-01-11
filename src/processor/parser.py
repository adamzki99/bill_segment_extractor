import pdfplumber
import re
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional

class NordeaParser:
    """Library for parsing Nordea PDF credit card statements."""
    
    def __init__(self, currency: str = "SEK"):
        self.currency = currency

    def _is_valid_date(self, date_str: str) -> bool:
        """Checks if the string is a valid YYYYMMDD date."""
        if not date_str.isdigit() or len(date_str) != 8:
            return False
        try:
            datetime.strptime(date_str, "%Y%m%d")
            return True
        except ValueError:
            return False

    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extracts text between the first space and the last minus sign."""
        first_space = text.find(" ")
        last_minus = text.rfind("-")
        if first_space == -1 or last_minus == -1 or last_minus <= first_space:
            return None
        return text[first_space + 1:last_minus].strip()

    def _extract_amount(self, text: str) -> Optional[Decimal]:
        """Parses the numerical amount from the end of the string."""
        # Match an optional minus sign followed by digits with optional spaces/commas/periods
        # This pattern looks for the last number in the string
        pattern = r'(-?\s*\d[\d\s,.]*\d|\d)\s*$'
        match = re.search(pattern, text)
        
        if not match:
            return None
        
        amount_str = match.group(0).strip()
        
        # Normalize: remove spaces, replace comma with period
        normalized = amount_str.replace(" ", "").replace(",", ".")
        
        try:
            return Decimal(normalized)
        except Exception:
            return None

    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Reads a PDF and returns a list of transaction dictionaries."""
        transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                
                for line in text.split('\n'):
                    parts = line.split(' ')
                    if not parts or not self._is_valid_date(parts[0]):
                        continue
                    
                    date_raw = parts[0]
                    merchant = self._extract_merchant(line)
                    amount = self._extract_amount(line)
                

                    if merchant and amount:
                        transactions.append({
                            "date": f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}",
                            "purchase_place": merchant,
                            "amount": str(amount), # Convert Decimal to string for JSON compatibility
                            "currency": self.currency
                        })
        return transactions