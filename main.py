import uuid
from datetime import datetime
from modules.gmail_auth import get_gmail_service
from modules.date_window import get_window_from_month, update_state_with_next_month
from modules.email_service import get_matching_emails
from modules.email_parser_service import parse_emails
from modules.sheet_service import SheetService
from modules.post_processor import PostProcessor
from utils import load_email_configs, log_and_collect
from constants import EMAIL_CONFIGS_PATH, DATE_FORMAT

class EmailParsingPipeline:
    def __init__(self):
        # Step 0: Set up execution window and ID
        self.start_date, self.end_date = get_window_from_month()
        self.execution_id = str(uuid.uuid4())
        print(f"📅 Looking for emails from {self.start_date} to {self.end_date}")
        print(f"🔁 Execution ID: {self.execution_id}")

        # Step 1: Set up services
        self.gmail_service = get_gmail_service()
        print("✅ Gmail Service initialized")
        self.sheet_service = SheetService()
        print("✅ Google Sheets Service initialized")

        # Step 2: Load config
        self.email_configs = load_email_configs(EMAIL_CONFIGS_PATH)
        print(f"✅ Email Configs loaded: {len(self.email_configs)}")

        # Step 3: Load post-processing rules
        self.post_processor = PostProcessor(self.sheet_service.load_category_rules())
        print(f"✅ Post processor rules loaded: {len(self.post_processor.rules)}")

    def execute(self):
        log_store = []
        # Step 4: Find and filter emails
        emails = get_matching_emails(self.gmail_service, self.email_configs, self.start_date, self.end_date)
        log_and_collect(f"📬 Found {len(emails)} matching emails", log_store)

        filtered_emails = self.sheet_service.filter_out_already_processed_emails(emails)
        log_and_collect(f"📬 Processing {len(filtered_emails)} emails after filtering", log_store)

        # Step 5: Parse emails
        parsed_emails = parse_emails(filtered_emails, self.gmail_service, execution_id=self.execution_id)
        log_and_collect(f"✅ Parsed {len(parsed_emails)} emails", log_store)

        # Step 6: Post-process
        post_processed = self.post_processor.process_all(parsed_emails)

        # Step 7: Write to Google Sheets
        self.sheet_service.write_all_outputs(post_processed, log_store)
        log_and_collect("📤 Results written to Google Sheets", log_store)

        # Step 8: Write execution log
        date_run = datetime.now().strftime(DATE_FORMAT)
        self.sheet_service.write_execution_log(
            execution_id=self.execution_id,
            date_run=date_run,
            start_date=self.start_date.strftime(DATE_FORMAT),
            end_date=self.end_date.strftime(DATE_FORMAT),
            total_emails=len(emails),
            filtered_emails=len(filtered_emails),
            log="\n".join(log_store)
        )
        # Optional state update
        # update_state_with_next_month(self.start_date)

if __name__ == '__main__':
    pipeline = EmailParsingPipeline()
    pipeline.execute()
