import os
import smtplib
from email.mime.text import MIMEText
import cloudscraper

# Credentials retrieved securely from GitHub Secrets
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL

# VFS Italy Nepal URL
VFS_URL = "https://visa.vfsglobal.com/npl/en/ita/book-an-appointment"


def send_email_alert(subject, details):
    body = f"VFS Appointment Update:\n\n{details}\n\nCheck now: {VFS_URL}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_vfs_student_slots():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        response = scraper.get(VFS_URL, timeout=30)

        if response.status_code != 200:
            print(
                f"Page fetch returned status {response.status_code}. Skipping check."
            )
            return

        page_text = response.text.lower()

        # Phrases indicating NO slots are available
        no_slot_phrases = [
            "no seats available",
            "no appointment slots available",
            "no slots available",
            "currently no open slots",
            "no dates available",
        ]

        # Target keywords for Student / Type D Visa
        student_visa_keywords = [
            "study",
            "student",
            "type d",
            "long term",
            "national visa",
        ]

        has_no_slots = any(phrase in page_text for phrase in no_slot_phrases)
        mentions_student = any(kw in page_text for kw in student_visa_keywords)

        # Check for open slots or specific appointment category updates
        if not has_no_slots and mentions_student:
            print("Student D Visa slot potentially available!")
            send_email_alert(
                "🚨 VFS Italy: Student (Type D) Visa Slot Available!",
                "VFS portal indicates available appointment slots for Study / Type D Visa.",
            )
        else:
            print(
                "No Student D Visa slots detected at this time. (No email sent)"
            )

    except Exception as e:
        print(f"Error checking VFS page: {e}")


if __name__ == "__main__":
    check_vfs_student_slots()
