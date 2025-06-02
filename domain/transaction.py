from pydantic import BaseModel, Field
from typing import Literal
from domain.constants import CategoryType, TransactionType

class Transaction(BaseModel):
    date: str
    amount: float
    note: str
    txn_type: TransactionType
    category: CategoryType
    reason: str

    def to_row(self) -> list[str]:
        return [self.date, self.txn_type, self.category, str(self.amount), self.note, self.reason]
