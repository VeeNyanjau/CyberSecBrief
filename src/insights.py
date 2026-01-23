import os
import logging
import google.generativeai as genai
from typing import List, Dict

logger = logging.getLogger(__name__)

class InsightGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.enabled = False
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.enabled = True
                logger.info("InsightGenerator initialized with Gemini API.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
                self.enabled = False
        else:
            logger.warning("GOOGLE_API_KEY not found. Insights will be skipped.")

    def _generate_text(self, prompt: str) -> str:
        if not self.enabled:
            return ""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return ""

    def analyze_story(self, story: Dict, region: str = "Global") -> Dict:
        """
        Generates deep intelligence analysis for a single story.
        Returns a dict with 'why_it_matters', 'significance', 'who_should_care', 'action', and 'kenya_context' (if applicable).
        """
        if not self.enabled:
            return {}

        title = story.get('title', '')
        summary = story.get('clean_summary', '')
        category = story.get('category', '')
        
        # Build prompt conditions
        kenya_instruction = ""
        if region == "Kenya":
            kenya_instruction = "Task 5: Write a 'Kenya Context' section (1 sentence). Explicitly relate this to Kenya's national policy, local infrastructure, data protection laws (ODPC), or public sector systems."

        prompt = f"""
        Analyze this cybersecurity news item:
        Title: {title}
        Summary: {summary}
        Category: {category}
        Region: {region}

        Perform the following intelligence tasks:
        Task 1: Assign a 'Significance Level' (Low / Medium / High / Critical).
        Task 2: Write a 'Why This Matters' analysis (1 sentence). Explain the real-world impact.
        Task 3: Identify 'Who Should Care' (comma-separated list, e.g., ISPs, Banks, SMEs, Regulators).
        Task 4: Recommend a 'Practical Action' (1 short sentence). Practical guidance for the target audience.
        {kenya_instruction}
        
        Constraint: If Category is 'Academic Research & Papers', ensure the 'Practical Action' is a concrete takeaway, not abstract theory.

        Output format:
        Significance: [Level]
        Why: [Text]
        Who: [List]
        Action: [Text]
        Context: [Text (only if requested)]
        """
        
        response_text = self._generate_text(prompt)
        
        result = {
            'significance': 'Medium', 
            'why_it_matters': '', 
            'who_should_care': '', 
            'action': '',
            'kenya_context': ''
        }
        
        # Parsing
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('Significance:'):
                result['significance'] = line.replace('Significance:', '').strip()
            elif line.startswith('Why:'):
                result['why_it_matters'] = line.replace('Why:', '').strip()
            elif line.startswith('Who:'):
                result['who_should_care'] = line.replace('Who:', '').strip()
            elif line.startswith('Action:'):
                result['action'] = line.replace('Action:', '').strip()
            elif line.startswith('Context:'):
                result['kenya_context'] = line.replace('Context:', '').strip()
                
        return result

    def generate_briefing_insight(self, all_stories: Dict[str, List[Dict]]) -> Dict:
        """
        Generates an Executive Summary and Signals/Patterns based on all top stories.
        """
        if not self.enabled:
            return {'executive_summary': '', 'signals': []}

        # Prepare a condensed input context
        context_lines = []
        for cat, stories in all_stories.items():
            if stories:
                context_lines.append(f"Category: {cat}")
                for s in stories:
                    context_lines.append(f"- {s.get('title', '')}")

        context = "\n".join(context_lines)

        prompt = f"""
        Based on the following cybersecurity news briefing digest:
        {context}

        Task 1: Write an 'Executive Insight Summary' (approx 150-200 words). Highlight key emerging themes, repeated threat patterns, or notable shifts.
        Task 2: Identify 3 distinct 'Signals & Patterns' (cross-category trends). For each, provide a short Title and Description.

        Output format:
        SUMMARY:
        [Summary text]

        SIGNAL 1: [Title] - [Description]
        SIGNAL 2: [Title] - [Description]
        SIGNAL 3: [Title] - [Description]
        """

        response_text = self._generate_text(prompt)
        
        insights = {
            'executive_summary': '',
            'signals': []
        }
        
        # Parsing state machine-ish
        current_section = None
        summary_lines = []
        
        for line in response_text.split('\n'):
            line = line.strip()
            if not line: continue
            
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                continue
            elif line.startswith('SIGNAL'):
                current_section = 'signal'
                # Parse Signal line: SIGNAL 1: Title - Description
                parts = line.split(':', 1)
                if len(parts) > 1:
                    content = parts[1].strip()
                    # Split title/desc if possible
                    if ' - ' in content:
                        t, d = content.split(' - ', 1)
                        insights['signals'].append({'title': t, 'description': d})
                    else:
                        insights['signals'].append({'title': 'Trend', 'description': content})
                continue
            
            if current_section == 'summary':
                summary_lines.append(line)
        
        insights['executive_summary'] = " ".join(summary_lines)
        return insights
