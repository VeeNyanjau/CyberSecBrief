import logging
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
import re
from src.insights import InsightGenerator

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        # Specific keywords could be used for extra scoring if needed
        self.keywords = ['zero-day', 'vulnerability', 'breach', 'ransomware', 'critical', 'patch', 'exploit', 'malware']
        
        # New: Tracking keywords for high priority topics
        self.priority_topics = ['policy', 'regulation', 'act', 'bill', 'sim swap', 'cyber incident', 'data breach', 'attack']
        
        # New: Politics filter (exclude if these exist without tech context)
        self.politics_keywords = ['politics', 'election', 'party', 'campaign', 'vote']
        self.tech_context = ['cyber', 'tech', 'internet', 'digital', 'audit', 'data', 'online', 'social media', 'ict']

        self.insight_gen = InsightGenerator()

    def clean_html(self, text: str) -> str:
        """Removes HTML tags and unescapes characters."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=' ').strip()

    def _determine_region(self, story: Dict, text: str) -> str:
        """Determines if story is Kenya, East Africa, or Global."""
        # Check source category first
        if story.get('category') == 'Regional Focus':
            # Assume implicit Kenya/East Africa if from our specific regional sources
            # We can refine further if needed, but for now High Priority Regional is safest.
            # But let's try to distinguish Kenya vs just EA
            pass
            
        text_lower = text.lower()
        kenya_terms = ['kenya', 'nairobi', 'cak', 'communications authority', 'odpc', 'ruto', 'ministry of ict', 'ke-cirt', 'konza', 'safaricom', 'airtel kenya']
        ea_terms = ['uganda', 'tanzania', 'rwanda', 'east africa', 'ethiopia', 'somalia', 'burundi', 'drc']

        for term in kenya_terms:
            if term in text_lower:
                return "Kenya"
        
        for term in ea_terms:
            if term in text_lower:
                return "East Africa"
                
        # If explicitly from a known Kenyan source but no keywords, still Kenya
        known_kenya_sources = ['TechWeez', 'CIO Africa', 'Business Daily (Tech)', 'CA Kenya (News)', 'KE-CIRT (News)', 'ODPC Kenya', 'Ministry of ICT Kenya']
        if story.get('source') in known_kenya_sources:
             return "Kenya"

        return "Global"

    def _calculate_score(self, story: Dict, text: str, region: str) -> int:
        """Calculates score based on Region, Topic, and Keywords."""
        score = 0
        text_lower = text.lower()

        # 1. Region Score
        if region == "Kenya":
            score += 10
        elif region == "East Africa":
            score += 5
        else:
            score += 0 # Global

        # 2. Topic/Keyword Bonus
        for kw in self.keywords:
            if kw in text_lower:
                score += 1
        
        for pt in self.priority_topics:
            if pt in text_lower:
                score += 5

        # 3. Politics Filter / Penalty
        is_political = any(pk in text_lower for pk in self.politics_keywords)
        has_tech_context = any(tc in text_lower for tc in self.tech_context)
        
        if is_political and not has_tech_context:
            score -= 50 # Heavy penalty to effectively exclude

        return score

    def process(self, raw_stories: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicates, scores, classifies, AND enriches stories.
        Returns:
            1. Top 10 Stories List (Flat)
            2. Briefing insights dict
        """
        if not raw_stories:
            raw_stories = []

        # 1. Deduplicate globally by link
        unique_stories = {}
        for story in raw_stories:
            if story['link'] not in unique_stories:
                story['clean_summary'] = self.clean_html(story['summary'])
                # Truncate summary
                if len(story['clean_summary']) > 400:
                    story['clean_summary'] = story['clean_summary'][:397] + "..."
                unique_stories[story['link']] = story
        
        processed_stories = []

        # 2. Score and Tag
        for story in unique_stories.values():
            full_text = (story['title'] + " " + story['clean_summary'])
            
            # Determine Region
            region = self._determine_region(story, full_text)
            story['region'] = region
            
            # Calculate Score
            score = self._calculate_score(story, full_text, region)
            story['score'] = score
            
            # Only keep positive scores (filters out heavy negative political noise)
            if score > -10: 
                processed_stories.append(story)

        # 3. Sort: Score (Desc), Date (Desc)
        processed_stories.sort(key=lambda x: (x['score'], x['published']), reverse=True)

        # 4. Limit to Top 10 Total
        top_10_stories = processed_stories[:10]

        # 5. GENERATE INSIGHTS (Enrichment)
        logger.info("Generating AI Insights for Top 10 stories...")
        for story in top_10_stories:
            analysis = self.insight_gen.analyze_story(story)
            story['why_it_matters'] = analysis.get('why_it_matters', '')
            story['research_tag'] = analysis.get('research_tag', 'General')

        # Generate Report-Level Insights (Adapted for flat list)
        logger.info("Generating Executive Briefing Insights for Top 10...")
        # Mock categorization for the prompt context to keep insights structure working if needed
        # Or just pass the flat list if updated in insights.py. 
        # The insights.py expects Dict[str, List]. Let's adapt it briefly here or update insights.py?
        # Let's check insights.py. It iterates items(). 
        # Adapting key here for compatibility:
        report_context = {"Top Stories": top_10_stories}
        report_insights = self.insight_gen.generate_briefing_insight(report_context)

        total_count = len(top_10_stories)
        logger.info(f"Processed into {total_count} final top stories.")
        
        return top_10_stories, report_insights
