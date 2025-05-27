import json
from datetime import datetime
from googleapiclient.discovery import Resource
from domain.account_config import AccountConfig
from domain.matched_email import MatchedEmail


DATE_FORMAT = '%Y-%m-%d'
FILTER_CONFIG_PATH = 'config/filters.json'


def load_filters():
    with open('config/filters.json', 'r') as f:
        raw_accounts = json.load(f)['accounts']
    return [AccountConfig.from_dict(account) for account in raw_accounts]



def build_query(start_date, end_date):
    # Gmail API query uses epoch seconds
    after_epoch = int(datetime.strptime(str(start_date), DATE_FORMAT).timestamp())
    before_epoch = int(datetime.strptime(str(end_date), DATE_FORMAT).timestamp()) + 86400  # include full end date
    return f"after:{after_epoch} before:{before_epoch} category:primary has:attachment"

def message_matches_filters(full_msg, filters):
    headers = full_msg.get('payload', {}).get('headers', [])
    from_header = next((h['value'] for h in headers if h['name'] == 'From'), '').lower()
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()

    for account in filters:
        if account.matches_email(from_header, subject):
            return account
    return None

def fetch_filtered_emails(service: Resource, start_date, end_date):
    filters = load_filters()
    query = build_query(start_date, end_date)

    # Only fetch messages from Primary inbox
    result = service.users().messages().list(
        userId='me',
        q=query,
        labelIds=['INBOX'],
        maxResults=100
    ).execute()

    messages = result.get('messages', [])
    matched = []
    for message in messages:
        full_msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='full'
        ).execute()

        matched_account = message_matches_filters(full_msg, filters)

        if matched_account:
            matched.append(MatchedEmail(account=matched_account, message=full_msg))


    return matched
