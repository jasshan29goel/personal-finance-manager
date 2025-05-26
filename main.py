from modules.gmail_auth import get_gmail_service

def main():
    # Step 1: Connect to Gmail
    service = get_gmail_service()

    # Step 2: Fetch and display basic email info (placeholder for next module)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    print("Recent email subjects:")
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        print(f"- {subject}")

if __name__ == '__main__':
    main()
