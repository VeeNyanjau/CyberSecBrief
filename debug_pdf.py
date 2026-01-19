import sys
import logging
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
import io
import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_pdf_gen():
    try:
        # Load template
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_template.html')
        
        # Dummy data
        stories = {
            'Emerging Threats & Attack Patterns': [
                {'title': 'Test Story 1', 'link': 'http://example.com', 'source': 'Test Source', 'published': datetime.datetime.now(), 'clean_summary': 'This is a test summary.'}
            ]
        }
        
        html_content = template.render(date="2026-01-20", stories=stories)
        
        # specific debugging for xhtml2pdf
        pdf_buffer = io.BytesIO()
        
        logger.info("Starting pisa.CreatePDF...")
        pisa_status = pisa.CreatePDF(
            src=html_content,    # Expects string
            dest=pdf_buffer,
            encoding='utf-8'     # Explicit encoding
        )
        
        if pisa_status.err:
            logger.error(f"PISA returned error code: {pisa_status.err}")
        else:
            logger.info(f"Success! PDF size: {len(pdf_buffer.getvalue())} bytes")
            
    except Exception as e:
        logger.exception("Exception during PDF generation details:")

if __name__ == "__main__":
    test_pdf_gen()
