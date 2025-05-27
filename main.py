from modules.gmail_auth import get_gmail_service
from modules.date_window import get_next_week_window, update_state_with_end_date
from modules.email_filter import fetch_filtered_emails
from modules.pdf_unlocker import extract_pdf_attachments
from modules.pdf_parser import extract_transactions_from_pdf
from modules.sheets_writer import connect_to_sheet, append_transactions_from_parsed_pdfs

import os

OUTPUT_DIR = 'output_pdfs'

def get_unlocked_pdfs():
    return [
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith('.pdf')
    ]

"""
Step 0: get date range. 
Step 1: Conenct to gmail services.
Step 2: Filter mails based on filter config.
Step 3: get attachements of filtered mails and save the unlocked files in the directory. 

Step Last: update the date range, in state once processing is done.
"""
def main():
    start_date, end_date = get_next_week_window()
    print(f"Looking for emails from {start_date} to {end_date}")
    service = get_gmail_service()
    matched_emails = fetch_filtered_emails(service, start_date, end_date)
    extract_pdf_attachments(service, matched_emails)

    unlocked_pdfs_path = get_unlocked_pdfs()

    parsed_results = []
    for pdf in unlocked_pdfs_path:
        parsed = extract_transactions_from_pdf(pdf, False)
        parsed_results.append(parsed)

    sheet = connect_to_sheet()
    append_transactions_from_parsed_pdfs(sheet, parsed_results)

    #update_state_with_end_date(end_date)

if __name__ == '__main__':
    main()



