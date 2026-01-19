import smtplib
import logging
import os
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import Dict, List
from xhtml2pdf import pisa
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, RECIPIENT_EMAIL

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def create_pdf(self, html_content: str) -> bytes:
        """Converts HTML content to PDF bytes."""
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
        if pisa_status.err:
            logger.error(f"PDF generation error: {pisa_status.err}")
            return None
        return pdf_buffer.getvalue()

    def send_briefing(self, stories: Dict[str, List[Dict]], insights: Dict = None) -> None:
        """Generates the HTML briefing and sends it via email with PDF attachment."""
        try:
            # Load both templates
            email_template = self.env.get_template('email_template.html')
            report_template = self.env.get_template('report_template.html')
            
            date_str = datetime.now().strftime('%Y-%m-%d')
            subject = f"Daily Cybersecurity & IT Briefing – {date_str}"
            
            # Default empty insights if None
            if not insights:
                insights = {'executive_summary': '', 'signals': []}

            # Render Email Body (HTML optimized for email clients)
            email_html = email_template.render(
                date=date_str,
                stories=stories,
                insights=insights
            )
            
            # Render PDF Content (HTML optimized for printing/PDF)
            pdf_html = report_template.render(
                date=date_str,
                stories=stories,
                insights=insights
            )

            msg = MIMEMultipart('mixed') # Changed to mixed to support attachments
            msg['Subject'] = subject
            msg['From'] = SMTP_USER
            msg['To'] = RECIPIENT_EMAIL

            # Create the body (alternative part for HTML/Text)
            msg_body = MIMEMultipart('alternative')
            part_html = MIMEText(email_html, 'html')
            msg_body.attach(part_html)
            msg.attach(msg_body)

            # Generate and attach PDF using separate template
            logger.info("Generating PDF report...")
            pdf_bytes = self.create_pdf(pdf_html)
            if pdf_bytes:
                pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"CyberSecBrief_{date_str}.pdf")
                msg.attach(pdf_attachment)
                logger.info("PDF report attached successfully.")
            else:
                logger.warning("Failed to generate PDF, sending email without attachment.")

            logger.info(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
