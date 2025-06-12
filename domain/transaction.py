from pydantic import BaseModel
from constants import CategoryType, TransactionType
from typing import Optional

class Transaction(BaseModel):
    date: str
    amount: float
    note: str
    txn_type: TransactionType
    category: CategoryType
    reason: str
    score: Optional[float] = None
    best_match_line: str = ""

    def to_row(self) -> list[str]:
        return [self.date, self.txn_type, self.category, str(self.amount), self.note, self.reason, str(self.score) if self.score is not None else "", self.best_match_line]
