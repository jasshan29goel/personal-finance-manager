import gspread
from google.oauth2.service_account import Credentials
from typing import List
from utils import log_and_collect
from domain.email import Email
from domain.parsed_email import ParsedEmail
from domain.category_rule import CategoryRule
from constants import SHEETS_SERVICE_ACCOUNT_FILE, SHEETS_SCOPES, SHEETS_SPREADSHEET_ID


class SheetService:
    def __init__(self):
        try:
            credentials = Credentials.from_service_account_file(
                SHEETS_SERVICE_ACCOUNT_FILE,
                scopes=SHEETS_SCOPES
            )
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

            self.transaction_sheet = spreadsheet.worksheet('transactions')
            self.status_sheet = spreadsheet.worksheet('status')
            self.balances_sheet = spreadsheet.worksheet('balances')
            self.execution_log_sheet = spreadsheet.worksheet('execution_log')
            self.category_rules_sheet = spreadsheet.worksheet('category_rules')

        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to Google Sheets: {e}")

    def load_category_rules(self) -> List[CategoryRule]:
        try:
            rows = self.category_rules_sheet.get_all_records()
            rules = [CategoryRule.from_sheet_row(row) for row in rows]
            return sorted(rules, key=lambda r: r.priority)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load category rules: {e}")

    def filter_out_already_processed_emails(self, emails: List[Email]) -> List[Email]:
        try:
            existing_records = self.status_sheet.get_all_values()
            processed_ids = {row[1] for row in existing_records[1:] if row}  # Column 1 = message_id
        except Exception as e:
            raise RuntimeError(f"❌ Failed to read from status sheet: {e}")

        return [email for email in emails if email.get_message_id() not in processed_ids]

    def write_transactions(self, parsed_emails: List[ParsedEmail], log_store: List[str]):
        transaction_rows: List[List[str]] = []

        for email in parsed_emails:
            if email.transactions:
                for txn in email.transactions:
                    row = [
                        email.execution_id,
                        email.message_id,
                        email.account_id,
                    ] + txn.to_row()
                    transaction_rows.append(row)

        log_and_collect(f"✅ Writing {len(transaction_rows)} transactions", log_store)

        if transaction_rows:
            self.transaction_sheet.append_rows(transaction_rows, value_input_option="USER_ENTERED")  # type: ignore

    def write_balances(self, parsed_emails: List[ParsedEmail], log_store: List[str]):
        balance_rows: List[List[str]] = []

        for email in parsed_emails:
            if email.total_amount_due is not None or email.closing_balance is not None:
                row = [
                    email.execution_id,
                    email.message_id,
                    email.account_id,
                    email.email_date,
                    str(email.closing_balance) if email.closing_balance is not None else "",
                    str(email.total_amount_due) if email.total_amount_due is not None else "",
                ]
                balance_rows.append(row)

        log_and_collect(f"✅ Writing {len(balance_rows)} balances", log_store)

        if balance_rows:
            self.balances_sheet.append_rows(balance_rows, value_input_option="USER_ENTERED")  # type: ignore

    def write_status(self, parsed_emails: List[ParsedEmail], log_store: List[str]):
        status_rows: List[List[str]] = []

        for email in parsed_emails:
            row = [
                email.execution_id,
                email.message_id,
                email.account_id,
                email.email_date,
                email.status,
                email.script_message or "",
            ]
            status_rows.append(row)

        log_and_collect(f"✅ Writing {len(status_rows)} statuses", log_store)

        if status_rows:
            self.status_sheet.append_rows(status_rows, value_input_option="USER_ENTERED")  # type: ignore

    def write_execution_log(
        self,
        execution_id: str,
        date_run: str,
        start_date: str,
        end_date: str,
        total_emails: int,
        filtered_emails: int,
        log: str
    ):
        row = [
            execution_id,
            date_run,
            start_date, 
            end_date,
            str(total_emails),
            str(filtered_emails),
            log,
        ]

        print(f"✅ Logging execution run {execution_id}")
        self.execution_log_sheet.append_row(row, value_input_option="USER_ENTERED")  # type: ignore

    def write_all_outputs(self, parsed_emails: List[ParsedEmail], log_store: List[str]):
        self.write_transactions(parsed_emails, log_store)
        self.write_balances(parsed_emails, log_store)
        self.write_status(parsed_emails, log_store)

