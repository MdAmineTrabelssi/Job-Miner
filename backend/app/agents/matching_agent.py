from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import groq
import json
from app.core.config import settings

class MatchingAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def calculate_skill_overlap(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """Calcule le pourcentage de compétences correspondantes"""
        if not job_skills:
            return 80.0  # Si pas de compétences requises, score élevé par défaut
        
        cv_set = set([s.lower().strip() for s in cv_skills])
        job_set = set([s.lower().strip() for s in job_skills])
        
        if not job_set:
            return 80.0
        
        overlap = len(cv_set.intersection(job_set))
        
        # Bonus si compétences exactes
        if overlap == len(job_set):
            return 100.0
        
        # Score de base + bonus pour chaque compétence matchée
        base_score = (overlap / len(job_set)) * 70
        bonus = min(30, overlap * 10)
        
        return min(100, base_score + bonus)
    
    def calculate_text_similarity(self, cv_text: str, job_desc: str) -> float:
        """Calcule la similarité textuelle"""
        try:
            vectors = self.vectorizer.fit_transform([cv_text[:5000], job_desc[:5000]])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            # Ajuster pour être plus généreux
            return 50 + (similarity * 50)
        except:
            return 65.0  # Score par défaut plus élevé
    
    def calculate_experience_match(self, cv_exp: str, job_exp: str) -> float:
        """Calcule la correspondance du niveau d'expérience"""
        exp_levels = {
            'entry': 0, 'junior': 1, 'mid': 2, 'senior': 3, 'lead': 4, 'expert': 5
        }
        
        cv_level = 2  # Mid par défaut
        job_level = 2
        
        for key, value in exp_levels.items():
            if key in cv_exp.lower():
                cv_level = value
            if key in job_exp.lower():
                job_level = value
        
        # Si le candidat a le niveau requis ou plus
        if cv_level >= job_level:
            return 100.0
        else:
            return max(0, (cv_level / max(1, job_level)) * 100)
    
    async def analyze_match(self, cv_data: Dict, job: Dict) -> Dict:
        """Analyse complète du match"""
        cv_skills = cv_data.get('sections', {}).get('skills', [])
        job_skills = job.get('requirements', {}).get('skills', [])
        
        # Calcul des différents scores
        skill_score = self.calculate_skill_overlap(cv_skills, job_skills)
        text_score = self.calculate_text_similarity(
            cv_data.get('raw_text', ''),
            job.get('description', '')
        )
        
        # Score d'expérience
        cv_exp = ' '.join(cv_data.get('sections', {}).get('experience', []))
        job_exp = job.get('experience_level', 'Mid')
        exp_score = self.calculate_experience_match(cv_exp, job_exp)
        
        # Score final pondéré
        match_percentage = (skill_score * 0.6) + (text_score * 0.25) + (exp_score * 0.15)
        
        # Bonus si le job contient des compétences clés
        key_skills = ['python', 'javascript', 'react', 'sql', 'java']
        bonus = 0
        for skill in job_skills:
            if skill.lower() in key_skills and skill.lower() in [s.lower() for s in cv_skills]:
                bonus += 2
        match_percentage = min(100, match_percentage + bonus)
        
        # Score d'écart de compétences
        skill_gap = max(0, 100 - skill_score)
        
        # Score de préparation entretien
        interview_readiness = min(100, match_percentage + 15)
        
        # Compétences manquantes
        cv_skills_set = set([s.lower().strip() for s in cv_skills])
        job_skills_set = set([s.lower().strip() for s in job_skills])
        missing_skills = list(job_skills_set - cv_skills_set)
        
        # Analyse IA pour explication
        prompt = f"""Analyse le match entre un candidat et un poste.

COMPÉTENCES CANDIDAT: {', '.join(cv_skills[:15])}
COMPÉTENCES REQUISES: {', '.join(job_skills[:15])}
SCORE TECHNIQUE: {skill_score:.0f}%

Donne:
1. 2 points forts du candidat pour ce poste
2. 2 points à améliorer
3. Une recommandation finale en 1 phrase

Sois positif et encourageant."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            explanation = response.choices[0].message.content
        except:
            explanation = f"Bon match ! Le candidat correspond à {match_percentage:.0f}% des critères. Compétences principales identifiées."
        
        return {
            'match_percentage': round(match_percentage, 1),
            'skill_gap_score': round(skill_gap, 1),
            'interview_readiness': round(interview_readiness, 1),
            'missing_skills': missing_skills[:8],
            'explanation': explanation,
            'skill_overlap': round(skill_score, 1),
            'experience_match': round(exp_score, 1)
        }