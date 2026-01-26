import logging
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
import re
from src.insights import InsightGenerator

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        # 1. IMPACT INDICATORS (+15 points)
        # Focus: Active exploitation, critical urgency, confirmed incidents
        self.impact_keywords = [
            'exploited in the wild', 'active exploitation', 'critical vulnerability', 
            'zero-day', 'cve-', 'cvss 9', 'cvss 10', 'ransomware attack', 
            'data breach', 'confirmed incident', 'patch now', 'under attack'
        ]

        # 2. PRIORITY TOPICS (+5 points)
        # Focus: Strategic relevance, policy, regulation
        self.priority_topics = [
            'policy', 'regulation', 'act', 'bill', 'sim swap', 
            'cyber incident', 'compliance', 'directive'
        ]
        
        # 3. NOISE / FLUFF FILTERS (-50 points)
        # Focus: Exclude non-actionable content
        self.noise_keywords = [
            'top 10', 'best of', 'awards', 'ranking', 'opinion:', 'editorial:', 
            'thought leadership', 'prediction', 'market report', 'vendor showcase'
        ]

        # 4. POLITICS FILTER (-50 points unless technical)
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
            pass # Continue to refine specific country
            
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
        """Calculates score based on Region, Impact, and Relevance."""
        score = 0
        text_lower = text.lower()

        # 1. Region Score (Reduced Bias)
        if region == "Kenya":
            score += 5   # Was 10
        elif region == "East Africa":
            score += 3   # Was 5
        else:
            score += 0 # Global

        # 2. Impact Bonus (High Weight)
        for kw in self.impact_keywords:
            if kw in text_lower:
                score += 15
                break # Cap at one major boost to avoid inflation

        # 3. Topic Bonus
        for pt in self.priority_topics:
            if pt in text_lower:
                score += 5
                
        # 4. Noise / Politics Filter (Heavy Penalty)
        is_political = any(pk in text_lower for pk in self.politics_keywords)
        has_tech_context = any(tc in text_lower for tc in self.tech_context)
        is_noise = any(nk in text_lower for nk in self.noise_keywords)
        
        if is_noise:
            score -= 50
        
        if is_political and not has_tech_context:
            score -= 50

        return score

    def process(self, raw_stories: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicates, scores, classifies, AND enriches stories.
        Returns Top 6-8 Stories List.
        """
        if not raw_stories:
            raw_stories = []

        # 1. Deduplicate globally by link
        unique_stories = {}
        for story in raw_stories:
            if story['link'] not in unique_stories:
                story['clean_summary'] = self.clean_html(story['summary'])
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
            
            # Threshold: exclude distinct noise
            if score > -10: 
                processed_stories.append(story)

        # 3. Sort: Score (Desc), Date (Desc)
        processed_stories.sort(key=lambda x: (x['score'], x['published']), reverse=True)

        # 4. Selection Logic (Limits & Caps)
        final_selection = []
        academic_count = 0
        emerging_count = 0
        
        for story in processed_stories:
            if len(final_selection) >= 8: # Hard Cap at 8
                break

            # Academic Limit: Max 1
            if story.get('category') == 'Academic Research & Papers':
                if academic_count >= 1:
                    continue
                academic_count += 1

            # Emerging Tech Limit: Max 2
            if story.get('category') == 'Emerging Technologies':
                if emerging_count >= 2:
                    continue
                emerging_count += 1
            
            final_selection.append(story)

        # 5. GENERATE INSIGHTS (Enrichment)
        logger.info(f"Generating AI Insights for {len(final_selection)} selected stories...")
        for story in final_selection:
            analysis = self.insight_gen.analyze_story(story, region=story.get('region', 'Global'))
            story['significance'] = analysis.get('significance', 'Medium')
            story['why_it_matters'] = analysis.get('why_it_matters', '')
            story['who_should_care'] = analysis.get('who_should_care', '')
            story['action'] = analysis.get('action', '')
            story['kenya_context'] = analysis.get('kenya_context', '')

        # Generate Report-Level Insights
        logger.info("Generating Executive Briefing Insights...")
        report_context = {"Top Stories": final_selection}
        report_insights = self.insight_gen.generate_briefing_insight(report_context)

        total_count = len(final_selection)
        logger.info(f"Processed into {total_count} final top stories.")
        
        return final_selection, report_insights
