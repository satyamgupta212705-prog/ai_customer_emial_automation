import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scope determines what the script is allowed to do (read, send, and modify drafts)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticates the agency's Gmail account if credentials exist."""
    creds = None
    
    # 1. Check if the user has already logged in previously (token.json exists)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # 2. If no valid credentials, try to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # THIS IS THE PLUG-AND-PLAY CHECK:
            if not os.path.exists('credentials.json'):
                print("\n⚠️ [SYSTEM HALT] Live Email Connection Disabled.")
                print("Missing 'credentials.json'. To activate live email, the agency must place their Google Cloud credentials in this folder.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run so they don't have to log in every time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("\n✅ [SUCCESS] Securely connected to Live Gmail Inbox.")
        return service
    except HttpError as error:
        print(f'\n❌ [ERROR] An error occurred connecting to Gmail: {error}')
        return None

def fetch_unread_emails(service):
    """Fetches unread emails from the inbox."""
    if not service:
        return []
        
    try:
        # Ask Gmail for messages that are unread
        results = service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])
        inbox = []
        
        for msg in messages:
            # Fetch the full email data
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data['payload']['headers']
            
            # Extract basic info safely
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
            body = msg_data.get('snippet', '') # Snippet is the clean, plain-text preview of the email!
            
            inbox.append({
                'id': msg['id'],
                'sender': sender,
                'subject': subject,
                'body': body
            })
            
        return inbox
    except HttpError as error:
        print(f'❌ [ERROR] An error occurred fetching emails: {error}')
        return []

def create_draft(service, sender_email, subject, reply_body):
    """Saves the AI-generated reply as a Draft in the Gmail inbox for human review."""
    if not service:
        return
        
    try:
        message = EmailMessage()
        message.set_content(reply_body)
        message['To'] = sender_email
        message['Subject'] = f"Re: {subject}"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'message': {'raw': encoded_message}}
        
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        print(f"📧 [GMAIL] Draft successfully saved in inbox! (Draft ID: {draft['id']})")
        
    except HttpError as error:
        print(f'❌ [ERROR] An error occurred creating the draft: {error}')

if __name__ == "__main__":
    # Test the plug-and-play logic
    print("Testing Live Email Connector...")
    service = authenticate_gmail()