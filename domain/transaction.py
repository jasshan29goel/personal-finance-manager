from pydantic import BaseModel, Field
from typing import Literal

class Transaction(BaseModel):
    date: str
    amount: float
    note: str
    txn_type: Literal["CREDIT", "DEBIT"]
    confidence: float = Field(..., ge=0, le=1)

    def to_row(self) -> list[str]:
        return [self.date, self.txn_type, str(self.amount), str(self.confidence), self.note]
