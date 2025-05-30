import tiktoken
import json
from domain.email_config import EmailConfig

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Returns the number of tokens in the input text for a given OpenAI model.

    Args:
        text (str): The input string to count tokens for.
        model (str): The name of the OpenAI model (e.g., 'gpt-4', 'gpt-3.5-turbo').

    Returns:
        int: The number of tokens in the input text.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def load_email_configs(path: str) -> list[EmailConfig]:
    with open(path, 'r') as f:
        raw_accounts = json.load(f)['email_configs']
    email_configs = [EmailConfig.from_dict(account) for account in raw_accounts]
    return [config for config in email_configs if config.run]