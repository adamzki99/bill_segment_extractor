import unittest
import os
import sys
import re
import json
from decimal import Decimal

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processor.parser import NordeaParser

class TestParseNordeaBatch(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the test directory and instantiate the parser"""
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        cls.debug_dir = os.path.join(os.path.dirname(__file__), 'debug_output')
        
        if not os.path.exists(cls.test_data_dir):
            raise FileNotFoundError(f"Test data directory not found at: {cls.test_data_dir}")
            
        # Create debug directory if it doesn't exist
        os.makedirs(cls.debug_dir, exist_ok=True)
            
        cls.parser = NordeaParser(currency="SEK")

    def _extract_expected_amount(self, filename: str) -> Decimal:
        """Extracts amount from 'nordea_bill_20945_54.pdf' -> -20945.54"""
        match = re.search(r'(\d+)_(\d+)\.pdf$', filename)
        if not match:
            raise ValueError(f"Filename '{filename}' invalid pattern")
        
        return Decimal(f"-{match.group(1)}.{match.group(2)}")

    def test_all_pdfs_in_test_data(self):
        """Iterates through all PDFs and dumps JSON on failure."""
        pdf_files = [f for f in os.listdir(self.test_data_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            self.fail("No PDF files found in test_data directory.")

        for filename in pdf_files:
            with self.subTest(filename=filename):
                file_path = os.path.join(self.test_data_dir, filename)
                expected_total = self._extract_expected_amount(filename)
                
                # Parse the actual PDF
                transactions = self.parser.parse_pdf(file_path)
                actual_total = sum(Decimal(str(t['amount'])) for t in transactions)
                
                try:
                    self.assertEqual(
                        actual_total, 
                        expected_total, 
                        f"Sum mismatch in {filename}"
                    )
                except AssertionError as e:
                    # --- Debug Dump Logic ---
                    dump_path = os.path.join(self.debug_dir, f"{filename}.fail.json")
                    debug_info = {
                        "filename": filename,
                        "expected_total": str(expected_total),
                        "actual_total": str(actual_total),
                        "transaction_count": len(transactions),
                        "transactions": transactions
                    }
                    
                    with open(dump_path, 'w', encoding='utf-8') as f:
                        json.dump(debug_info, f, indent=4, ensure_ascii=False)
                    
                    print(f"\n❌ Test failed for {filename}. Data dumped to: {dump_path}")
                    raise e # Re-raise to ensure the test runner sees the failure

if __name__ == '__main__':
    unittest.main()