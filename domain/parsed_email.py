from typing import List, Optional
from pydantic import BaseModel
from domain.transaction import Transaction

class ParsedEmail(BaseModel):
    execution_id: str
    message_id: str                  # For tracking
    email_date: str                  # YYYY-MM-DD
    account_id: str                  # From EmailConfig.id

    transactions: Optional[List[Transaction]] = None
    total_amount_due: Optional[float] = None
    closing_balance: Optional[float] = None

    status: str                      # success / failed
    script_message: Optional[str] = None
