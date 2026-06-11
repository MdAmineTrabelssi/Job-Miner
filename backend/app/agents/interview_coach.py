import groq
import json
from app.core.config import settings

class InterviewCoachAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"
    
    async def generate_questions(self, job_description: str, job_title: str) -> dict:
        prompt = f"""Génère des questions d'entretien pour: {job_title}

Description: {job_description[:2000]}

Retourne UNIQUEMENT ce JSON:
{{
    "technical": ["Q1", "Q2", "Q3"],
    "hr": ["Q1", "Q2", "Q3"],
    "behavioral": ["Q1", "Q2", "Q3"],
    "scenario": ["Q1", "Q2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "technical": ["Décrivez votre expérience technique", "Quels sont vos projets récents?"],
                "hr": ["Pourquoi voulez-vous travailler chez nous?", "Quelles sont vos prétentions salariales?"],
                "behavioral": ["Décrivez une situation difficile que vous avez résolue", "Comment travaillez-vous en équipe?"],
                "scenario": ["Comment géreriez-vous un délai serré?", "Que feriez-vous face à un bug critique?"]
            }
    
    async def generate_personalized_answers(self, questions: list, cv_context: str) -> list:
        answers = []
        for question in questions[:5]:
            prompt = f"""CV: {cv_context[:1000]}
Question: {question}

Donne une réponse personnalisée et professionnelle (2-3 phrases)."""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                suggested = response.choices[0].message.content
            except:
                suggested = f"Je peux répondre à cette question en m'appuyant sur mon expérience..."
            
            answers.append({
                'question': question,
                'suggested_answer': suggested
            })
        
        return answers
    
    async def conduct_mock_interview(self, job_data: dict, user_cv: str) -> dict:
        questions = await self.generate_questions(
            job_data.get('description', ''),
            job_data.get('title', 'Software Engineer')
        )
        
        all_questions = (questions.get('technical', []) + 
                        questions.get('hr', []) + 
                        questions.get('behavioral', []) +
                        questions.get('scenario', []))
        
        personalized_answers = await self.generate_personalized_answers(all_questions[:8], user_cv)
        
        return {
            'questions': questions,
            'personalized_answers': personalized_answers,
            'tips': [
                "Préparez des exemples concrets avec la méthode STAR",
                "Faites des recherches approfondies sur l'entreprise",
                "Préparez 3-4 questions à poser à la fin",
                "Pratiquez à voix haute devant un miroir"
            ]
        }