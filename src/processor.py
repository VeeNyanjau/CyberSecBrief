import logging
from typing import List, Dict
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        # Specific keywords could be used for extra scoring if needed
        self.keywords = ['zero-day', 'vulnerability', 'breach', 'ransomware', 'critical', 'patch', 'exploit', 'malware']

    def clean_html(self, text: str) -> str:
        """Removes HTML tags and unescapes characters."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=' ').strip()

    def process(self, raw_stories: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Deduplicates, scores, and categorizes stories.
        Returns a dictionary: { 'Category Name': [stories] }
        Limits total stories to under 10 (approx 2-3 per category).
        """
        if not raw_stories:
            return {}

        # 1. Deduplicate globally by link
        unique_stories = {}
        for story in raw_stories:
            if story['link'] not in unique_stories:
                story['clean_summary'] = self.clean_html(story['summary'])
                if len(story['clean_summary']) > 500:
                    story['clean_summary'] = story['clean_summary'][:497] + "..."
                unique_stories[story['link']] = story
        
        # 2. Group by Category
        categorized = {
            "Trending Vulnerabilities": [],
            "Research & Project Ideas": [],
            "Industry Trends": [],
            "Open-Source Tools": []
        }

        for story in unique_stories.values():
            cat = story.get('category', 'Industry Trends') # Default fallback
            if cat in categorized:
                categorized[cat].append(story)
            else:
                categorized['Industry Trends'].append(story)

        # 3. Score and Sort within Categories
        final_output = {}
        
        # Define limits per category to keep total < 10
        # Total = 3 + 2 + 2 + 2 = 9
        limits = {
            "Trending Vulnerabilities": 3,
            "Research & Project Ideas": 2,
            "Industry Trends": 2,
            "Open-Source Tools": 2
        }

        for category, stories in categorized.items():
            # Score
            for story in stories:
                score = 0
                text_to_check = (story['title'] + " " + story['clean_summary']).lower()
                for keyword in self.keywords:
                    if keyword in text_to_check:
                        score += 1
                story['score'] = score
            
            # Sort by score (desc) then date (desc)
            stories.sort(key=lambda x: (x['score'], x['published']), reverse=True)
            
            # Apply limit
            limit = limits.get(category, 2)
            final_output[category] = stories[:limit]

        # Calculate total
        total_count = sum(len(v) for v in final_output.values())
        logger.info(f"Processed into {total_count} final items across {len(final_output)} categories.")
        
        return final_output
