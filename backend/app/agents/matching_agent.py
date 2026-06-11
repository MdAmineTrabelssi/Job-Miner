from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import groq
import json
from app.core.config import settings

class MatchingAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"  # Modèle actif
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def calculate_skill_overlap(self, cv_skills: List[str], job_skills: List[str]) -> float:
        if not job_skills:
            return 0.0
        cv_set = set([s.lower() for s in cv_skills])
        job_set = set([s.lower() for s in job_skills])
        if not job_set:
            return 0.0
        overlap = len(cv_set.intersection(job_set))
        return (overlap / len(job_set)) * 100
    
    def calculate_text_similarity(self, cv_text: str, job_desc: str) -> float:
        try:
            vectors = self.vectorizer.fit_transform([cv_text[:5000], job_desc[:5000]])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return similarity * 100
        except:
            return 50.0
    
    async def analyze_match(self, cv_data: Dict, job: Dict) -> Dict:
        cv_skills = cv_data.get('sections', {}).get('skills', [])
        job_skills = job.get('requirements', {}).get('skills', [])
        
        skill_overlap = self.calculate_skill_overlap(cv_skills, job_skills)
        text_similarity = self.calculate_text_similarity(
            cv_data.get('raw_text', ''),
            job.get('description', '')
        )
        
        match_percentage = (skill_overlap * 0.7 + text_similarity * 0.3)
        skill_gap = 100 - skill_overlap
        interview_readiness = min(100, match_percentage + 10)
        
        job_skills_set = set([s.lower() for s in job_skills])
        cv_skills_set = set([s.lower() for s in cv_skills])
        missing_skills = list(job_skills_set - cv_skills_set)
        
        prompt = f"""Explique pourquoi ce candidat correspond à ce poste:
        
Compétences candidat: {', '.join(cv_skills[:10])}
Compétences requises: {', '.join(job_skills[:10])}
Match: {match_percentage:.1f}%

Donne 3 points forts et 3 points à améliorer en une phrase chacun."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            explanation = response.choices[0].message.content
        except:
            explanation = f"Le candidat correspond à {match_percentage:.1f}% au poste. Compétences similaires identifiées."
        
        return {
            'match_percentage': round(match_percentage, 2),
            'skill_gap_score': round(skill_gap, 2),
            'interview_readiness': round(interview_readiness, 2),
            'missing_skills': missing_skills[:10],
            'explanation': explanation,
            'skill_overlap': round(skill_overlap, 2)
        }