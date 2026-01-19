import feedparser
import logging
from datetime import datetime, timedelta
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.sources = [
            "https://feeds.feedburner.com/TheHackersNews", # The Hacker News
            "https://www.bleepingcomputer.com/feed/", # BleepingComputer
            "https://krebsonsecurity.com/feed/", # Krebs on Security
            "https://www.darkreading.com/rss.xml", # Dark Reading
            "https://feeds.feedburner.com/securityweek", # SecurityWeek
            "https://www.wired.com/feed/category/security/latest/rss", # Wired Security
            "https://arstechnica.com/tag/security/feed/", # Ars Technica Security
            "https://www.zdnet.com/topic/security/rss.xml" # ZDNet Security
        ]
        # Alternative/Backup URLs in case some change
        self.backup_sources = {} 

    def collect_news(self) -> List[Dict]:
        """
        Fetches news from all configured sources for the last 24 hours.
        Returns a list of dictionaries with keys: 'title', 'link', 'summary', 'published', 'source'.
        """
        collected_stories = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for url in self.sources:
            try:
                logger.info(f"Fetching news from: {url}")
                feed = feedparser.parse(url)
                
                if feed.bozo:
                    logger.warning(f"Error parsing feed {url}: {feed.bozo_exception}")
                    continue

                for entry in feed.entries:
                    # Parse published time
                    published_time = None
                    if hasattr(entry, 'published_parsed'):
                         published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    elif hasattr(entry, 'updated_parsed'):
                        published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                    
                    if published_time and published_time > cutoff_time:
                        # Normalize summary - some feeds use 'summary', others 'description'
                        summary_text = getattr(entry, 'summary', '')
                        if not summary_text:
                            summary_text = getattr(entry, 'description', 'No summary available.')

                        collected_stories.append({
                            'title': entry.title,
                            'link': entry.link,
                            'summary': summary_text,
                            'published': published_time,
                            'source': feed.feed.get('title', 'Unknown Source')
                        })
                        
            except Exception as e:
                logger.error(f"Failed to fetch from {url}: {e}")

        logger.info(f"Collected {len(collected_stories)} stories from last 24 hours.")
        return collected_stories
