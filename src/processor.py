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
        self.insight_gen = InsightGenerator()

    def clean_html(self, text: str) -> str:
        """Removes HTML tags and unescapes characters."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=' ').strip()

    def process(self, raw_stories: List[Dict]) -> Tuple[Dict[str, List[Dict]], Dict]:
        """
        Deduplicates, scores, categorizes, AND enriches stories.
        Returns:
            1. Categorized stories dict
            2. Briefing insights dict (Executive Summary, Signals)
        """
        if not raw_stories:
            raw_stories = []

        # 1. Deduplicate globally by link
        unique_stories = {}
        for story in raw_stories:
            if story['link'] not in unique_stories:
                story['clean_summary'] = self.clean_html(story['summary'])
                # Truncate summary
                if len(story['clean_summary']) > 400: # Slightly shorter for 9 cats
                    story['clean_summary'] = story['clean_summary'][:397] + "..."
                unique_stories[story['link']] = story
        
        # 2. Initialize Categories
        categories = [
            "Emerging Threats & Attack Patterns",
            "Defensive Techniques & Blue Team Strategies",
            "Tools, Frameworks & Open-Source Spotlight",
            "Academic Research & Papers",
            "Vulnerabilities & Exploit Analysis",
            "Security Failures & Postmortems",
            "Ethics, Law & Policy in Cybersecurity",
            "AI, Automation & Cybersecurity",
            "Sector-Specific Security"
        ]
        
        categorized = {cat: [] for cat in categories}

        # 3. Assign Stories
        for story in unique_stories.values():
            cat = story.get('category')
            # Fallback if category invalid or missing
            if cat not in categorized:
                # Basic keyword fallback could go here, for now default to Emerging Threats
                cat = "Emerging Threats & Attack Patterns"
            
            categorized[cat].append(story)

        # 4. Score and Sort within Categories
        final_output = {}
        
        # Limit strictly to 2 per category to keep digest readable (9*2 = 18 max)
        LIMIT_PER_CATEGORY = 2

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
            final_output[category] = stories[:LIMIT_PER_CATEGORY]

        # 5. GENERATE INSIGHTS (Enrichment)
        logger.info("Generating AI Insights for stories...")
        for cat, stories in final_output.items():
            for story in stories:
                analysis = self.insight_gen.analyze_story(story)
                story['why_it_matters'] = analysis.get('why_it_matters', '')
                story['research_tag'] = analysis.get('research_tag', 'General') # For future grouping

        # Generate Report-Level Insights
        logger.info("Generating Executive Briefing Insights...")
        report_insights = self.insight_gen.generate_briefing_insight(final_output)

        # Calculate total
        total_count = sum(len(v) for v in final_output.values())
        logger.info(f"Processed into {total_count} final items across {len(final_output)} categories.")
        
        return final_output, report_insights
