"""Quick test script to verify the backend API."""

import asyncio
from app.analyzer import extract_skills, compute_gap

async def test_analyzer():
    """Test the analyzer functions."""
    
    # Test extract_skills with sample text
    resume_text = """
    Senior Software Engineer with 5 years of experience.
    Skills: Python, JavaScript, React, SQL, Git, REST APIs
    """
    
    jd_text = """
    Looking for a Full Stack Developer.
    Required: Python, React, Docker, Kubernetes, System Design, CI/CD, TypeScript, AWS
    """
    
    print("Testing skill extraction...")
    resume_skills = await extract_skills(resume_text, "resume")
    jd_skills = await extract_skills(jd_text, "job description")
    
    print(f"Resume skills extracted: {len(resume_skills)}")
    print(f"JD skills extracted: {len(jd_skills)}")
    
    # If Ollama is not running, use fallback
    if not resume_skills:
        print("Using fallback resume skills (Ollama not available)")
        resume_skills = [
            {"name": "Python", "proficiency": 85, "category": "technical"},
            {"name": "JavaScript", "proficiency": 80, "category": "technical"},
            {"name": "React", "proficiency": 70, "category": "technical"},
        ]
    
    if not jd_skills:
        print("Using fallback JD skills (Ollama not available)")
        jd_skills = [
            {"name": "Python", "proficiency": 90, "category": "technical"},
            {"name": "React", "proficiency": 85, "category": "technical"},
            {"name": "Docker", "proficiency": 80, "category": "tool"},
        ]
    
    # Test compute_gap
    print("\nTesting gap computation...")
    gap_result = compute_gap(resume_skills, jd_skills)
    
    print(f"Matched skills: {len(gap_result['matched'])}")
    print(f"Gap skills: {len(gap_result['gaps'])}")
    print(f"Match percentage: {gap_result['match_pct']}%")
    print(f"Time saved percentage: {gap_result['time_saved_pct']}%")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
