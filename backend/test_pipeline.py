"""End-to-end pipeline test for PathForge."""
import sys
sys.path.insert(0, '.')

from app.analyzer import _extract_skills_regex, compute_gap

resume = """
Senior Data Scientist with 5 years experience.
Expert in Python, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy.
Strong knowledge of Machine Learning, Deep Learning, NLP.
Experience with Apache Spark, SQL, PostgreSQL, AWS.
Used Docker, Git, Airflow, MLflow, Statistics, Feature Engineering.
"""

jd = """
Required: Python, Machine Learning, Deep Learning, TensorFlow, PyTorch.
Must have: Apache Spark, Kafka, MLOps, Kubernetes, Docker.
Nice to have: LangChain, RAG, Hugging Face, Databricks.
Tools: SQL, Airflow, dbt, Git, AWS, GCP.
"""

r = _extract_skills_regex(resume, "resume")
j = _extract_skills_regex(jd, "job description")
gap = compute_gap(r, j)

print(f"Resume skills: {len(r)}")
print(f"JD skills:     {len(j)}")
print(f"Matched:       {len(gap['matched'])}")
print(f"Gaps:          {len(gap['gaps'])}")
print(f"Match %:       {gap['match_pct']}%")
print()
print("YOUR PROFILE (top 5):")
for s in r[:5]:
    print(f"  {s['name']}: {s['proficiency']}%")
print()
print("GAPS (top 5):")
for g in gap["gaps"][:5]:
    print(f"  {g['name']}: {g['proficiency']}% required")
print()
print("MATCHED (top 3):")
for jd_s, res_s, ratio in gap["matched"][:3]:
    print(f"  {res_s['name']} ({res_s['proficiency']}%) matches JD {jd_s['name']} ({jd_s['proficiency']}%)")
print()
print("Pipeline test PASSED!")
