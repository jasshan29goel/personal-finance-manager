from domain.email_config import EmailConfig
from datetime import datetime
from email.utils import parsedate_to_datetime

class Email:
    def __init__(self, config: EmailConfig, message: dict):
        self.config = config
        self.message = message

    def get_message_id(self) -> str:
        return str(self.message.get("id"))

    def get_email_date(self) -> str:
        headers = self.message.get("payload", {}).get("headers", [])
        date_header = next((h["value"] for h in headers if h["name"].lower() == "date"), None)
        if not date_header:
            raise ValueError(f"Email {self.get_message_id()} is missing a Date header")

        try:
            # This is the robust, RFC-compliant parser
            parsed = parsedate_to_datetime(date_header)
            return parsed.strftime("%Y-%m-%d")
        except Exception as e:
            raise ValueError(f"Failed to parse date for email {self.get_message_id()}: {e}")

    def get_filename_prefix(self) -> str:
        return f"{self.config.id}_{self.get_email_date()}"




