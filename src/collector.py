import feedparser
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        # Configuration for grouped sources
        self.sources = [
            # 0. Regional Focus: Kenya & East Africa (Highest Priority)
            {
                "name": "TechWeez",
                "url": "https://techweez.com/feed/",
                "category": "Regional Focus",
                "type": "rss"
            },
            {
                "name": "CIO Africa",
                "url": "https://cioafrica.co/feed/",
                "category": "Regional Focus",
                "type": "rss"
            },
            {
                "name": "Business Daily (Tech)",
                "url": "https://www.businessdailyafrica.com/service/rss/bdaafrica/technology/539552?x=1", # Standard Nation Media RSS pattern
                "category": "Regional Focus",
                "type": "rss"
            },
            # Kenyan Govt Bodies (via Google News RSS)
            {
                "name": "CA Kenya (News)",
                "url": "https://news.google.com/rss/search?q=Communications+Authority+of+Kenya&hl=en-KE&gl=KE&ceid=KE:en",
                "category": "Regional Focus",
                "type": "rss"
            },
            {
                "name": "KE-CIRT (News)",
                "url": "https://news.google.com/rss/search?q=KE-CIRT+OR+National+Kenya+Computer+Incident+Response+Team&hl=en-KE&gl=KE&ceid=KE:en",
                "category": "Regional Focus",
                "type": "rss"
            },
            {
                "name": "ODPC Kenya",
                "url": "https://news.google.com/rss/search?q=Office+of+the+Data+Protection+Commissioner+Kenya&hl=en-KE&gl=KE&ceid=KE:en",
                "category": "Regional Focus",
                "type": "rss"
            },
            {
                "name": "Ministry of ICT Kenya",
                "url": "https://news.google.com/rss/search?q=Ministry+of+Information+Communications+and+The+Digital+Economy+Kenya&hl=en-KE&gl=KE&ceid=KE:en",
                "category": "Regional Focus",
                "type": "rss"
            },

            # 1. Emerging Threats & Attack Patterns
            # Focus: New malware, novel phishing, zero-day exploitation patterns
            {
                "name": "Threatpost", 
                "url": "https://threatpost.com/feed/", 
                "category": "Emerging Threats & Attack Patterns", 
                "type": "rss"
            },
            {
                "name": "BleepingComputer",
                "url": "https://www.bleepingcomputer.com/feed/",
                "category": "Emerging Threats & Attack Patterns",
                "type": "rss"
            },
            
            # 2. Defensive Techniques & Blue Team Strategies
            # Focus: Detection engineering, SOC workflows, IR playbooks
            {
                "name": "Microsoft Security Blog", 
                "url": "https://www.microsoft.com/security/blog/feed/", 
                "category": "Defensive Techniques & Blue Team Strategies", 
                "type": "rss"
            },
            {
                "name": "Splunk Blog",
                "url": "https://www.splunk.com/en_us/blog/security/feed.xml",
                "category": "Defensive Techniques & Blue Team Strategies",
                "type": "rss"
            },
            {
                 "name": "SANS Internet Storm Center",
                 "url": "https://isc.sans.edu/rssfeed.xml",
                 "category": "Defensive Techniques & Blue Team Strategies",
                 "type": "rss"
            },

            # 3. Tools, Frameworks & Open-Source Spotlight
            # Focus: New tools, plugins, frameworks
            {
                "name": "GitHub Trending (Security)",
                "url": "https://github.com/topics/security?o=desc&s=updated",
                "category": "Tools, Frameworks & Open-Source Spotlight",
                "type": "scraper_github"
            },
            {
                "name": "KitPloit - PenTest Tools",
                "url": "http://feeds.feedburner.com/PentestTools",
                "category": "Tools, Frameworks & Open-Source Spotlight",
                "type": "rss"
            },

            # 4. Academic Research & Papers
            # Focus: Theory into practice, summaries of papers
            {
                "name": "arXiv (Security)",
                "url": "http://export.arxiv.org/rss/cs.CR",
                "category": "Academic Research & Papers",
                "type": "rss"
            },
            {
                "name": "IEEE Spectrum (Cyber)",
                "url": "https://spectrum.ieee.org/feeds/topic/cybersecurity",
                "category": "Academic Research & Papers",
                "type": "rss"
            },

            # 5. Vulnerabilities & Exploit Analysis
            # Focus: CVE trends, exploit chains, misconfigurations
            {
                "name": "Exploit-DB",
                "url": "https://www.exploit-db.com/rss.xml",
                "category": "Vulnerabilities & Exploit Analysis",
                "type": "rss"
            },
            {
                "name": "Packet Storm",
                "url": "https://packetstormsecurity.com/feeds/files/",
                "category": "Vulnerabilities & Exploit Analysis",
                "type": "rss"
            },
            
            # 6. Security Failures & Postmortems
            # Focus: Breach analyses, incident timelines, lessons learned
            # Note: Often covered in general news, but reliable breach trackers help
            {
                "name": "The Record (Recorded Future)",
                "url": "https://therecord.media/feed/",
                "category": "Security Failures & Postmortems",
                "type": "rss"
            },
            {
                "name": "Dark Reading (Attacks & Breaches)", 
                "url": "https://www.darkreading.com/rss/attacks-breaches",
                "category": "Security Failures & Postmortems",
                "type": "rss"
            },

            # 7. Ethics, Law & Policy in Cybersecurity
            # Focus: Cyber laws, privacy debates, ethical boundaries
            {
                "name": "EFF Updates",
                "url": "https://www.eff.org/rss/updates.xml",
                "category": "Ethics, Law & Policy in Cybersecurity",
                "type": "rss"
            },
            {
                "name": "Lawfare Blog (Cyber)",
                "url": "https://www.lawfareblog.com/taxonomy/term/65/feed", # Cyber law specific tag if available, else main
                "category": "Ethics, Law & Policy in Cybersecurity",
                "type": "rss"
            },
            {
                "name": "Krebs on Security", # Often covers law/policy/crime
                "url": "https://krebsonsecurity.com/feed/",
                "category": "Ethics, Law & Policy in Cybersecurity",
                "type": "rss"
            },

            # 8. AI, Automation & Cybersecurity
            # Focus: AI offense/defense, LLM risks
            {
                "name": "Schneier on Security", # Often discusses AI/Crypto implications
                "url": "https://www.schneier.com/feed/atom/",
                "category": "AI, Automation & Cybersecurity",
                "type": "rss"
            },
            # AI specific feeds are rare, will rely on keywords from general feeds too

            # 9. Sector-Specific Security & Regional
            # Focus: Healthcare, Finance, Local context
            {
                "name": "Dark Reading (Risk)",
                "url": "https://www.darkreading.com/rss/risk-management",
                "category": "Sector-Specific Security",
                "type": "rss"
            },
             {
                "name": "SecurityWeek (Cybercrime)",
                "url": "https://feeds.feedburner.com/securityweek",
                "category": "Sector-Specific Security", # Will need keyword filtering to be accurate
                "type": "rss"
            }
        ]

    def collect_news(self) -> List[Dict]:
        """
        Fetches news from all configured sources for the last 24 hours.
        Returns a list of dictionaries with keys: 'title', 'link', 'summary', 'published', 'source', 'category'.
        """
        collected_stories = []
        # Use timezone-aware UTC for comparison
        # Extended to 48 hours to ensure content availability
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=48)
        
        for source in self.sources:
            try:
                logger.info(f"Fetching news from: {source['name']} ({source['url']})")
                
                if source['type'] == 'rss':
                    stories = self._fetch_rss(source, cutoff_time)
                    collected_stories.extend(stories)
                elif source['type'] == 'scraper_github':
                    stories = self._scrape_github(source, cutoff_time)
                    collected_stories.extend(stories)
                        
            except Exception as e:
                logger.error(f"Failed to fetch from {source['name']}: {e}")

        logger.info(f"Collected {len(collected_stories)} stories from last 24 hours.")
        return collected_stories

    def _fetch_rss(self, source: Dict, cutoff_time: datetime) -> List[Dict]:
        stories = []
        # Reddit specific headers to avoid 429
        headers = {}
        if 'reddit.com' in source['url']:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            
        # For Reddit, we might need to use requests to get proper content if feedparser fails on UA
        # But try standard feedparser first with modified agent if possible, or just let feedparser handle it.
        # Feedparser allows 'agent' argument? older versions maybe.
        # Safest is to download with requests if needed, but for now standard feedparser:
        
        feed = feedparser.parse(source['url'], request_headers=headers)
        
        if feed.bozo and not feed.entries: # Only skip if truly broken and no entries
            logger.warning(f"Error parsing feed {source['url']}: {feed.bozo_exception}")
            return []

        for entry in feed.entries:
            published_time = self._parse_time(entry)

            if published_time and published_time > cutoff_time:
                summary_text = getattr(entry, 'summary', '')
                if not summary_text:
                    summary_text = getattr(entry, 'description', 'No summary available.')

                stories.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': summary_text,
                    'published': published_time,
                    'source': source['name'],
                    'category': source['category']
                })
        return stories

    def _scrape_github(self, source: Dict, cutoff_time: datetime) -> List[Dict]:
        stories = []
        try:
            resp = requests.get(source['url'], headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                logger.warning(f"GitHub fetch failed: {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for article tags which usually hold repo info in topics view
            repos = soup.find_all('article', class_='border rounded-2 box-shadow-bg-gray-mktg my-4')
            
            # If the structure changed, try standard repo list
            if not repos:
                 repos = soup.find_all('div', class_='d-flex flex-justify-between flex-items-start flex-wrap gap-2 my-3')

            # Fallback to just parsing headers if specific classes fail - GitHub changes often.
            # Let's try to match the 'topics' page structure as of late 2024/2025
            # Usually: h3 with f3 class containing link
            
            repo_links = soup.select("h3.f3 a.Link") # Selector for repo name
            
            count = 0
            for link in repo_links:
                if count >= 5: break # Limit
                
                href = link.get('href')
                full_link = f"https://github.com{href}"
                title = link.text.strip().replace("\n", "").replace(" ", "")
                
                # Description often in the following p tag
                # We need to find the parent or next sibling
                # This is heuristic
                description = "New security tool or resource on GitHub."
                parent_div = link.find_parent('div') or link.find_parent('h3').find_parent('div')
                if parent_div:
                    desc_tag = parent_div.find_next_sibling('p')
                    if desc_tag:
                         description = desc_tag.text.strip()

                # For scraping, hard to determine exact time, so we assume it's 'fresh' if it's on top of updated list
                # We assign current time to ensure it's included
                published_time = datetime.now(timezone.utc)

                stories.append({
                    'title': f"{title}",
                    'link': full_link,
                    'summary': description,
                    'published': published_time,
                    'source': source['name'],
                    'category': source['category']
                })
                count += 1
                
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
            
        return stories

    def _parse_time(self, entry) -> datetime:
        """Helper to parse feed times into timezone-aware UTC datetime."""
        dt = None
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                dt = datetime.fromtimestamp(time.mktime(entry.updated_parsed), timezone.utc)
            elif hasattr(entry, 'published'): # sometimes plain string
                 # minimal effort parse, strict formats usually work with feedparser
                 pass
        except Exception:
            pass
        
        # If no timezone info, assume utc for comparison or make aware
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        return dt
