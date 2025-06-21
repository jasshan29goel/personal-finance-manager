from datetime import datetime, date
from typing import Any, List, Optional
from domain.email import Email
from domain.email_config import EmailConfig
from constants import DATE_FORMAT

def build_query(start_date: date, end_date: date, email_configs: List[EmailConfig]) -> str:
    after_epoch = int(datetime.strptime(str(start_date), DATE_FORMAT).timestamp())
    before_epoch = int(datetime.strptime(str(end_date), DATE_FORMAT).timestamp())
    # Collect all from addresses from enabled configs
    from_filters = set()
    for config in email_configs:
        if config.run:
            from_filters.update(config.from_addresses)

    query_parts = [f"after:{after_epoch}", f"before:{before_epoch}"]
    if from_filters:
        query_parts.append(f"({' OR '.join(f'from:{addr}' for addr in from_filters)})")

    return " ".join(query_parts)

def message_matches_filters(full_msg, email_configs: List[EmailConfig]) -> Optional[EmailConfig]:
    headers = full_msg.get('payload', {}).get('headers', [])
    from_header = next((h['value'] for h in headers if h['name'] == 'From'), '').lower()
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()

    for config in email_configs:
        if config.matches_email(from_header, subject):
            return config
    return None

def get_matching_emails(gmail_service: Any, email_configs: List[EmailConfig], start_date: date, end_date: date) -> List[Email]:
    query = build_query(start_date, end_date, email_configs)
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
