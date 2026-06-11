from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import groq
import json
import re
from app.core.config import settings

class MatchingAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key)
        self.model = "llama3-70b-8192"
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Domaines et leurs mots-clés associés
        self.domains = {
            'cybersecurity': {
                'keywords': ['cyber', 'security', 'sécurité', 'firewall', 'siem', 'soc', 'pentest', 'ethical hacking', 'vulnerability', 'risk', 'compliance', 'iso 27001', 'gdpr', 'encryption', 'malware', 'threat', 'incident response', 'cissp', 'ceh', 'oscp', 'ransomware', 'antivirus', 'ids', 'ips', 'vpn', 'authentication', 'authorization', 'audit', 'security analyst', 'security engineer'],
                'search_terms': ['security analyst', 'cybersecurity', 'soc analyst', 'pentester', 'security engineer', 'information security'],
                'display_name': 'Cybersecurity'
            },
            'data_science': {
                'keywords': ['data', 'machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'statistics', 'big data', 'spark', 'hadoop', 'analytics', 'visualization', 'tableau', 'power bi', 'data engineer', 'data analyst'],
                'search_terms': ['data scientist', 'data analyst', 'machine learning', 'ai engineer', 'data engineer'],
                'display_name': 'Data Science'
            },
            'web_development': {
                'keywords': ['react', 'angular', 'vue', 'node', 'javascript', 'typescript', 'html', 'css', 'frontend', 'backend', 'fullstack', 'api', 'rest', 'graphql', 'django', 'flask', 'express', 'nextjs', 'web dev'],
                'search_terms': ['web developer', 'frontend developer', 'backend developer', 'fullstack developer', 'react developer'],
                'display_name': 'Web Development'
            },
            'cloud_devops': {
                'keywords': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'devops', 'cloud', 'infrastructure', 'ansible', 'prometheus', 'grafana', 'container', 'orchestration'],
                'search_terms': ['devops engineer', 'cloud engineer', 'aws engineer', 'kubernetes', 'sre'],
                'display_name': 'Cloud & DevOps'
            },
            'mobile_dev': {
                'keywords': ['ios', 'android', 'swift', 'kotlin', 'react native', 'flutter', 'mobile', 'app development', 'xamarin', 'ionic'],
                'search_terms': ['mobile developer', 'ios developer', 'android developer', 'react native developer'],
                'display_name': 'Mobile Development'
            },
            'database': {
                'keywords': ['sql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'database', 'dba', 'data warehouse', 'etl', 'data modeling', 'nosql'],
                'search_terms': ['database administrator', 'dba', 'data engineer', 'sql developer'],
                'display_name': 'Database'
            },
            'project_management': {
                'keywords': ['agile', 'scrum', 'jira', 'project management', 'product owner', 'scrum master', 'pmp', 'prince2', 'leadership', 'team management', 'kanban', 'trello'],
                'search_terms': ['project manager', 'product owner', 'scrum master', 'agile coach'],
                'display_name': 'Project Management'
            },
            'networking': {
                'keywords': ['cisco', 'network', 'tcp/ip', 'dns', 'dhcp', 'routing', 'switching', 'ccna', 'ccnp', 'firewall', 'lan', 'wan', 'vlan'],
                'search_terms': ['network engineer', 'network administrator', 'cisco engineer'],
                'display_name': 'Networking'
            }
        }
    
    def detect_cv_domain(self, cv_skills: List[str], cv_text: str) -> Dict:
        """Détecte le domaine principal du CV"""
        cv_lower = cv_text.lower()
        domain_scores = {}
        
        for domain, info in self.domains.items():
            score = 0
            keywords = info['keywords']
            for keyword in keywords:
                # Vérifier dans les compétences
                for skill in cv_skills:
                    if keyword in skill.lower():
                        score += 3
                # Vérifier dans le texte
                if keyword in cv_lower:
                    score += 1
            if score > 0:
                domain_scores[domain] = score
        
        # Trier par score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_domains:
            main_domain = sorted_domains[0][0]
            return {
                'main_domain': main_domain,
                'display_name': self.domains[main_domain]['display_name'],
                'score': sorted_domains[0][1],
                'search_terms': self.domains[main_domain]['search_terms'],
                'all_domains': [{'domain': d, 'name': self.domains[d]['display_name'], 'score': s} for d, s in sorted_domains[:3]]
            }
        
        return {
            'main_domain': 'general',
            'display_name': 'General IT',
            'score': 0,
            'search_terms': ['developer', 'engineer'],
            'all_domains': []
        }
    
    def calculate_domain_match(self, cv_domain: str, job_title: str, job_desc: str) -> float:
        """Calcule si le job correspond au domaine du CV"""
        job_lower = (job_title + " " + job_desc).lower()
        
        if cv_domain == 'general':
            return 60.0
        
        keywords = self.domains.get(cv_domain, {}).get('keywords', [])
        if not keywords:
            return 50.0
        
        # Compter les correspondances
        matches = 0
        for keyword in keywords:
            if keyword in job_lower:
                matches += 1
        
        # Score basé sur le nombre de correspondances
        if matches >= 5:
            return 98.0
        elif matches >= 3:
            return 90.0
        elif matches >= 2:
            return 80.0
        elif matches >= 1:
            return 70.0
        else:
            return 50.0
    
    def calculate_skill_overlap(self, cv_skills: List[str], job_skills: List[str], cv_domain: str) -> float:
        """Calcule le score de compétences basé sur le domaine"""
        
        if not cv_skills:
            return 55.0
        
        if not job_skills:
            return 75.0
        
        cv_set = set([s.lower().strip() for s in cv_skills])
        job_set = set([s.lower().strip() for s in job_skills])
        
        # Compétences communes
        common = cv_set.intersection(job_set)
        
        # Compétences du domaine du CV
        domain_keywords = self.domains.get(cv_domain, {}).get('keywords', [])
        domain_skills_in_cv = [s for s in cv_skills if any(k in s.lower() for k in domain_keywords)]
        domain_skills_in_job = [s for s in job_skills if any(k in s.lower() for k in domain_keywords)]
        
        # Bonus si le job a des compétences dans le domaine du CV
        domain_bonus = min(25, len(domain_skills_in_job) * 5)
        
        # Score de base
        if len(job_set) > 0:
            base_score = (len(common) / len(job_set)) * 70
        else:
            base_score = 70
        
        # Bonus pour compétences communes
        common_bonus = min(15, len(common) * 3)
        
        final_score = min(98, base_score + common_bonus + domain_bonus)
        
        # Garantir un score minimum si le domaine correspond
        if cv_domain != 'general' and len(domain_skills_in_job) > 0 and final_score < 60:
            final_score = 65
        
        return round(final_score, 1)
    
    async def analyze_match(self, cv_data: Dict, job: Dict) -> Dict:
        """Analyse complète du match basée sur le domaine du CV"""
        
        cv_skills = cv_data.get('sections', {}).get('skills', [])
        cv_text = cv_data.get('raw_text', '')
        
        job_skills = job.get('requirements', {}).get('skills', [])
        job_title = job.get('title', '')
        job_desc = job.get('description', '')
        
        # 1. Détecter le domaine du CV
        cv_domain_info = self.detect_cv_domain(cv_skills, cv_text)
        cv_domain = cv_domain_info['main_domain']
        
        # 2. Calculer le score de domaine
        domain_score = self.calculate_domain_match(cv_domain, job_title, job_desc)
        
        # 3. Calculer le score de compétences
        skill_score = self.calculate_skill_overlap(cv_skills, job_skills, cv_domain)
        
        # 4. Score textuel
        try:
            vectors = self.vectorizer.fit_transform([cv_text[:3000], job_desc[:3000]])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            text_score = 50 + (similarity * 40)
        except:
            text_score = 65.0
        
        # Score final pondéré (domaine a le plus de poids)
        if cv_domain != 'general':
            match_percentage = (domain_score * 0.50) + (skill_score * 0.35) + (text_score * 0.15)
        else:
            match_percentage = (skill_score * 0.60) + (text_score * 0.40)
        
        # S'assurer que le score n'est pas trop bas
        match_percentage = max(40, min(98, match_percentage))
        
        # Compétences manquantes
        cv_skills_set = set([s.lower().strip() for s in cv_skills])
        job_skills_set = set([s.lower().strip() for s in job_skills])
        missing_skills = list(job_skills_set - cv_skills_set)
        
        # Filtrer les compétences hors domaine si trop nombreuses
        domain_keywords = self.domains.get(cv_domain, {}).get('keywords', [])
        if len(missing_skills) > 5 and cv_domain != 'general':
            missing_skills = [s for s in missing_skills if any(k in s.lower() for k in domain_keywords)]
        
        # Message personnalisé basé sur le domaine
        if domain_score >= 85:
            message = f"🎯 Excellent match en {cv_domain_info['display_name']}! {match_percentage:.0f}% - Parfait pour votre profil."
        elif domain_score >= 70:
            message = f"✅ Bon match en {cv_domain_info['display_name']}! {match_percentage:.0f}% - Votre profil correspond bien."
        elif match_percentage >= 65:
            message = f"📈 Bon potentiel ! {match_percentage:.0f}% - Postulez en valorisant vos compétences."
        elif match_percentage >= 50:
            message = f"⚠️ Match partiel. Votre profil est en {cv_domain_info['display_name']}. À étudier."
        else:
            message = f"❌ Domaine différent. Votre profil: {cv_domain_info['display_name']}. Cherchez des offres dans votre domaine."
        
        return {
            'match_percentage': round(match_percentage, 1),
            'skill_gap_score': round(100 - skill_score, 1),
            'interview_readiness': round(min(98, match_percentage + 15), 1),
            'missing_skills': missing_skills[:6],
            'explanation': message,
            'skill_overlap': round(skill_score, 1),
            'domain': cv_domain_info['display_name'],
            'domain_match_score': round(domain_score, 1)
        }