from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import json

from app.agents.cv_analyzer import CVAnalyzerAgent
from app.agents.job_miner import JobMiningAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.interview_coach import InterviewCoachAgent
from app.agents.career_coach import CareerCoachAgent
from app.agents.interview_simulator import InterviewSimulatorAgent
from app.core.database import get_db
from app.models.database import Resume
from sqlalchemy.orm import Session

# Créer le routeur
router = APIRouter()

# Initialiser les agents
cv_agent = CVAnalyzerAgent()
job_agent = JobMiningAgent()
matching_agent = MatchingAgent()
interview_agent = InterviewCoachAgent()
career_agent = CareerCoachAgent()
interview_simulator = InterviewSimulatorAgent()


# ============ CV ANALYSIS ============
@router.post("/analyze-cv")
async def analyze_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyse un CV et retourne les scores détaillés"""
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, "Format non supporté. Utilisez PDF ou DOCX")
    
    contents = await file.read()
    result = await cv_agent.analyze_cv(contents, file.filename)
    
    # Sauvegarder (user_id = 1 par défaut pour demo)
    resume = Resume(
        user_id=1,
        filename=file.filename,
        content_text=result.get('raw_text', ''),
        cv_score=result.get('cv_score', 0),
        ats_score=result.get('ats_compatibility', 0),
        skill_score=result.get('skill_relevance', 0),
        employability_score=result.get('employability_score', 0),
        analysis_data=result
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return result


# ============ JOB SEARCH ============
@router.get("/search-jobs")
async def search_jobs(query: str, location: str = ""):
    """Recherche des offres d'emploi"""
    jobs = await job_agent.search_jobs(query, location)
    return {"jobs": jobs, "count": len(jobs)}


# ============ RECOMMENDED JOBS (VERSION AMÉLIORÉE - BASÉE SUR LE DOMAINE) ============
@router.get("/recommended-jobs")
async def get_recommended_jobs(db: Session = Depends(get_db)):
    """Retourne les offres recommandées basées sur le domaine du CV"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    if not resume:
        raise HTTPException(404, "Aucun CV trouvé. Veuillez d'abord analyser un CV.")
    
    # Détecter le domaine du CV
    from app.agents.matching_agent import MatchingAgent
    temp_agent = MatchingAgent()
    cv_skills = resume.analysis_data.get('sections', {}).get('skills', [])
    cv_text = resume.content_text
    cv_domain_info = temp_agent.detect_cv_domain(cv_skills, cv_text)
    
    # Termes de recherche basés sur le domaine détecté
    search_terms = cv_domain_info.get('search_terms', ['developer', 'engineer'])
    search_query = search_terms[0]
    
    # Rechercher des jobs
    jobs = await job_agent.search_jobs(search_query, "")
    
    # Trier par score de match
    jobs_with_scores = []
    for job in jobs:
        match_result = await matching_agent.analyze_match(resume.analysis_data, job)
        jobs_with_scores.append({
            **job,
            'match_score': match_result['match_percentage'],
            'missing_skills': match_result['missing_skills'][:5],
            'explanation': match_result['explanation'],
            'domain_match': match_result.get('domain_match_score', 0),
            'detected_domain': match_result.get('domain', cv_domain_info['display_name'])
        })
    
    # Trier par score décroissant
    jobs_with_scores.sort(key=lambda x: x['match_score'], reverse=True)
    
    return {
        'recommended_jobs': jobs_with_scores[:10],
        'detected_domain': cv_domain_info['display_name'],
        'based_on_skills': cv_skills[:8],
        'search_used': search_query
    }


# ============ JOB MATCHING ============
@router.post("/match-job")
async def match_with_job(job: dict, db: Session = Depends(get_db)):
    """Match un CV avec une offre"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    if not resume:
        raise HTTPException(404, "Aucun CV trouvé. Veuillez d'abord analyser un CV.")
    
    match_result = await matching_agent.analyze_match(
        resume.analysis_data,
        job
    )
    
    return match_result


