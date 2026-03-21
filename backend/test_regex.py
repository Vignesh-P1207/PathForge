from app.analyzer import _extract_skills_regex
text = """
Python (NumPy, Pandas, Matplotlib, Seaborn)
SQL (PostgreSQL, MySQL)
Exploratory Data Analysis (EDA)
Tableau / Power BI
Git & GitHub (version control)
"""
res = _extract_skills_regex(text, "resume")
print("REGEX SKILLS:", [x["name"] for x in res])
