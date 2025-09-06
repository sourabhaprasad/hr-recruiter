import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from core.db import get_db
from core.models import Candidate, JD, MatchResult, BiasAlert, DiversityMetrics

class AIAssistant:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def get_dashboard_context(self, db: Session, jd_id: Optional[int] = None) -> Dict:
        """Get current dashboard data as context for AI"""
        context = {}
        
        # Get candidates and matches
        if jd_id:
            matches = db.query(MatchResult).filter(MatchResult.jd_id == jd_id).all()
            jd = db.query(JD).filter(JD.id == jd_id).first()
            context["job_description"] = {
                "title": jd.title if jd else "Unknown",
                "requirements": jd.required_skills if jd else {}
            }
        else:
            matches = db.query(MatchResult).all()
            context["job_description"] = "All job descriptions"
        
        # Prepare candidate data
        candidates_data = []
        for match in matches:
            candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
            if candidate:
                candidates_data.append({
                    "name": candidate.name,
                    "email": candidate.email,
                    "match_score": match.overall_score,
                    "skill_match": match.skills_match_score,
                    "experience_match": match.experience_match_score,
                    "skills": candidate.extracted_skills,
                    "experience_years": candidate.experience_years,
                    "education": candidate.education
                })
        
        context["candidates"] = candidates_data
        context["total_candidates"] = len(candidates_data)
        
        # Get bias alerts
        bias_alerts = db.query(BiasAlert).all()
        context["bias_alerts"] = [
            {
                "type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity
            } for alert in bias_alerts
        ]
        
        # Get diversity metrics
        diversity_metrics = db.query(DiversityMetrics).all()
        if diversity_metrics:
            latest_metrics = diversity_metrics[-1]
            context["diversity"] = {
                "gender_distribution": latest_metrics.gender_distribution,
                "diversity_score": latest_metrics.diversity_score,
                "inclusion_score": latest_metrics.inclusion_score
            }
        
        return context
    
    def generate_response(self, query: str, context: Dict) -> str:
        """Generate AI response using Gemini API"""
        if not self.model:
            return "AI Assistant is not configured. Please set up your Gemini API key in the environment variables."
        
        # Create a comprehensive prompt
        prompt = f"""
You are an AI assistant for a talent matching dashboard. You help HR professionals understand candidate data, matching results, and recruitment insights.

Current Dashboard Context:
- Job Description: {context.get('job_description', 'N/A')}
- Total Candidates: {context.get('total_candidates', 0)}
- Bias Alerts: {len(context.get('bias_alerts', []))} active alerts
- Diversity Score: {context.get('diversity', {}).get('diversity_score', 'N/A')}

Candidate Summary:
{json.dumps(context.get('candidates', [])[:5], indent=2)}

Bias Alerts:
{json.dumps(context.get('bias_alerts', []), indent=2)}

Diversity Metrics:
{json.dumps(context.get('diversity', {}), indent=2)}

User Query: {query}

Please provide a helpful, professional response that:
1. Directly answers the user's question
2. Uses the dashboard data to provide specific insights
3. Offers actionable recommendations when appropriate
4. Maintains a professional HR-focused tone
5. Keeps responses concise but informative

Response:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    def get_suggested_questions(self, context: Dict) -> List[str]:
        """Generate suggested questions based on current dashboard state"""
        suggestions = [
            "What are the top candidates for this position?",
            "Are there any bias concerns in the current candidate pool?",
            "How diverse is our candidate selection?",
            "Which candidates have the best skill matches?",
            "What skills are most common among high-scoring candidates?"
        ]
        
        # Add context-specific suggestions
        if context.get('bias_alerts'):
            suggestions.append("What do the bias alerts mean and how should I address them?")
        
        if context.get('total_candidates', 0) > 10:
            suggestions.append("How can I narrow down this large candidate pool?")
        
        if context.get('diversity', {}).get('diversity_score', 0) < 0.5:
            suggestions.append("How can I improve diversity in my candidate selection?")
        
        return suggestions[:6]  # Return top 6 suggestions

# Global instance
ai_assistant = AIAssistant()
