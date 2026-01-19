import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, RECIPIENT_EMAIL

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def send_briefing(self, stories: list):
        if not stories:
            logger.warning("No stories to email. Skipping.")
            return

        try:
            template = self.env.get_template('email_template.html')
            date_str = datetime.now().strftime('%Y-%m-%d')
            subject = f"Daily Cybersecurity & IT Briefing – {date_str}"
            
            html_content = template.render(
                date=date_str,
                stories=stories
            )

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SMTP_USER
            msg['To'] = RECIPIENT_EMAIL

            part = MIMEText(html_content, 'html')
            msg.attach(part)

            logger.info(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
