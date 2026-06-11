import httpx
from typing import List, Dict

class AdzunaAPI:
    def __init__(self):
        # Remplacez par vos identifiants Adzuna
        self.app_id = "507b59c2"  # À remplacer
        self.api_key = "2ac3713906f37c2613847a4f427b1897"  # À remplacer
        self.base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/1"
    
    async def search_jobs(self, query: str, location: str = "") -> List[Dict]:
        """Recherche des offres via l'API Adzuna"""
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'results_per_page': 25,
            'what': query,
            'where': location or "France",
            'content-type': 'application/json'
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=30)
                data = response.json()
                
                jobs = []
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'description': job.get('description', '')[:500],
                        'salary_range': self._extract_salary(job),
                        'experience_level': self._extract_experience(job),
                        'requirements': {'skills': self._extract_skills(job)},
                        'source': 'Adzuna',
                        'url': job.get('redirect_url', '#'),
                        'posted_date': job.get('created', '')
                    })
                return jobs
        except Exception as e:
            print(f"Adzuna API error: {e}")
            return []
    
    def _extract_salary(self, job: dict) -> str:
        salary_min = job.get('salary_min', 0)
        salary_max = job.get('salary_max', 0)
        if salary_min and salary_max:
            return f"{int(salary_min)}k-{int(salary_max)}k EUR"
        return "Salary not specified"
    
    def _extract_experience(self, job: dict) -> str:
        # Extraction approximative du niveau d'expérience
        title = job.get('title', '').lower()
        if 'senior' in title or 'lead' in title:
            return 'Senior'
        elif 'junior' in title or 'entry' in title:
            return 'Entry/Junior'
        else:
            return 'Mid Level'
    
    def _extract_skills(self, job: dict) -> list:
        # Extraction simple de compétences depuis la description
        description = job.get('description', '').lower()
        common_skills = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 
                        'sql', 'aws', 'docker', 'kubernetes', 'git', 'typescript']
        
        skills = []
        for skill in common_skills:
            if skill in description:
                skills.append(skill.capitalize())
        return skills[:5]  # Max 5 compétences