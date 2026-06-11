import asyncio
from typing import List, Dict
from app.agents.job_api import AdzunaAPI

class JobMiningAgent:
    def __init__(self):
        self.api = AdzunaAPI()
        # Données mockées par domaine
        self.mock_jobs_by_domain = {
            'cybersecurity': [
                {
                    'title': 'Cybersecurity Analyst',
                    'company': 'SecureTech',
                    'location': 'Paris, France',
                    'description': 'Analyse des menaces, gestion des incidents de sécurité et mise en place des politiques de sécurité.',
                    'requirements': {'skills': ['SIEM', 'Firewall', 'IDS/IPS', 'Risk Assessment', 'Incident Response', 'Splunk', 'Wireshark']},
                    'salary_range': '50k-70k EUR',
                    'experience_level': 'Mid',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'SOC Analyst (Security Operations Center)',
                    'company': 'CyberDefense',
                    'location': 'Lyon, France',
                    'description': 'Surveillance des alertes de sécurité, analyse des logs et réponse aux incidents.',
                    'requirements': {'skills': ['SOC', 'SIEM', 'Security Monitoring', 'Threat Hunting', 'Splunk', 'QRadar']},
                    'salary_range': '45k-60k EUR',
                    'experience_level': 'Junior/Mid',
                    'source': 'LinkedIn',
                    'url': '#'
                },
                {
                    'title': 'Penetration Tester (Pentester)',
                    'company': 'HackSecure',
                    'location': 'Remote, France',
                    'description': 'Tests d\'intrusion, audits de sécurité et rédaction de rapports de vulnérabilités.',
                    'requirements': {'skills': ['Penetration Testing', 'Burp Suite', 'Metasploit', 'OWASP', 'Ethical Hacking', 'Nmap']},
                    'salary_range': '55k-80k EUR',
                    'experience_level': 'Mid/Senior',
                    'source': 'Glassdoor',
                    'url': '#'
                },
                {
                    'title': 'Security Engineer',
                    'company': 'CloudSecure',
                    'location': 'Toulouse, France',
                    'description': 'Mise en place de solutions de sécurité cloud et DevSecOps.',
                    'requirements': {'skills': ['AWS Security', 'Azure Security', 'DevSecOps', 'Kubernetes Security', 'Terraform']},
                    'salary_range': '60k-85k EUR',
                    'experience_level': 'Senior',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'GRC Analyst (Governance Risk Compliance)',
                    'company': 'CompliancePro',
                    'location': 'Bordeaux, France',
                    'description': 'Gestion des risques, conformité réglementaire et audits de sécurité.',
                    'requirements': {'skills': ['ISO 27001', 'GDPR', 'Risk Management', 'Audit', 'Compliance', 'NIST']},
                    'salary_range': '50k-70k EUR',
                    'experience_level': 'Mid',
                    'source': 'LinkedIn',
                    'url': '#'
                },
                {
                    'title': 'Cybersecurity Consultant',
                    'company': 'AdviseCyber',
                    'location': 'Paris, France',
                    'description': 'Conseil en sécurité informatique pour les entreprises clients.',
                    'requirements': {'skills': ['Risk Assessment', 'Security Audit', 'ISO 27001', 'GDPR', 'Communication']},
                    'salary_range': '55k-75k EUR',
                    'experience_level': 'Senior',
                    'source': 'Glassdoor',
                    'url': '#'
                },
                {
                    'title': 'Threat Intelligence Analyst',
                    'company': 'ThreatWatch',
                    'location': 'Remote, France',
                    'description': 'Analyse des menaces et monitoring des cyberattaques.',
                    'requirements': {'skills': ['Threat Intelligence', 'OSINT', 'MITRE ATT&CK', 'Security Monitoring', 'Python']},
                    'salary_range': '50k-70k EUR',
                    'experience_level': 'Mid',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'Identity & Access Management (IAM) Engineer',
                    'company': 'IDSecure',
                    'location': 'Nantes, France',
                    'description': 'Gestion des identités et des accès.',
                    'requirements': {'skills': ['IAM', 'Active Directory', 'SSO', 'MFA', 'Okta', 'Azure AD']},
                    'salary_range': '55k-75k EUR',
                    'experience_level': 'Mid/Senior',
                    'source': 'LinkedIn',
                    'url': '#'
                },
                {
                    'title': 'Cloud Security Architect',
                    'company': 'CloudSecur',
                    'location': 'Paris, France',
                    'description': 'Architecture de sécurité cloud.',
                    'requirements': {'skills': ['AWS', 'Azure', 'GCP', 'Kubernetes Security', 'Terraform', 'DevSecOps']},
                    'salary_range': '80k-110k EUR',
                    'experience_level': 'Senior',
                    'source': 'Glassdoor',
                    'url': '#'
                },
                {
                    'title': 'Incident Response Specialist',
                    'company': 'IRTeam',
                    'location': 'Remote, France',
                    'description': 'Gestion et réponse aux incidents de sécurité.',
                    'requirements': {'skills': ['Incident Response', 'Forensics', 'Malware Analysis', 'SIEM', 'EDR']},
                    'salary_range': '60k-85k EUR',
                    'experience_level': 'Senior',
                    'source': 'Indeed',
                    'url': '#'
                }
            ],
            'data_science': [
                {
                    'title': 'Data Scientist',
                    'company': 'DataMind',
                    'location': 'Paris, France',
                    'description': 'Analyse de données et modèles de machine learning.',
                    'requirements': {'skills': ['Python', 'Pandas', 'Scikit-learn', 'TensorFlow', 'SQL']},
                    'salary_range': '55k-75k EUR',
                    'experience_level': 'Mid',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'Data Analyst',
                    'company': 'AnalyticsPro',
                    'location': 'Lyon, France',
                    'description': 'Visualisation et analyse de données.',
                    'requirements': {'skills': ['SQL', 'Tableau', 'Power BI', 'Excel', 'Python']},
                    'salary_range': '40k-55k EUR',
                    'experience_level': 'Junior',
                    'source': 'LinkedIn',
                    'url': '#'
                },
                {
                    'title': 'Machine Learning Engineer',
                    'company': 'MLFactory',
                    'location': 'Toulouse, France',
                    'description': 'Déploiement de modèles ML en production.',
                    'requirements': {'skills': ['Python', 'TensorFlow', 'PyTorch', 'Docker', 'Kubernetes', 'MLOps']},
                    'salary_range': '60k-85k EUR',
                    'experience_level': 'Senior',
                    'source': 'Glassdoor',
                    'url': '#'
                }
            ],
            'web_development': [
                {
                    'title': 'Frontend Developer',
                    'company': 'WebStudio',
                    'location': 'Paris, France',
                    'description': 'Développement d\'interfaces utilisateur.',
                    'requirements': {'skills': ['React', 'JavaScript', 'HTML/CSS', 'TypeScript', 'Next.js']},
                    'salary_range': '45k-65k EUR',
                    'experience_level': 'Mid',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'Fullstack Developer',
                    'company': 'TechCorp',
                    'location': 'Remote, France',
                    'description': 'Développement fullstack.',
                    'requirements': {'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker']},
                    'salary_range': '55k-75k EUR',
                    'experience_level': 'Mid/Senior',
                    'source': 'LinkedIn',
                    'url': '#'
                },
                {
                    'title': 'Backend Developer',
                    'company': 'APIFirst',
                    'location': 'Bordeaux, France',
                    'description': 'Développement API et microservices.',
                    'requirements': {'skills': ['Python', 'FastAPI', 'Node.js', 'PostgreSQL', 'Redis']},
                    'salary_range': '50k-70k EUR',
                    'experience_level': 'Mid',
                    'source': 'Glassdoor',
                    'url': '#'
                }
            ],
            'cloud_devops': [
                {
                    'title': 'DevOps Engineer',
                    'company': 'CloudNative',
                    'location': 'Paris, France',
                    'description': 'Gestion CI/CD et infrastructure cloud.',
                    'requirements': {'skills': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform']},
                    'salary_range': '60k-85k EUR',
                    'experience_level': 'Senior',
                    'source': 'Indeed',
                    'url': '#'
                },
                {
                    'title': 'Cloud Architect',
                    'company': 'CloudExperts',
                    'location': 'Lyon, France',
                    'description': 'Architecture cloud.',
                    'requirements': {'skills': ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Terraform']},
                    'salary_range': '70k-100k EUR',
                    'experience_level': 'Senior',
                    'source': 'LinkedIn',
                    'url': '#'
                }
            ],
            'general': [
                {
                    'title': 'Software Engineer',
                    'company': 'Tech Corp',
                    'location': 'Paris, France',
                    'description': 'Développement logiciel.',
                    'requirements': {'skills': ['Python', 'JavaScript', 'SQL', 'Git']},
                    'salary_range': '50k-70k EUR',
                    'experience_level': 'Mid',
                    'source': 'Indeed',
                    'url': '#'
                }
            ]
        }
    
    def _get_all_jobs(self) -> List[Dict]:
        """Retourne toutes les offres mockées"""
        all_jobs = []
        for jobs in self.mock_jobs_by_domain.values():
            all_jobs.extend(jobs)
        return all_jobs
    
    async def search_jobs(self, query: str, location: str = "") -> List[Dict]:
        """Recherche des offres d'emploi basées sur la requête (domaine)"""
        try:
            # Essayer l'API réelle
            real_jobs = await self.api.search_jobs(query, location)
            if real_jobs and len(real_jobs) > 0:
                return real_jobs
        except Exception as e:
            print(f"API error, using mock data: {e}")
        
        # Déterminer le domaine à partir de la requête
        query_lower = query.lower()
        detected_domain = None
        
        # Mots-clés par domaine
        domain_keywords = {
            'cybersecurity': ['security', 'cyber', 'soc', 'siem', 'firewall', 'pentest', 'cissp', 'ceh', 'iso 27001', 'gdpr', 'threat', 'incident', 'risk', 'compliance'],
            'data_science': ['data', 'scientist', 'analyst', 'machine learning', 'ml', 'ai', 'tensorflow', 'pandas', 'scikit-learn'],
            'web_development': ['frontend', 'backend', 'fullstack', 'react', 'angular', 'vue', 'javascript', 'html', 'css', 'web'],
            'cloud_devops': ['devops', 'cloud', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd']
        }
        
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected_domain = domain
                    break
            if detected_domain:
                break
        
        # Filtrer les jobs par domaine détecté
        if detected_domain and detected_domain in self.mock_jobs_by_domain:
            return self.mock_jobs_by_domain[detected_domain]
        
        # Si requête spécifique, filtrer par titre ou compétences
        if query and query.strip():
            filtered_jobs = []
            for job in self._get_all_jobs():
                if (query_lower in job['title'].lower() or 
                    query_lower in job['company'].lower() or
                    any(query_lower in skill.lower() for skill in job['requirements']['skills'])):
                    filtered_jobs.append(job)
            
            return filtered_jobs if filtered_jobs else self.mock_jobs_by_domain['general']
        
        # Par défaut, retourner les offres cybersécurité
        return self.mock_jobs_by_domain['cybersecurity']
    
    async def get_job_details(self, job_url: str) -> Dict:
        """Récupère les détails d'une offre"""
        return {
            'title': 'Software Engineer',
            'company': 'Example Corp',
            'description': 'Full description here...',
            'requirements': 'Python, React, SQL',
            'benefits': 'Health insurance, Remote work'
        }