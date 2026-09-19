import smtplib
from email.mime.text import MIMEText
import cloudscraper

# --- CONFIGURATION ---
SENDER_EMAIL = "laxmanchaulagain1154@gmail.com"
APP_PASSWORD = "kwju kyub rxnl fmxh"  # Or retrieved via os.environ for GitHub Actions
RECEIVER_EMAIL = "laxmanchaulagain1154@gmail.com"
VFS_URL = "https://visa.vfsglobal.com/npl/en/ita/application-detail"


def send_email_alert(slot_info):
    subject = "🚨 VFS VISA SLOT AVAILABLE!"
    body = f"An appointment slot is available:\n\n{slot_info}\n\nLog in immediately to book!"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_vfs():
    scraper = cloudscraper.create_scraper()
    response = scraper.get(VFS_URL)

    if response.status_code == 200:
        page_text = response.text.lower()

        # Define phrases that indicate NO slots
        no_slot_keywords = [
            "no seats available",
            "no appointment slots available",
            "no slots available",
            "currently no open slots",
        ]

        # Check if any "no slot" phrase exists on the page
        has_no_slots = any(keyword in page_text for keyword in no_slot_keywords)

        if not has_no_slots:
            # If the "no slot" text is missing, an appointment might be open!
            print("Slot detected! Sending email...")
            send_email_alert("An appointment slot appears to be available on VFS!")
        else:
            print("No slots available at this time. (No email sent)")
    else:
        print(f"Failed to fetch VFS page. Status code: {response.status_code}")


if __name__ == "__main__":
    check_vfs()