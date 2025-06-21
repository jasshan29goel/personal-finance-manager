import json
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from domain.email_config import EmailConfig
from domain.parsed_email import ParsedEmail
from constants import EMAIL_CONFIGS

def getStartEndDate(year, month):
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1)
    return start_date.date(), end_date.date()

def load_email_configs(path: str) -> list[EmailConfig]:
    with open(path, 'r') as f:
        raw_accounts = json.load(f)[EMAIL_CONFIGS]
    email_configs = [EmailConfig.from_dict(account) for account in raw_accounts]
    filtered_configs = [config for config in email_configs if config.run]
    return sorted(filtered_configs, key=lambda email_config: email_config.id)

def write_strings_to_file(strings, filename):
    separator = "=" * 50 + "\n"

    with open(filename, "a", encoding="utf-8") as f:
        for i, s in enumerate(strings):
            f.write(str(s) + "\n")
            f.write(separator)

# This would run once after generating the ParsedEmail list
def save_parsed_emails_to_disk(parsed_emails: List[ParsedEmail], path: str):
    with open(path, "w", encoding="utf-8") as f:
        data = [email.model_dump() for email in parsed_emails]
        import json
        json.dump(data, f, indent=2)


def load_parsed_emails_from_disk(path: str) -> List[ParsedEmail]:
    from domain.parsed_email import ParsedEmail
    import json

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [ParsedEmail(**item) for item in data]

def log_and_collect(message: str, log_store: list[str]):
    print(message)
    log_store.append(message)