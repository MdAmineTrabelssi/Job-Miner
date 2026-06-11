import pytest
from app.agents.cv_analyzer import CVAnalyzerAgent

@pytest.mark.asyncio
async def test_cv_analysis():
    agent = CVAnalyzerAgent()
    
    # Créer un faux CV
    fake_cv = b"John Doe\nSkills: Python, React, SQL\nEducation: Master CS"
    
    result = await agent.analyze_cv(fake_cv, "test.pdf")
    
    assert result['CV Score'] is not None
    assert result['ATS Compatibility Score'] is not None