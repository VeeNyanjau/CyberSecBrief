import logging
import sys
import os
import io
from typing import Dict, List

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collector import NewsCollector
from src.processor import ContentProcessor

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('verify_run')

class MockInsightGenerator:
    def analyze_story(self, story: Dict, region: str = "Global") -> Dict:
        return {
            'significance': 'High',
            'why_it_matters': 'This is a mocked impact statement for verification.',
            'who_should_care': 'ISPs, Banks, Government',
            'action': 'Patch immediateley and review logs.',
            'kenya_context': 'Specific context for Kenya would appear here.' if region == 'Kenya' else ''
        }
    
    def generate_briefing_insight(self, all_stories: Dict) -> Dict:
        return {
            'executive_summary': 'This is a mocked executive summary.',
            'signals': [{'title': 'Mock Signal', 'description': 'Mock description.'}]
        }

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

        # 2. Process & Enrich Content
        logger.info("Processing and Categorizing News (with AI insights if enabled)...")
        processor = ContentProcessor()
        
        # Monkeypatch for verification if API key is missing
        if not processor.insight_gen.enabled:
            logger.warning("InsightGenerator disabled (no API key). Using Mock for verification.")
            processor.insight_gen = MockInsightGenerator()
            
        # process() now returns a tuple: (stories, insights)
        categorized_stories, insights = processor.process(raw_stories)
        
        # Log results
        # Log results
        logger.info(f"--- Top {len(categorized_stories)} Stories ---")
        for i, item in enumerate(categorized_stories):
            title = item.get('title', 'No Title')
            region = item.get('region', 'Global')
            score = item.get('score', 0)
            sig = item.get('significance', 'N/A')
            why = item.get('why_it_matters', 'N/A')
            who = item.get('who_should_care', 'N/A')
            action = item.get('action', 'N/A')
            context = item.get('kenya_context', '')
            
            logger.info(f"   [ {i+1} ] [{region}] [{sig}] {title} - Score: {score}")
            if why: logger.info(f"       -> Why: {why}")
            if who: logger.info(f"       -> Who: {who}")
            if action: logger.info(f"       -> Action: {action}")
            if context: logger.info(f"       -> 🇰🇪 Context: {context}")
        
        # Log Executive Summary availability
        if insights and insights.get('executive_summary'):
             logger.info("Executive Summary generated.")
        else:
             logger.info("No Executive Summary (API Key missing or disabled).")

        # 3. Verify PDF Generation
        try:
            from src.emailer import EmailService
            logger.info("Testing PDF Generation (Professional Report)...")
            emailer = EmailService()
            # Explicitly test the report template rendering
            report_template = emailer.env.get_template('report_template.html')
            date_str = "2024-01-01" # Dummy date
            
            pdf_html = report_template.render(
                date=date_str, 
                stories=categorized_stories, 
                insights=insights
            )
            
            pdf_bytes = emailer.create_pdf(pdf_html)
            if pdf_bytes:
                 logger.info(f"Professional PDF successfully generated ({len(pdf_bytes)} bytes). Saving to verify_output.pdf")
                 with open("verify_output.pdf", "wb") as f:
                     f.write(pdf_bytes)
            else:
                 logger.error("PDF generation returned None.")
        except ImportError:
            logger.error("xhtml2pdf not installed or accessible.")
        except Exception as e:
            logger.error(f"PDF Verification failed: {e}")

        logger.info("Verification completed.")

    except Exception as e:
        logger.critical(f"Critical failure: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
