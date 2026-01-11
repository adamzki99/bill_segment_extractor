import unittest
import json
import os
import sys
from decimal import Decimal

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the function from the processor module
from processor.parser import parse_nordea_pdf


class TestParseNordeaPdf(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the test PDF path"""
        cls.pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'nordea_20945_54_bill.pdf')
        
        # Verify the file exists
        if not os.path.exists(cls.pdf_path):
            raise FileNotFoundError(f"Test PDF not found at: {cls.pdf_path}")
    
    def test_parse_nordea_pdf_total_amount(self):
        """Test that parsing a Nordea PDF produces the expected total amount of -20945.54"""
        
        # Call the function with the actual PDF
        result_json = parse_nordea_pdf(self.pdf_path)
        
        # Parse the JSON result
        transactions = json.loads(result_json)
        
        # Check if there was an error
        if isinstance(transactions, dict) and 'error' in transactions:
            self.fail(f"PDF parsing failed with error: {transactions['error']}")
        
        # Calculate the total amount
        total_amount = Decimal('0')
        for transaction in transactions:
            total_amount += Decimal(str(transaction['amount']))
        
        # Assert the total is -20945.54
        expected_total = Decimal('-20945.54')
        self.assertEqual(total_amount, expected_total, 
                       f"Expected total amount {expected_total}, but got {total_amount}")
        
        # Additional assertions
        self.assertIsInstance(transactions, list)
        self.assertGreater(len(transactions), 0, "Expected at least one transaction")
        
        # Verify structure of transactions
        for transaction in transactions:
            self.assertIn('date', transaction)
            self.assertIn('purchase_place', transaction)
            self.assertIn('amount', transaction)
            self.assertIn('currency', transaction)
            self.assertEqual(transaction['currency'], 'SEK')
        
        # Print summary
        print(f"\nParsed {len(transactions)} transactions")
        print(f"Total amount: {total_amount} (expected: {expected_total})")


if __name__ == '__main__':
    unittest.main()