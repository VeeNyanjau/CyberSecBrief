import logging
import sys
import os

# Add project root to python path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_config
from src.collector import NewsCollector
from src.processor import ContentProcessor
from src.emailer import EmailService

# Configure logger for main script
logger = logging.getLogger('main')

def main():
    try:
        # 1. Validate Configuration
        logger.info("Starting CyberSec Daily Brief...")
        validate_config()

        # 2. Collect News
        collector = NewsCollector()
        raw_stories = collector.collect_news()
        
        if not raw_stories:
            logger.warning("No stories found in the last 24 hours. Exiting.")
            return

        # 3. Process and Rank
        processor = ContentProcessor()
        top_stories = processor.process(raw_stories)
        
        if not top_stories:
            logger.warning("No stories remained after processing. Exiting.")
            return

        # 4. Send Email
        emailer = EmailService()
        emailer.send_briefing(top_stories)
        
        logger.info("Daily briefing completed successfully.")

    except Exception as e:
        logger.critical(f"Critical failure: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
