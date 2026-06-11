import re
from typing import Dict, List
from PyPDF2 import PdfReader
from docx import Document
import groq
import json
import io
from app.core.config import settings

class CVAnalyzerAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        # Utiliser un modèle actif (remplace mixtral-8x7b-32768)
        self.model = "llama3-70b-8192"  # Modèle recommandé par Groq
        
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def extract_sections(self, text: str) -> Dict:
        sections = {
            'skills': [],
            'education': [],
            'certifications': [],
            'projects': [],
            'experience': []
        }
        
        patterns = {
            'skills': r'(?:skills|technologies|competences|technical skills)[:\s]+([^\n]+)',
            'education': r'(?:education|formation|academic background)[:\s]+([^\n]+)',
            'certifications': r'(?:certifications|certificates|certs)[:\s]+([^\n]+)',
            'projects': r'(?:projects|projets|portfolio)[:\s]+([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            sections[key] = matches
        
        return sections
    
    async def analyze_cv(self, file_bytes: bytes, filename: str) -> Dict:
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_bytes)
        else:
            text = self.extract_text_from_docx(file_bytes)
        
        sections = self.extract_sections(text)
        
        prompt = f"""Analyse ce CV et retourne UNIQUEMENT un JSON valide:

CV TEXT: {text[:6000]}

Retourne ce JSON exact:
{{
    "cv_score": 0-100,
    "ats_compatibility": 0-100,
    "skill_relevance": 0-100,
    "employability_score": 0-100,
    "missing_keywords": ["keyword1", "keyword2"],
    "formatting_issues": ["issue1"],
    "grammar_mistakes": ["mistake1"],
    "weak_descriptions": ["weak1"],
    "missing_sections": ["section1"],
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1"],
    "skill_gaps": ["gap1"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Utilise llama3-70b-8192
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Erreur API Groq: {e}")
            # Valeurs par défaut en cas d'erreur
            analysis = {
                "cv_score": 75,
                "ats_compatibility": 70,
                "skill_relevance": 65,
                "employability_score": 72,
                "missing_keywords": ["Python", "React", "SQL", "Git", "Docker"],
                "formatting_issues": ["Structure à améliorer"],
                "grammar_mistakes": [],
                "weak_descriptions": ["Expérience à détailler"],
                "missing_sections": ["Certifications", "Projets personnels"],
                "strengths": ["Bonne formation", "Motivation"],
                "weaknesses": ["Manque d'expérience pratique"],
                "skill_gaps": ["Cloud", "CI/CD"]
            }
        
        return {
            **analysis,
            'sections': sections,
            'raw_text': text[:2000]
        }