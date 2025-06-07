import os
import json
from typing import Any, List, Literal
from datetime import datetime
import openai
from dotenv import load_dotenv
import tiktoken

from domain.transaction import Transaction
from domain.field_parser.field_processors.base_processor_config import BaseProcessorConfig

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

JSONL_EVAL_PATH = "evals/current.jsonl"

today_str = datetime.now().strftime("%Y-%m-%d")

SYSTEM_MESSAGE = (
    "You extract structured transaction data from bank or credit card statements. "
    "The data was extracted using pdfplumber. Return a JSON object matching the provided schema. "
    "Do not guess missing or unclear values. Amounts must be greater than zero. "
    "Dates must be in YYYY-MM-DD format and must not be in the future. "
    "If any field is ambiguous or incomplete, exclude the transaction and reduce the overall confidence accordingly. "
    "Assume today's date is {today}."
).format(today=today_str)

TRANSACTION_SCHEMA = {
    "type": "object",
    "required": ["transactions", "confidence"],
    "properties": {
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "date",
                    "amount",
                    "txn_type",
                    "note",
                    "reason"
                ],
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Transaction date in YYYY-MM-DD format"
                    },
                    "note": {
                        "type": "string",
                        "description": "Narration or description of the transaction"
                    },
                    "amount": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Transaction amount"
                    },
                    "txn_type": {
                        "type": "string",
                        "enum": ["CREDIT", "DEBIT"],
                        "description": "Type of transaction: CREDIT or DEBIT"
                    },
                    "reason": {
                        "type": "string",
                        "description": "For the given output explain why you choose the given amount date note and transaction type."
                    },
                },
                "additionalProperties": False
            }
        },
        "confidence": {
            "type": "number",
            "description": "value from 0 - 1 to indicate your confidence in the parsing of the entire query and its accuracy."
        }
    },
    "additionalProperties": False
}

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

class TransactionsProcessorUsingLLMConfig(BaseProcessorConfig):
    type: Literal['llm']
    model: str = "gpt-4.1-mini"

    def process_field(self, field_name: str, extracted_content: Any) -> tuple[List[Transaction], str]:
        if field_name != "transactions":
            raise ValueError(f"{self.__class__.__name__} only supports 'transactions' field")

        input_query = str(extracted_content)
        print(input_query)

        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_MESSAGE}]
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": input_query}]
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "transaction_response",
                    "schema": TRANSACTION_SCHEMA,
                    "strict": True
                }
            },
            reasoning={},
            tools=[],
            temperature=0.01,
            max_output_tokens=16384,
            top_p=1,
            store=True
        )

        try:
            parsed = json.loads(response.output_text)
            append_eval_jsonl(SYSTEM_MESSAGE, input_query, response.output_text, JSONL_EVAL_PATH)
            transactions =  [
                Transaction(
                    date=txn["date"],
                    amount=txn["amount"],
                    note=txn["note"],
                    txn_type=txn["txn_type"],
                    reason=txn["reason"],
                    category="MISC"
                )
                for txn in parsed["transactions"]
            ]
            confidence = parsed["confidence"]
            llm_message = f"Extracting transactions via LLM. Confidence: {confidence}"
            
            print(f"📤 Running {self.model} responses api for {count_tokens(input_query)} input tokens")
            print(f"📤 Running {self.model} responses api for {count_tokens(response.output_text)} output tokens")

            return transactions, llm_message
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse LLM response: {e}")