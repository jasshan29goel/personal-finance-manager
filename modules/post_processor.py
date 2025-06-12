from domain.category_rule import CategoryRule
from domain.parsed_email import ParsedEmail
from domain.transaction import Transaction
from constants import CategoryType
from typing import List

class PostProcessor:
    def __init__(self, rules: List[CategoryRule]):
        self.rules = rules

    def _assign_category(self, txn: Transaction, email: ParsedEmail) -> CategoryType:
        for rule in self.rules:
            if rule.matches(txn, email):
                return rule.category
        return "MISC"
    
    def process_all(self, emails: List[ParsedEmail]) -> List[ParsedEmail]:
        return [self._process_single(email) for email in emails]

    def _process_single(self, email: ParsedEmail) -> ParsedEmail:
        if email.status != "success" or not email.transactions:
            return email

        for txn in email.transactions:
            txn.category = self._assign_category(txn, email)
        return email
