import json
from modules.gmail_auth import get_gmail_service
from modules.date_window import get_next_week_window, update_state_with_end_date
from modules.email_service import get_matching_emails
from modules.email_parser_service import parse_emails
from modules.sheet_service import SheetService
from utils import load_email_configs

EMAIL_CONFIGS_PATH = 'config/email_configs.json'

def main():
    # Step 0: Get date range
    start_date, end_date = get_next_week_window()
    print(f"📅 Looking for emails from {start_date} to {end_date}")

    # Step 1: Connect to Gmail and Google Sheets
    gmail_service = get_gmail_service()
    sheet_service = SheetService()

    # Step 2: Load configs and connect to Google Sheets
    email_configs = load_email_configs(EMAIL_CONFIGS_PATH)

    # Step 3: Filter matching emails
    emails = get_matching_emails(gmail_service, email_configs, start_date, end_date)
    print(f"📬 Found {len(emails)} matching emails")

    # Step 4: Filter out emails which have already been processed
    filtered_emails = sheet_service.filter_out_already_processed_emails(emails)
    print(f"📬 Processing {len(filtered_emails)} emails after filtering")

    # Step 5: Parse matched emails into structured results
    parsed_emails = parse_emails(filtered_emails, gmail_service)
    print(f"✅ Parsed {len(parsed_emails)} emails")

    # Step 6: Write to Google Sheets
    sheet_service.write_parsed_email_to_google_sheets(parsed_emails)
    print("📤 Results written to Google Sheets")

    # Step 7: Update state
    # update_state_with_end_date(end_date)


if __name__ == '__main__':
    main()
