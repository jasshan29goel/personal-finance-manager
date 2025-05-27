from typing import List
from domain.transaction import Transaction

class ParsedPDF:
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
