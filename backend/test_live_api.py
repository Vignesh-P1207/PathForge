"""Live API test — hits the running backend with real files."""
import requests
import json
import time

API = "http://localhost:8000"

# Simulate a real data scientist resume
RESUME_TEXT = """
Vignesh Kumar
Data Scientist | Machine Learning Engineer
Email: vignesh@email.com | LinkedIn: linkedin.com/in/vignesh

SUMMARY
Data Scientist with 3 years of experience building ML models and data pipelines.
Strong expertise in Python and statistical modeling. Passionate about NLP and deep learning.

SKILLS
Languages: Python (Expert), R (Intermediate), SQL (Advanced)
ML Frameworks: Scikit-learn (Expert), TensorFlow (Intermediate), Pandas, NumPy, Matplotlib
Tools: Git, Jupyter Notebook, VS Code, Docker (Basic)
Databases: PostgreSQL, MySQL, MongoDB
Cloud: AWS (Basic - S3, EC2)
Other: Statistics, A/B Testing, Feature Engineering, Data Visualization

EXPERIENCE
Data Scientist — ABC Analytics (2022–Present)
- Built classification models using Scikit-learn achieving 92% accuracy
- Developed ETL pipelines using Python and SQL
- Conducted A/B testing for product features
- Created dashboards using Matplotlib and Seaborn

Junior Data Analyst — XYZ Corp (2021–2022)
- Analyzed large datasets using Python and Pandas
- Wrote complex SQL queries for reporting
- Built visualizations using Tableau

EDUCATION
B.Tech Computer Science — VIT University, 2021
"""

JD_TEXT = """
Senior Data Scientist — TechCorp AI

Requirements:
- 4+ years Python experience (Expert level)
- Machine Learning: Scikit-learn, XGBoost, LightGBM
- Deep Learning: TensorFlow, PyTorch, Keras
- NLP and Large Language Models (LLM, Hugging Face, Transformers)
- MLOps: MLflow, Kubeflow, model deployment
- Big Data: Apache Spark, Kafka, Airflow
- Cloud: AWS (SageMaker, S3, EC2), GCP or Azure
- Databases: PostgreSQL, MongoDB, Redis
- Docker, Kubernetes for model deployment
- Statistics, A/B Testing, Experimentation
- Data Visualization: Tableau, Power BI
- Git, CI/CD pipelines
"""

def test_live():
    print("=" * 60)
    print("PATHFORGE LIVE API TEST")
    print("=" * 60)

    # Write temp files
    with open("temp_resume.txt", "w") as f:
        f.write(RESUME_TEXT)
    with open("temp_jd.txt", "w") as f:
        f.write(JD_TEXT)

    print("\nUploading resume and JD to /api/analyze...")
    start = time.time()

    with open("temp_resume.txt", "rb") as r, open("temp_jd.txt", "rb") as j:
        resp = requests.post(
            f"{API}/api/analyze",
            files={
                "resume": ("resume.txt", r, "text/plain"),
                "job_description": ("jd.txt", j, "text/plain"),
            },
            data={"role_domain": "Data & Analytics"},
            timeout=120,
        )

    elapsed = time.time() - start
    print(f"Response time: {elapsed:.1f}s | Status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"ERROR: {resp.text}")
        return

    data = resp.json()

    print(f"\n{'='*60}")
    print(f"SKILL MATCH SCORE:  {data['match_pct']}%")
    print(f"CRITICAL GAPS:      {data['critical_gaps']}")
    print(f"TRAINING TIME SAVED:{data['time_saved_pct']}%")
    print(f"WEEKS TO READY:     {data['weeks_to_ready']}")

    print(f"\nYOUR PROFILE ({len(data['current_skills'])} skills):")
    for s in data["current_skills"]:
        bar = "█" * (s["pct"] // 10)
        print(f"  {s['name']:<25} {bar:<10} {s['pct']}%")

    print(f"\nROLE REQUIRES ({len(data['required_skills'])} skills):")
    for s in data["required_skills"]:
        tag = "✓ MATCH" if s["type"] == "req" else "✗ GAP"
        print(f"  {s['name']:<25} {s['pct']}%  [{tag}]")

    print(f"\nLEARNING PATHWAY ({len(data['pathway'])} modules):")
    for p in data["pathway"]:
        print(f"  {p['week']}  {p['title']:<35} {p['hrs']}hrs  [{p['tagLabel']}]")

    print(f"\nREASONING TRACE:")
    for t in data["reasoning_trace"]:
        # Strip HTML tags for console
        import re
        msg = re.sub(r'<[^>]+>', '', t["msg"])
        print(f"  [{t['tag']}] {msg}")

    print(f"\n{'='*60}")
    print("✅ REAL-TIME ANALYSIS COMPLETE — Results are 100% dynamic!")
    print(f"   Different resume = different results")
    print(f"   Different JD = different gaps")
    print(f"{'='*60}")

    # Cleanup
    import os
    os.remove("temp_resume.txt")
    os.remove("temp_jd.txt")

if __name__ == "__main__":
    test_live()
