import os
import csv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 1. Load the email credentials from the .env file
load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

if not sender_email or not email_password:
    print("Error: Missing email credentials in .env file.")
    exit()

# 2. Calculate the target date (Today + 2 days)
today = datetime.now()
target_date = today + timedelta(days=2)
target_date_str = target_date.strftime("%Y-%m-%d")

print(f"Today is: {today.strftime('%Y-%m-%d')}")
print(f"Looking for deadlines exactly on: {target_date_str}")

# 3. Read the Database and find matches
csv_file = "deadlines_database.csv"
reminders_to_send = []

try:
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if the row's deadline matches our target date
            if row["Deadline Date"] == target_date_str:
                reminders_to_send.append(row)
except FileNotFoundError:
    print("No database found yet. Run the Streamlit app first.")
    exit()

# 4. Send the Emails if matches are found
if not reminders_to_send:
    print("No deadlines approaching in exactly 2 days. No emails sent.")
else:
    print(f"Found {len(reminders_to_send)} approaching deadline(s). Sending email...")
    
    # Connect to Gmail's server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(sender_email, email_password)
        
        # Draft and send an email for each matching deadline
        for reminder in reminders_to_send:
            subject = f"URGENT: NCLT Deadline in 2 Days - {reminder['Case File']}"
            body = f"""
            Hello,
            
            This is an automated reminder from your NCLT Tracker.
            
            A deadline is approaching in exactly 2 days:
            
            Case File: {reminder['Case File']}
            Event: {reminder['Event']}
            Deadline Date: {reminder['Deadline Date']}
            
            Please take the necessary action.
            """
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            print(f"Email sent successfully for event: {reminder['Event']}")
            
        server.quit()
        
    except Exception as e:
        print(f"Failed to send email: {e}")