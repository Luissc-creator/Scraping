import imaplib
import email
import re

# Email account credentials
EMAIL = "clydemaxinelegaspi654@gmail.com"  # Replace with your email
PASSWORD = "truetiger"      # Replace with your email password
IMAP_SERVER = "imap.gmail.com"  # Correct IMAP server for Outlook

def fetch_latest_verification_code():
    mail = None
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        
        # Select the inbox
        mail.select("inbox")
        
        # Search for emails from a specific sender
        result, data = mail.search(None, '(FROM "noreply@telecompaper.com")')
        if result != "OK" or not data[0]:
            print("No emails found!")
            return None
        
        # Get the IDs of all matching emails
        email_ids = data[0].split()
        
        # Check if email_ids is empty
        if not email_ids:
            print("No matching emails found.")
            return None
        
        # Fetch the most recent email (latest one)
        latest_email_id = email_ids[-1]
        result, message_data = mail.fetch(latest_email_id, "(RFC822)")
        
        if result != "OK":
            print("Error fetching the latest email.")
            return None
        
        # Parse the email content
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Extract the email body
        email_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    email_body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            email_body = msg.get_payload(decode=True).decode(errors='ignore')
        
        # Use regex to extract the verification code (5-digit number)
        verification_code = re.search(r'\b\d{5}\b', email_body)
        
        if verification_code:
            print("Verification Code:", verification_code.group())
            return verification_code.group()
        else:
            print("No verification code found in the latest email.")
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None

    finally:
        # Logout and close the connection if mail exists
        if mail:
            try:
                mail.logout()
            except:
                pass

# Fetch and print the latest verification code
if __name__ == "__main__":
    code = fetch_latest_verification_code()
    if code:
        print(f"The latest verification code is: {code}")
    else:
        print("No verification code could be extracted.")
