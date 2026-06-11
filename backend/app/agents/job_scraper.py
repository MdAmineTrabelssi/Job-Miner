import asyncio
import json
import re
from typing import List, Dict
from curl_cffi import requests
import httpx

class RealJobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def search_indeed(self, query: str, location: str = "France") -> List[Dict]:
        """Scraper Indeed"""
        jobs = []
        url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}"
        
        try:
            response = requests.get(url, headers=self.headers, impersonate="chrome", timeout=30)
            
            json_match = re.search(r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\] = (.+?});', response.text)
            if json_match:
                data = json.loads(json_match.group(1))
                results = data.get('metaData', {}).get('mosaicProviderJobCardsModel', {}).get('results', [])
                for job in results:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('formattedLocation', ''),
                        'description': job.get('description', ''),
                        'salary_range': job.get('salarySnippet', ''),
                        'experience_level': job.get('jobLocation', {}).get('experienceLevel', 'Not specified'),
                        'requirements': {'skills': []},
                        'source': 'Indeed',
                        'url': f"https://www.indeed.com/viewjob?jk={job.get('jobkey', '')}"
                    })
        except Exception as e:
            print(f"Indeed error: {e}")
        
        return jobs
    
    async def search_wttj(self, query: str, location: str = "France") -> List[Dict]:
        """Welcome to the Jungle"""
        url = f"https://www.welcometothejungle.com/api/jobs/search?query={query}&location={location}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30)
                data = response.json()
                
                jobs = []
                for job in data.get('jobs', []):
                    jobs.append({
                        'title': job.get('name', ''),
                        'company': job.get('company', {}).get('name', ''),
                        'location': job.get('locations', [{}])[0].get('name', ''),
                        'description': job.get('description', ''),
                        'salary_range': job.get('salary', 'Not specified'),
                        'experience_level': job.get('experience_level', 'Not specified'),
                        'requirements': {'skills': []},
                        'source': 'WelcomeToTheJungle',
                        'url': job.get('url', '')
                    })
                return jobs
        except Exception as e:
            print(f"WTTJ error: {e}")
            return []
    
    async def search_all(self, query: str, location: str = "France") -> List[Dict]:
        """Recherche sur toutes les sources"""
        tasks = [
            self.search_indeed(query, location),
            self.search_wttj(query, location),
        ]
        
        results = await asyncio.gather(*tasks)
        
        all_jobs = []
        for jobs in results:
            all_jobs.extend(jobs)
        
        # Supprimer les doublons
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job['title']}|{job['company']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs