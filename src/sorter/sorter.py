import os
from typing import List, Dict, Optional
from groq import Groq

class TransactionClassifier:
    def __init__(self, api_key: Optional[str] = None, model: str = "groq/compound-mini"):
        """Initializes the Groq client and configuration."""
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model

    def classify_transaction(self, transaction: Dict, system_prompt: str) -> str:
        """Classifies a single transaction dictionary."""
        prompt = system_prompt.format(
            purchase_place=transaction.get('purchase_place'),
            amount=transaction.get('amount', 0),
            currency=transaction.get('currency')
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=10,
            stream=False
        )
        
        return completion.choices[0].message.content.strip()

    def process_batch(self, transactions: List[Dict], system_prompt: str) -> List[Dict]:
        """Processes a list of transactions and returns the updated list."""
        for transaction in transactions:
            category = self.classify_transaction(transaction, system_prompt)
            transaction['category'] = category
        return transactions