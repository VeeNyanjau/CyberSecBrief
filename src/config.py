import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Application Settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

# Configure Logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

def validate_config():
    """Validates that necessary configuration is present."""
    missing = []
    if not SMTP_USER: missing.append('SMTP_USER')
    if not SMTP_PASSWORD: missing.append('SMTP_PASSWORD')
    if not RECIPIENT_EMAIL: missing.append('RECIPIENT_EMAIL')
    
    if missing:
        raise ValueError(f"Missing configuration variables: {', '.join(missing)}")
