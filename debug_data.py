import logging
import datetime
from src.collector import NewsCollector

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_collection():
    collector = NewsCollector()

    print("\n--- TEST 1: Standard 24h window ---")
    stories = collector.collect_news()
    print(f"Total stories found (24h): {len(stories)}\n")
    for s in stories:
        print(f" - {s['title']} ({s['source']}) [{s['published']}]")

    print("\n--- TEST 2: Relaxed 7-day window (Simulated) ---")
    # We can't easily override the internal variable without modifying code or subclassing, 
    # so let's just inspect the _fetch_rss method behavior by calling it manually with a different cutoff 
    
    cutoff_7days = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    
    total_found = 0
    for source in collector.sources:
        print(f"Checking {source['name']} with 7-day window...")
        try:
            if source['type'] == 'rss':
                items = collector._fetch_rss(source, cutoff_7days)
                print(f"  -> Found {len(items)} items.")
                total_found += len(items)
            elif source['type'] == 'scraper_github':
                items = collector._scrape_github(source, cutoff_7days)
                print(f"  -> Found {len(items)} items.")
                total_found += len(items)
        except Exception as e:
            print(f"  -> Error: {e}")

    print(f"\nTotal stories found (7 days): {total_found}")

if __name__ == "__main__":
    test_collection()
