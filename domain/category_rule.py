from pydantic import BaseModel, Field
from typing import Optional, Literal
from domain.constants import CategoryType, TransactionType
from domain.transaction import Transaction
from domain.parsed_email import ParsedEmail

class CategoryRule(BaseModel):
    priority: int = Field(..., description="Lower value means higher priority")
    txn_type: Optional[TransactionType] = None
    account_id_contains: Optional[str] = None
    note_contains: Optional[str] = None
    regex_note: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    category: CategoryType

    def matches(self, transaction: Transaction, parsed_email: ParsedEmail) -> bool:
        if self.txn_type and self.txn_type != transaction.txn_type:
            return False
        if self.account_id_contains and self.account_id_contains.lower() not in parsed_email.account_id.lower():
            return False
        if self.note_contains and self.note_contains.lower() not in transaction.note.lower():
            return False
        if self.regex_note:
            try:
                import re
                if not re.search(self.regex_note, transaction.note, re.IGNORECASE):
                    return False
            except re.error:
                return False
        if self.min_amount is not None and transaction.amount < self.min_amount:
            return False
        if self.max_amount is not None and transaction.amount > self.max_amount:
            return False
        return True
    
    @classmethod
    def from_sheet_row(cls, row: dict) -> "CategoryRule":
        return cls(
            priority=int(row["priority"]),
            txn_type=row["txn_type"].strip().upper() if row["txn_type"] else None,
            account_id_contains = str(row["account_id_contains"]).strip() or None,
            note_contains=str(row["note_contains"]).strip() or None,
            regex_note=str(row["regex_note"]).strip() or None,
            min_amount=float(row["min_amount"]) if row["min_amount"] not in ("", None) else None,
            max_amount=float(row["max_amount"]) if row["max_amount"] not in ("", None) else None,
            category=row["category"].strip().upper()
        )

