from domain.parsed_pdf import ParsedPDF
from domain.transaction import Transaction
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = 'creds/service_account.json'
SPREADSHEET_NAME = '1sjJ0ip3VW6tHsqLpWHafgVf9SjXM60ccYjMC-gI8M6c'
SHEET_NAME = 'Sheet1'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def connect_to_sheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, SCOPES
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

def append_transactions_from_parsed_pdfs(sheet, parsed_pdfs: list[ParsedPDF]):
    all_transactions: list[Transaction] = []

    for parsed in parsed_pdfs:
        all_transactions.extend(parsed.transactions)
    
    rows = [t.to_row() for t in all_transactions]
    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"✅ Appended {len(rows)} transactions to sheet.")
    else:
        print("ℹ️ No transactions to upload.")
