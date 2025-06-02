from typing import List, Any
from domain.email import Email
from domain.parsed_email import ParsedEmail
from modules.attachment_service import save_unlocked_attachment_pdf
from modules.extract_from_pdf import apply_extraction
from modules.content_processor_service import process_field
from utils import write_strings_to_file, count_tokens

def parse_emails(emails: List[Email], gmail_service: Any) -> List[ParsedEmail]:
    parsed_emails: List[ParsedEmail] = []

    for email in sorted(emails):
        try:
            field_outputs = {}
            confidences = []
            for field_name, field_config in email.config.field_parsers.items():
                # Step 1: Get the input text/table
                if field_config.source == "attachment":
                    pdf_path = save_unlocked_attachment_pdf(email, gmail_service) 
                    extracted_content = apply_extraction(field_config, pdf_path)
                else:
                    raise ValueError(f"Unsupported source: {field_config.source}")

                # Step 2: Process the chunk
                # print(str(extracted_content))
                # print(count_tokens(str(extracted_content)))
                # write_strings_to_file(extracted_content, 'output.txt')
                result, confidence = process_field(field_name, extracted_content, field_config.processor)
                confidences.append(confidence)
                field_outputs[field_name] = result

            final_confidence = sum(confidences)/len(confidences)
            parsed_emails.append(
                ParsedEmail(
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    confidence=final_confidence,
                    **field_outputs,
                    status="success"
                )
            )

        except Exception as e:
            parsed_emails.append(
                ParsedEmail(
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    confidence=0,
                    status="failed",
                    error_message=str(e)
                )
            )

    return parsed_emails
