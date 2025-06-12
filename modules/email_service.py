from datetime import datetime, date
from typing import Any, List, Optional
from domain.email import Email
from domain.email_config import EmailConfig
from constants import DATE_FORMAT

def build_query(start_date: date, end_date: date) -> str:
    after_epoch = int(datetime.strptime(str(start_date), DATE_FORMAT).timestamp())
    before_epoch = int(datetime.strptime(str(end_date), DATE_FORMAT).timestamp()) + 86400
    return f"after:{after_epoch} before:{before_epoch} category:primary has:attachment"

def message_matches_filters(full_msg, email_configs: list[EmailConfig]) -> Optional[EmailConfig]:
    headers = full_msg.get('payload', {}).get('headers', [])
    from_header = next((h['value'] for h in headers if h['name'] == 'From'), '').lower()
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()

    for config in email_configs:
        if config.matches_email(from_header, subject):
            return config
    return None

def get_matching_emails(gmail_service: Any, email_configs: list[EmailConfig], start_date: date, end_date: date) -> List[Email]:
    query = build_query(start_date, end_date)

    result = gmail_service.users().messages().list(
        userId='me',
        q=query,
        labelIds=['INBOX'],
        maxResults=100
    ).execute()

    messages = result.get('messages', [])
    matched = []

    for message in messages:
        full_msg = gmail_service.users().messages().get(
            userId='me',
            id=message['id'],
            format='full'
        ).execute()

        matched_config = message_matches_filters(full_msg, email_configs)

        if matched_config:
            matched.append(Email(config=matched_config, message=full_msg))

    return matched
