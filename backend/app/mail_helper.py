import smtplib
from email.mime.text import MIMEText
from flask import current_app


def send_mfa_email(to_email, code):
    subject = "Your Momentum MFA Code"
    body = f"""
Your Momentum verification code is: {code}

Enter this code to complete your login.
If you did not request this, you can ignore this email.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_FROM"]
    msg["To"] = to_email

    server = smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"]
    )
    server.starttls()
    server.login(
        current_app.config["MAIL_USERNAME"],
        current_app.config["MAIL_PASSWORD"]
    )
    server.send_message(msg)
    server.quit()