# ============ INTERVIEW PREPARATION ============
@router.post("/prepare-interview")
async def prepare_interview(job_data: dict, db: Session = Depends(get_db)):
    """Prépare pour un entretien"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    mock_interview = await interview_agent.conduct_mock_interview(
        job_data,
        resume.analysis_data.get('raw_text', '') if resume else ''
    )
    
    return mock_interview


# ============ INTERVIEW SIMULATOR ============
@router.post("/start-simulated-interview")
async def start_simulated_interview(job_data: dict, db: Session = Depends(get_db)):
    """Démarre un entretien simulé avec notation"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    cv_skills = resume.analysis_data.get('sections', {}).get('skills', []) if resume else []
    
    questions = await interview_simulator.generate_interview_questions(
        job_title=job_data.get('title', ''),
        job_description=job_data.get('description', ''),
        cv_skills=cv_skills
    )
    
    return {
        'job_title': job_data.get('title', ''),
        'company': job_data.get('company', ''),
        'questions': questions.get('questions', []),
        'total_points_max': questions.get('total_points_max', 100)
    }


@router.post("/evaluate-answer")
async def evaluate_answer(evaluation_data: dict):
    """Évalue une réponse et donne une note"""
    result = await interview_simulator.evaluate_answer(
        question=evaluation_data.get('question', ''),
        user_answer=evaluation_data.get('user_answer', ''),
        expected_answer=evaluation_data.get('expected_answer', ''),
        points_max=evaluation_data.get('points_max', 20)
    )
    return result


@router.post("/final-decision")
async def final_decision(decision_data: dict):
    """Calcule la décision finale basée sur tous les scores"""
    result = await interview_simulator.calculate_final_decision(
        scores=decision_data.get('scores', []),
        total_max=decision_data.get('total_max', 100),
        job_title=decision_data.get('job_title', '')
    )
    return result


# ============ CAREER ROADMAP ============
@router.post("/career-roadmap")
async def career_roadmap(target_role: str, current_role: str = "Current Position", db: Session = Depends(get_db)):
    """Génère un plan de carrière"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    skill_gaps = resume.analysis_data.get('skill_gaps', []) if resume else []
    
    roadmap = await career_agent.generate_career_roadmap(
        current_role=current_role,
        target_role=target_role,
        skill_gaps=skill_gaps
    )
    
    return roadmap


# ============ DASHBOARD ============
@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Tableau de bord personnel"""
    latest_resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    return {
        'stats': {
            'employability_score': latest_resume.employability_score if latest_resume else 0,
            'cv_score': latest_resume.cv_score if latest_resume else 0,
            'ats_score': latest_resume.ats_score if latest_resume else 0,
            'resumes_count': db.query(Resume).filter(Resume.user_id == 1).count()
        },
        'next_steps': [
            "Ajoutez plus de mots-clés spécifiques à votre CV",
            "Postulez aux offres avec 70%+ de match",
            "Préparez-vous pour les entretiens techniques",
            "Obtenez une certification dans votre domaine"
        ]
    }


# ============ HEALTH CHECK ============
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Job-Miner API"}


# ============ FORCE EXTRACT SKILLS (UTILITY) ============
@router.post("/force-extract-skills")
async def force_extract_skills(db: Session = Depends(get_db)):
    """Force l'extraction des compétences depuis le dernier CV"""
    resume = db.query(Resume).filter(Resume.user_id == 1).order_by(Resume.id.desc()).first()
    
    if not resume:
        raise HTTPException(404, "Aucun CV trouvé")
    
    # Re-analyser les compétences
    from app.agents.cv_analyzer import CVAnalyzerAgent
    temp_agent = CVAnalyzerAgent()
    sections = temp_agent.extract_sections(resume.content_text)
    
    # Mettre à jour
    if 'sections' not in resume.analysis_data:
        resume.analysis_data['sections'] = {}
    resume.analysis_data['sections']['skills'] = sections.get('skills', [])
    resume.analysis_data['sections']['education'] = sections.get('education', [])
    
    # Ajouter des compétences par défaut si nécessaire
    if len(sections.get('skills', [])) < 3:
        default_skills = ['Python', 'JavaScript', 'SQL', 'Git', 'Teamwork', 'Communication', 'Problem Solving']
        resume.analysis_data['sections']['skills'] = list(set(sections.get('skills', []) + default_skills))
    
    db.commit()
    
    return {
        'extracted_skills': resume.analysis_data['sections']['skills'],
        'skills_count': len(resume.analysis_data['sections']['skills']),
        'message': f"{len(resume.analysis_data['sections']['skills'])} compétences extraites"
    }