from modules.gmail_auth import get_gmail_service
from modules.date_window import get_window_from_month, update_state_with_next_month
from modules.email_service import get_matching_emails
from modules.email_parser_service import parse_emails
from modules.sheet_service import SheetService
from modules.post_processor import PostProcessor
from utils import load_email_configs, save_parsed_emails_to_disk, load_parsed_emails_from_disk
from modules.validator import validate_parsed_emails
from pprint import pprint

EMAIL_CONFIGS_PATH = 'config/email_configs.json'
SAVED_PARSED_EMAILS_PATH = 'parsed_email_dump.json'

def main():
    # Step 0: Get date range
    start_date, end_date = get_window_from_month()
    print(f"📅 Looking for emails from {start_date} to {end_date}")

    # Step 1: Connect to Gmail and Google Sheets
    gmail_service = get_gmail_service()
    sheet_service = SheetService()

    # Step 2: Load configs for email matching and categories
    email_configs = load_email_configs(EMAIL_CONFIGS_PATH)
    post_processor = PostProcessor(sheet_service.load_category_rules())
    print(len(post_processor.rules))

    # Step 3: Filter matching emails
    emails = get_matching_emails(gmail_service, email_configs, start_date, end_date)
    print(f"📬 Found {len(emails)} matching emails")

    # # Step 4: Filter out emails which have already been processed
    filtered_emails = sheet_service.filter_out_already_processed_emails(emails)
    print(f"📬 Processing {len(filtered_emails)} emails after filtering")

    # Step 5: Parse matched emails into structured results
    parsed_emails = parse_emails(filtered_emails, gmail_service)
    print(f"✅ Parsed {len(parsed_emails)} emails")

    save_parsed_emails_to_disk(parsed_emails, SAVED_PARSED_EMAILS_PATH)

    parsed_emails_from_disk = load_parsed_emails_from_disk(SAVED_PARSED_EMAILS_PATH)

    # Step 6: Do post processing on the structured parsed_emails output.
    post_processed_parsed_emails = post_processor.process_all(parsed_emails_from_disk)

    mismatches = validate_parsed_emails("evals/expected_response.json", parsed_emails)

    if mismatches:
        print("❌ Mismatches found:")
        pprint(mismatches)
    else:
        print("✅ All transactions match!")
        # Step 7: Write to Google Sheets
    sheet_service.write_parsed_email_to_google_sheets(post_processed_parsed_emails)
    print("📤 Results written to Google Sheets")

    # Step 7: Update state
    # update_state_with_next_month(start_date)


if __name__ == '__main__':
    main()
