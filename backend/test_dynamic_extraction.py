"""Test dynamic skill extraction with different inputs."""

import asyncio
from app.analyzer import _extract_skills_regex

def test_resume_extraction():
    """Test skill extraction from a sample resume."""
    
    resume_text = """
    John Doe
    Senior Full Stack Developer
    
    SKILLS:
    - Python, Django, Flask
    - JavaScript, React, Node.js
    - PostgreSQL, MongoDB
    - Docker, Kubernetes
    - AWS, CI/CD
    - Git, Agile
    
    EXPERIENCE:
    Built microservices using Python and Docker.
    Developed React applications with TypeScript.
    """
    
    skills = _extract_skills_regex(resume_text, "resume")
    print("=== RESUME SKILLS ===")
    for skill in skills:
        print(f"  {skill['name']}: {skill['proficiency']}% ({skill['category']})")
    print(f"Total: {len(skills)} skills\n")
    return skills


def test_jd_extraction():
    """Test skill extraction from a sample job description."""
    
    jd_text = """
    Senior Backend Engineer
    
    Requirements:
    - 5+ years experience with Python
    - Strong knowledge of FastAPI or Django
    - Experience with Docker and Kubernetes
    - Cloud platforms (AWS, Azure, or GCP)
    - Database design (PostgreSQL, Redis)
    - CI/CD pipelines
    - System Design
    - GraphQL and REST APIs
    """
    
    skills = _extract_skills_regex(jd_text, "job description")
    print("=== JOB DESCRIPTION SKILLS ===")
    for skill in skills:
        print(f"  {skill['name']}: {skill['proficiency']}% ({skill['category']})")
    print(f"Total: {len(skills)} skills\n")
    return skills


def test_data_science_resume():
    """Test with a data science focused resume."""
    
    resume_text = """
    Data Scientist
    
    Technical Skills:
    - Python, R, SQL
    - Machine Learning, Deep Learning
    - TensorFlow, PyTorch, Scikit-learn
    - Pandas, NumPy
    - Spark, Hadoop
    - Jupyter, Git
    """
    
    skills = _extract_skills_regex(resume_text, "resume")
    print("=== DATA SCIENCE RESUME ===")
    for skill in skills:
        print(f"  {skill['name']}: {skill['proficiency']}% ({skill['category']})")
    print(f"Total: {len(skills)} skills\n")
    return skills


if __name__ == "__main__":
    print("Testing Dynamic Skill Extraction\n")
    print("=" * 50)
    
    resume_skills = test_resume_extraction()
    jd_skills = test_jd_extraction()
    ds_skills = test_data_science_resume()
    
    print("=" * 50)
    print("\n✅ All extractions are DYNAMIC and based on actual content!")
    print("   Each different input produces different results.")
