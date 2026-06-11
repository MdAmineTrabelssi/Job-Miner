import asyncio
from typing import List, Dict
from app.agents.job_api import AdzunaAPI

class JobMiningAgent:
    def __init__(self):
        self.api = AdzunaAPI()
        # Données mockées en secours
        self.mock_jobs = self._get_mock_jobs()
    
    def _get_mock_jobs(self):
        return [
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Paris, France',
                'description': 'We are looking for a skilled Software Engineer...',
                'requirements': {'skills': ['Python', 'React', 'SQL', 'Git', 'Docker']},
                'salary_range': '50k-70k EUR',
                'experience_level': 'Entry/Mid',
                'source': 'Indeed',
                'url': '#'
            },
            {
                'title': 'Senior Python Developer',
                'company': 'Innovation Labs',
                'location': 'Remote',
                'description': 'Senior Python developer needed for AI projects.',
                'requirements': {'skills': ['Python', 'FastAPI', 'Machine Learning', 'PostgreSQL']},
                'salary_range': '70k-90k EUR',
                'experience_level': 'Senior',
                'source': 'LinkedIn',
                'url': '#'
            },
            {
                'title': 'Frontend Developer',
                'company': 'WebStudio',
                'location': 'Lyon, France',
                'description': 'Frontend developer with React expertise.',
                'requirements': {'skills': ['React', 'TypeScript', 'TailwindCSS', 'Next.js']},
                'salary_range': '45k-60k EUR',
                'experience_level': 'Junior/Mid',
                'source': 'Glassdoor',
                'url': '#'
            },
            {
                'title': 'Data Scientist',
                'company': 'AI Center',
                'location': 'Toulouse, France',
                'description': 'Data scientist with Python skills.',
                'requirements': {'skills': ['Python', 'Pandas', 'Scikit-learn', 'TensorFlow']},
                'salary_range': '60k-85k EUR',
                'experience_level': 'Mid/Senior',
                'source': 'Indeed',
                'url': '#'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudNative',
                'location': 'Nantes, France',
                'description': 'DevOps engineer for cloud infrastructure.',
                'requirements': {'skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform']},
                'salary_range': '65k-90k EUR',
                'experience_level': 'Senior',
                'source': 'Glassdoor',
                'url': '#'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Digital Solutions',
                'location': 'Bordeaux, France',
                'description': 'Full stack developer.',
                'requirements': {'skills': ['JavaScript', 'Node.js', 'React', 'MongoDB']},
                'salary_range': '55k-75k EUR',
                'experience_level': 'Mid',
                'source': 'LinkedIn',
                'url': '#'
            },
            {
                'title': 'Mobile Developer',
                'company': 'AppFactory',
                'location': 'Nice, France',
                'description': 'Mobile developer React Native.',
                'requirements': {'skills': ['React Native', 'JavaScript', 'Firebase']},
                'salary_range': '50k-70k EUR',
                'experience_level': 'Mid',
                'source': 'Indeed',
                'url': '#'
            },
            {
                'title': 'Cloud Architect',
                'company': 'CloudExperts',
                'location': 'Strasbourg, France',
                'description': 'Cloud architect.',
                'requirements': {'skills': ['AWS', 'Azure', 'Terraform', 'Kubernetes']},
                'salary_range': '80k-110k EUR',
                'experience_level': 'Senior',
                'source': 'Glassdoor',
                'url': '#'
            },
            {
                'title': 'Product Manager',
                'company': 'TechStart',
                'location': 'Marseille, France',
                'description': 'Product manager.',
                'requirements': {'skills': ['Product Strategy', 'Agile', 'JIRA']},
                'salary_range': '60k-85k EUR',
                'experience_level': 'Mid/Senior',
                'source': 'LinkedIn',
                'url': '#'
            },
            {
                'title': 'QA Engineer',
                'company': 'QualityFirst',
                'location': 'Lille, France',
                'description': 'QA engineer.',
                'requirements': {'skills': ['Selenium', 'Jest', 'Cypress']},
                'salary_range': '45k-60k EUR',
                'experience_level': 'Junior/Mid',
                'source': 'Indeed',
                'url': '#'
            },
            {
                'title': 'Technical Lead',
                'company': 'BigCorp',
                'location': 'Paris, France',
                'description': 'Technical lead.',
                'requirements': {'skills': ['Leadership', 'System Design', 'Python']},
                'salary_range': '90k-120k EUR',
                'experience_level': 'Senior/Lead',
                'source': 'Glassdoor',
                'url': '#'
            }
        ]
    
    async def search_jobs(self, query: str, location: str = "") -> List[Dict]:
        """Recherche des offres d'emploi via API ou mock"""
        try:
            # Essayer l'API réelle
            real_jobs = await self.api.search_jobs(query, location)
            if real_jobs and len(real_jobs) > 0:
                return real_jobs
        except Exception as e:
            print(f"API error, using mock data: {e}")
        
        # Fallback: données mockées
        if query and query.strip():
            query_lower = query.lower()
            filtered_jobs = [
                job for job in self.mock_jobs 
                if query_lower in job['title'].lower() 
                or query_lower in job['company'].lower()
                or any(query_lower in skill.lower() for skill in job['requirements']['skills'])
            ]
            return filtered_jobs if filtered_jobs else self.mock_jobs[:8]
        
        return self.mock_jobs
    
    async def get_job_details(self, job_url: str) -> Dict:
        return {
            'title': 'Software Engineer',
            'company': 'Example Corp',
            'description': 'Full description here...',
            'requirements': 'Python, React, SQL',
            'benefits': 'Health insurance, Remote work'
        }