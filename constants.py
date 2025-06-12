from typing import Literal

# properties based on paths.
EMAIL_CONFIGS_PATH = 'config/email_configs.json'
PDF_OUTPUT_DIRECTORY = 'output_pdfs'
STATE_FILE = 'state/state.json'
PDF_PASSWORDS_PATH = 'creds/pdf_passwords.json'
JSONL_EVAL_PATH = "evals/current.jsonl"

# GMAIL constants
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_CREDENTIALS_PATH = 'creds/credentials.json'
GMAIL_TOKEN_PATH = 'creds/token.json'

# Google Sheets constants
SHEETS_SERVICE_ACCOUNT_FILE = 'creds/service_account.json'
SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEETS_SPREADSHEET_ID = '1sjJ0ip3VW6tHsqLpWHafgVf9SjXM60ccYjMC-gI8M6c'

# constants which there should be no need to change
OPEN_AI_API_KEY = 'OPEN_AI_API_KEY'
MONTH_TO_RUN_FIELD = 'month_to_run'
EMAIL_CONFIGS = 'email_configs'
MONTH_FORMAT = '%Y-%m'
DATE_FORMAT = '%Y-%m-%d'

# ENUMS
CategoryType = Literal[
    "REVENUE",
    "LIVING",
    "TRAVEL",
    "FUN",
    "SHOPPING",
    "INVESTMENT",
    "SELF",
    "MISC",
]

TransactionType = Literal[
    "CREDIT", 
    "DEBIT"
]