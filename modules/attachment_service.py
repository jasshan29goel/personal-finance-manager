import os
import base64
import tempfile
import pikepdf
from typing import Any
from domain.email import Email
from modules.password_lookup import get_pdf_password

OUTPUT_DIR = 'output_pdfs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_unlocked_attachment_pdf(email: Email, service: Any) -> str:
    message = email.message
    account_id = email.config.id
    filename = email.get_filename_prefix() + ".pdf"
    unlocked_path = os.path.join(OUTPUT_DIR, filename)

    # Step 1: Check if already saved
    if os.path.exists(unlocked_path):
        return unlocked_path

    # Step 2: Find first .pdf part
    parts = message.get("payload", {}).get("parts", [])
    pdf_part = next((p for p in parts if p.get("filename", "").lower().endswith(".pdf")), None)
    if not pdf_part:
        raise ValueError(f"No PDF attachment found for email {email.get_message_id()}")

    attachment_id = pdf_part.get("body", {}).get("attachmentId")
    if not attachment_id:
        raise ValueError(f"No attachment ID found for email {email.get_message_id()}")

    att = service.users().messages().attachments().get(
        userId="me",
        messageId=message["id"],
        id=attachment_id
    ).execute()

    data = base64.urlsafe_b64decode(att["data"].encode("UTF-8"))

    # Step 3: Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(data)
        temp_pdf_path = temp_pdf.name

    # Step 4: Determine unlock path
    password = get_pdf_password(account_id)

    try:
        if password:
            # Unlock the PDF using password
            with pikepdf.open(temp_pdf_path, password=password) as pdf:
                pdf.save(unlocked_path)
        else:
            # Assume it's already unlocked
            with pikepdf.open(temp_pdf_path) as pdf:
                pdf.save(unlocked_path)

        os.remove(temp_pdf_path)
        return unlocked_path

    except Exception as e:
        os.remove(temp_pdf_path)
        raise ValueError(f"Failed to process PDF for {account_id}: {e}")
