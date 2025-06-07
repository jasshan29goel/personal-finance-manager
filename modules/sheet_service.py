import gspread
from google.oauth2.service_account import Credentials
from typing import List
from domain.email import Email
from domain.parsed_email import ParsedEmail
from domain.category_rule import CategoryRule

SERVICE_ACCOUNT_FILE = 'creds/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1sjJ0ip3VW6tHsqLpWHafgVf9SjXM60ccYjMC-gI8M6c'

class SheetService:
    def __init__(self):
        try:
            credentials = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=SCOPES
            )
            client = gspread.authorize(credentials)

            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            self.transaction_sheet = spreadsheet.worksheet('transactions')
            self.status_sheet = spreadsheet.worksheet('status')
            self.category_rules = spreadsheet.worksheet('category_rules')

        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to Google Sheets: {e}")


    def filter_out_already_processed_emails(self, emails: List[Email]) -> List[Email]:
        try:
            existing_records = self.status_sheet.get_all_values()
            processed_ids = {row[0] for row in existing_records[1:] if row}  # skip header
        except Exception as e:
            raise RuntimeError(f"❌ Failed to read from status sheet: {e}")

        return [email for email in emails if email.get_message_id() not in processed_ids]

    def write_parsed_email_to_google_sheets(self, parsed_emails: List[ParsedEmail]):
        transaction_rows: List[List[str]] = []
        status_rows: List[List[str]] = []

        for email in parsed_emails:
            if email.transactions:
                for txn in email.transactions:
                    transaction_rows.append([email.message_id, email.account_id] + txn.to_row())

            status_rows.append([
                email.message_id,
                email.account_id,
                email.email_date,
                email.status,
                str(email.total_amount_due),
                str(email.closing_balance),
                email.script_message or "",
            ])

        print(f"✅ Writing {len(transaction_rows)} transactions")

        if transaction_rows:
            self.transaction_sheet.append_rows(transaction_rows, value_input_option="USER_ENTERED")  # type: ignore

        print(f"✅ Writing {len(status_rows)} statuses")

        if status_rows:
            self.status_sheet.append_rows(status_rows, value_input_option="USER_ENTERED")  # type: ignore

    def load_category_rules(self) -> List[CategoryRule]:
        try:
            rows = self.category_rules.get_all_records()
            rules = [CategoryRule.from_sheet_row(row) for row in rows]
            return sorted(rules, key=lambda r: r.priority)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load category rules: {e}")
