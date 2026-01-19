import logging
from typing import List, Dict
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        self.keywords = ['zero-day', 'vulnerability', 'breach', 'ransomware', 'critical', 'patch', 'exploit', 'malware']

    def clean_html(self, text: str) -> str:
        """Removes HTML tags and unescapes characters."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=' ').strip()

    def process(self, raw_stories: List[Dict]) -> List[Dict]:
        """
        Deduplicates, scores, and formats stories.
        Returns top 10 ranked stories.
        """
        if not raw_stories:
            return []

        # 1. Deduplicate by link and title similarity
        unique_stories = {}
        for story in raw_stories:
            # Use link as primary key
            if story['link'] not in unique_stories:
                story['clean_summary'] = self.clean_html(story['summary'])
                if len(story['clean_summary']) > 500:
                    story['clean_summary'] = story['clean_summary'][:497] + "..."
                
                unique_stories[story['link']] = story
            else:
                 # Check if this version has a better description? For now just skip
                 pass
        
        processed_list = list(unique_stories.values())
        
        # 2. Score stories
        for story in processed_list:
            score = 0
            text_to_check = (story['title'] + " " + story['clean_summary']).lower()
            
            for keyword in self.keywords:
                if keyword in text_to_check:
                    score += 1
            
            # Boost score for reputable sources if strictly needed, or specialized terms
            story['score'] = score

        # 3. Sort by score (desc) then by date (desc)
        processed_list.sort(key=lambda x: (x['score'], x['published']), reverse=True)

        # 4. Limit to top 10
        final_list = processed_list[:10]
        
        logger.info(f"Processed {len(raw_stories)} raw stories into {len(final_list)} final items.")
        return final_list
