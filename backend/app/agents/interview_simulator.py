import groq
import json
import random
from typing import Dict, List, Any
from app.core.config import settings

class InterviewSimulatorAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"
    
    async def generate_interview_questions(self, job_title: str, job_description: str, cv_skills: List[str]) -> Dict:
        """Génère des questions d'entretien basées sur le poste et le CV"""
        prompt = f"""Tu es un recruteur expérimenté. Génère 5 questions d'entretien pour un poste de {job_title}.

Description du poste: {job_description[:1000]}
Compétences du candidat: {', '.join(cv_skills[:10])}

Retourne UNIQUEMENT ce JSON:
{{
    "questions": [
        {{
            "id": 1,
            "type": "technique",
            "question": "Question technique ici",
            "expected_answer": "Éléments de réponse attendus",
            "points_max": 20
        }},
        {{
            "id": 2,
            "type": "comportemental",
            "question": "Question comportementale ici",
            "expected_answer": "Éléments de réponse attendus (méthode STAR)",
            "points_max": 20
        }},
        {{
            "id": 3,
            "type": "motivation",
            "question": "Question motivation ici",
            "expected_answer": "Éléments de réponse attendus",
            "points_max": 20
        }},
        {{
            "id": 4,
            "type": "mise_en_situation",
            "question": "Mise en situation ici",
            "expected_answer": "Éléments de réponse attendus",
            "points_max": 20
        }},
        {{
            "id": 5,
            "type": "personnalite",
            "question": "Question personnalité ici",
            "expected_answer": "Éléments de réponse attendus",
            "points_max": 20
        }}
    ],
    "total_points_max": 100
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_default_questions(job_title)
    
    def _get_default_questions(self, job_title: str) -> Dict:
        """Questions par défaut"""
        return {
            "questions": [
                {"id": 1, "type": "technique", "question": f"Quelles sont vos compétences techniques pour le poste de {job_title}?", "expected_answer": "Le candidat doit lister ses compétences clés", "points_max": 20},
                {"id": 2, "type": "comportemental", "question": "Décrivez une situation difficile que vous avez résolue", "expected_answer": "Situation, Tâche, Action, Résultat", "points_max": 20},
                {"id": 3, "type": "motivation", "question": "Pourquoi voulez-vous travailler chez nous?", "expected_answer": "Recherches sur l'entreprise, alignement des valeurs", "points_max": 20},
                {"id": 4, "type": "mise_en_situation", "question": "Comment gérez-vous un délai serré?", "expected_answer": "Priorisation, organisation, communication", "points_max": 20},
                {"id": 5, "type": "personnalite", "question": "Quels sont vos points forts et points faibles?", "expected_answer": "Honnêteté, conscience de soi, plan d'amélioration", "points_max": 20}
            ],
            "total_points_max": 100
        }
    
    async def evaluate_answer(self, question: str, user_answer: str, expected_answer: str, points_max: int) -> Dict:
        """Évalue une réponse et donne une note"""
        prompt = f"""En tant que recruteur expert, évalue cette réponse d'entretien.

Question: {question}
Réponse attendue: {expected_answer}
Réponse du candidat: {user_answer}

Note maximale: {points_max} points

Retourne UNIQUEMENT ce JSON:
{{
    "score": (0-{points_max}),
    "feedback": "Commentaire détaillé sur la qualité de la réponse",
    "strengths": ["Point fort 1", "Point fort 2"],
    "improvements": ["Amélioration 1", "Amélioration 2"],
    "suggested_answer": "Exemple de bonne réponse"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "score": points_max // 2,
                "feedback": "Réponse acceptable mais pourrait être améliorée",
                "strengths": ["Le candidat a répondu"],
                "improvements": ["Plus de détails souhaitables"],
                "suggested_answer": expected_answer
            }
    
    async def calculate_final_decision(self, scores: List[int], total_max: int, job_title: str) -> Dict:
        """Calcule la décision finale (Accepter/Refuser)"""
        total_score = sum(scores)
        percentage = (total_score / total_max) * 100
        
        # Logique de décision
        if percentage >= 80:
            decision = "ACCEPTER"
            status = "excellent"
            color = "green"
            message = f"Félicitations ! Vous avez obtenu {percentage:.0f}% au total. Le recruteur est très satisfait de vos réponses."
        elif percentage >= 65:
            decision = "ACCEPTER SOUS CONDITIONS"
            status = "bon"
            color = "orange"
            message = f"Vous avez obtenu {percentage:.0f}% au total. Le recruteur est satisfait mais aimerait discuter de certains points."
        elif percentage >= 50:
            decision = "ENTRETIEN COMPLÉMENTAIRE"
            status = "moyen"
            color = "yellow"
            message = f"Vous avez obtenu {percentage:.0f}% au total. Le recruteur souhaite un second entretien pour approfondir."
        else:
            decision = "REFUSER"
            status = "insuffisant"
            color = "red"
            message = f"Vous avez obtenu {percentage:.0f}% au total. Malheureusement, le recruteur a décidé de ne pas donner suite."
        
        return {
            "final_decision": decision,
            "total_score": total_score,
            "total_max": total_max,
            "percentage": round(percentage, 1),
            "status": status,
            "color": color,
            "message": message,
            "recommendations": self._get_recommendations(percentage)
        }
    
    def _get_recommendations(self, percentage: float) -> List[str]:
        """Recommandations basées sur le score"""
        if percentage >= 80:
            return ["Préparez votre lettre d'engagement", "Attendez l'offre formelle", "Préparez vos questions pour le prochain échange"]
        elif percentage >= 65:
            return ["Améliorez les réponses aux questions techniques", "Préparez plus d'exemples concrets", "Travaillez la méthode STAR"]
        elif percentage >= 50:
            return ["Revoir les bases techniques", "Pratiquez les mises en situation", "Améliorez votre storytelling"]
        else:
            return ["Refaites des simulations d'entretien", "Consultez des ressources sur l'entretien", "Travaillez votre communication"]