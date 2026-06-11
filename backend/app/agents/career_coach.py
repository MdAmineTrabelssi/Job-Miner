import groq
from typing import List, Dict
import json
from app.core.config import settings

class CareerCoachAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"
        
        self.certifications_db = {
            'Python': ['PCEP - Entry Level', 'PCAP - Associate', 'PCPP - Professional'],
            'Cloud': ['AWS Cloud Practitioner', 'Azure Fundamentals', 'Google Cloud Digital Leader'],
            'Data Science': ['IBM Data Science Professional', 'Google Data Analytics', 'Microsoft Azure Data Scientist'],
            'Project Management': ['PMP', 'PRINCE2', 'Agile Scrum Master']
        }
    
    async def recommend_certifications(self, skill_gaps: List[str], current_skills: List[str]) -> List[Dict]:
        recommendations = []
        for gap in skill_gaps[:3]:
            for key, certs in self.certifications_db.items():
                if gap.lower() in key.lower() or key.lower() in gap.lower():
                    for cert in certs[:2]:
                        recommendations.append({
                            'certification': cert,
                            'domain': key,
                            'estimated_time': '4-6 weeks',
                            'difficulty': 'Intermediate',
                            'provider': 'Various'
                        })
        return recommendations[:5]
    
    async def generate_career_roadmap(self, current_role: str, target_role: str, skill_gaps: List[str]) -> Dict:
        prompt = f"""Crée un plan de carrière de {current_role} à {target_role}.

Compétences manquantes: {', '.join(skill_gaps[:5])}

Retourne un roadmap en 4 phases (format texte):
Phase 1 (0-3 mois): Actions court terme
Phase 2 (3-6 mois): Actions moyen terme  
Phase 3 (6-12 mois): Actions long terme
Phase 4: Recommandations continues"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            roadmap_text = response.choices[0].message.content
        except:
            roadmap_text = f"""
Phase 1 (0-3 mois): 
- Acquérir les compétences manquantes: {', '.join(skill_gaps[:3])}
- Mettre à jour votre CV et LinkedIn

Phase 2 (3-6 mois):
- Obtenir des certifications pertinentes
- Développer un portfolio de projets

Phase 3 (6-12 mois):
- Postuler aux postes de {target_role}
- Participer à des événements networking
"""
        
        return {
            'roadmap': roadmap_text,
            'recommended_certifications': await self.recommend_certifications(skill_gaps, []),
            'recommended_courses': [
                {'course': 'Complete Python Bootcamp', 'platform': 'Udemy', 'duration': '40 hours'},
                {'course': 'Web Development Bootcamp', 'platform': 'Coursera', 'duration': '60 hours'},
                {'course': 'System Design Interview', 'platform': 'Educative', 'duration': '20 hours'}
            ],
            'portfolio_projects': [
                'Application full-stack avec authentification JWT',
                'Dashboard analytique avec visualisation de données',
                'API REST documentée avec Swagger',
                'Contribution à un projet open-source populaire'
            ]
        }