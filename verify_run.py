import logging
import sys
import os
import io

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collector import NewsCollector
from src.processor import ContentProcessor

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('verify_run')

def main():
    try:
        logger.info("Starting Verification Run...")

        # 1. Collect News
        collector = NewsCollector()
        logger.info("Collector initialized. Fetching news...")
        # For verification, we might want to just fetch specifically or all.
        # But to be fast, maybe we can mock? No, better to test real connections.
        raw_stories = collector.collect_news()
        
        if not raw_stories:
            logger.warning("No stories found.")
        else:
            logger.info(f"Collected {len(raw_stories)} raw stories.")
            # Print sample raw story
            logger.info(f"Sample Raw: {raw_stories[0]['title']} from {raw_stories[0]['source']} (Cat: {raw_stories[0].get('category')})")

        # 2. Process and Rank
        processor = ContentProcessor()
        top_stories = processor.process(raw_stories)
        
        if not top_stories:
            logger.warning("No stories remained after processing.")
        else:
            logger.info("Processing complete. Categorized Results:")
            for category, stories in top_stories.items():
                logger.info(f"--- {category} ({len(stories)}) ---")
                for story in stories:
                    logger.info(f"   [ {story['score']} ] {story['title']} ({story['source']})")

        logger.info("Verification completed.")

    except Exception as e:
        logger.critical(f"Critical failure: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
