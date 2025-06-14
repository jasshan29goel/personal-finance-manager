from typing import List, Any
from domain.email import Email
from domain.parsed_email import ParsedEmail
from modules.attachment_service import save_unlocked_attachment_pdf
from modules.field_parser.extractor import extract_from_pdf
from modules.field_parser.processor import process_field
from modules.field_parser.field_parser_utils import post_validate

def parse_emails(emails: List[Email], gmail_service: Any, execution_id: str) -> List[ParsedEmail]:
    parsed_emails: List[ParsedEmail] = []

    for email in sorted(emails):
        try:
            field_outputs = {}
            script_message = ""
            for field_name, field_config in email.config.field_parsers.items():
                # Step 1: Get the input text/table
                if field_config.type == "pdf_attachment":
                    pdf_path = save_unlocked_attachment_pdf(email, gmail_service)
                    extracted_content = extract_from_pdf(field_config.pdf_extractor, pdf_path)
                    result, message = process_field(field_config.processor, field_name, extracted_content)
                    post_validate(field_name, result, pdf_path)
                    field_outputs[field_name] = result
                    script_message += f"\n field: {field_name} message: {message}"
                else:
                    raise ValueError(f"Unsupported source: {field_config.type}")

            parsed_emails.append(
                ParsedEmail(
                    execution_id=execution_id,
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    **field_outputs,
                    status="success",
                    script_message=script_message
                )
            )

        except Exception as e:
            parsed_emails.append(
                ParsedEmail(
                    execution_id=execution_id,
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    status="failed",
                    script_message=str(e)
                )
            )

    return parsed_emails
