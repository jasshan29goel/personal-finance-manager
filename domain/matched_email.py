from domain.account_config import AccountConfig
from datetime import datetime

class MatchedEmail:
    def __init__(self, account: AccountConfig, message: dict):
        self.account = account
        self.message = message

    def get_message_id(self) -> str:
        return str(self.message.get("id"))

    def get_email_date(self) -> str:
        headers = self.message.get("payload", {}).get("headers", [])
        date_header = next((h["value"] for h in headers if h["name"].lower() == "date"), None)
        if not date_header:
            return "unknown"
        try:
            # Parses "Mon, 06 May 2025 12:34:56 +0000" to "2025-05-06"
            parsed = datetime.strptime(date_header[:25], "%a, %d %b %Y %H:%M:%S")
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return "unknown"

    def get_filename_prefix(self) -> str:
        return f"{self.account.id}_{self.get_email_date()}"
