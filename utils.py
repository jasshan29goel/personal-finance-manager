import tiktoken
import json
from domain.email_config import EmailConfig
from typing import List

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
    filtered_configs = [config for config in email_configs if config.run]
    return sorted(filtered_configs, key=lambda email_config: email_config.id)

def append_eval_jsonl(system_message: str, query, ideal, filepath: str):
    """
    Appends a row to a JSONL file for OpenAI evals.

    Parameters:
        system_message (str): The system prompt.
        query (Any): The user query (can be any JSON-serializable type).
        ideal (Any): The expected output (can be any JSON-serializable type).
        filepath (str): The path to the JSONL file.
    """
    entry = {
        "input": {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ]
        },
        "ideal": ideal
    }

    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n" + json.dumps(entry, ensure_ascii=False))


def write_strings_to_file(strings, filename):
    separator = "=" * 50 + "\n"

    with open(filename, "a", encoding="utf-8") as f:
        for i, s in enumerate(strings):
            f.write(str(s) + "\n")
            f.write(separator)
