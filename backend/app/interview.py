"""Interview Readiness Predictor — PathForge Backend."""

from __future__ import annotations

import re
from typing import Any

from .analyzer import call_ollama, _extract_json

# ── Pre-built question bank ───────────────────────────────────────────────────

SKILL_INTERVIEW_QUESTIONS: dict[str, list[str]] = {
    # Data / ML
    "Python": [
        "Explain the difference between a list and a tuple in Python.",
        "How does Python's GIL affect multi-threaded programs?",
        "What are decorators and when would you use them?",
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff.",
        "How do you handle class imbalance in a classification problem?",
        "What is cross-validation and why is it important?",
    ],
    "Deep Learning": [
        "What is the vanishing gradient problem and how do you address it?",
        "Explain the difference between CNN and RNN architectures.",
        "When would you use batch normalization?",
    ],
    "SQL": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "How would you find duplicate rows in a table?",
        "Explain window functions with an example.",
    ],
    "Statistics": [
        "What is the p-value and how do you interpret it?",
        "Explain the Central Limit Theorem.",
        "What is the difference between Type I and Type II errors?",
    ],
    "TensorFlow": [
        "What is the difference between eager and graph execution in TensorFlow?",
        "How do you save and restore a TensorFlow model?",
        "Explain the role of tf.data in building input pipelines.",
    ],
    "PyTorch": [
        "What is autograd and how does it work in PyTorch?",
        "How do you implement a custom loss function in PyTorch?",
        "Explain the difference between .detach() and .no_grad().",
    ],
    "NLP": [
        "What is the difference between stemming and lemmatization?",
        "Explain the transformer attention mechanism.",
        "How would you handle out-of-vocabulary words?",
    ],
    "Apache Spark": [
        "What is the difference between RDD, DataFrame, and Dataset in Spark?",
        "Explain lazy evaluation in Spark.",
        "How do you optimize a slow Spark job?",
    ],
    "Kafka": [
        "What is the role of a Kafka partition?",
        "How does Kafka ensure message durability?",
        "Explain consumer groups and their purpose.",
    ],
    # DevOps / Cloud
    "Docker": [
        "What is the difference between a Docker image and a container?",
        "How do you reduce Docker image size?",
        "Explain Docker networking modes.",
    ],
    "Kubernetes": [
        "What is the difference between a Deployment and a StatefulSet?",
        "How does Kubernetes handle pod scheduling?",
        "Explain the role of a Service in Kubernetes.",
    ],
    "AWS": [
        "What is the difference between S3 and EBS?",
        "Explain IAM roles vs IAM users.",
        "How does Auto Scaling work in AWS?",
    ],
    "CI/CD": [
        "What is the difference between continuous delivery and continuous deployment?",
        "How do you handle secrets in a CI/CD pipeline?",
        "Describe a blue-green deployment strategy.",
    ],
    "Terraform": [
        "What is Terraform state and why is it important?",
        "How do you manage multiple environments with Terraform?",
        "Explain the difference between terraform plan and terraform apply.",
    ],
    # Frontend / Backend
    "React": [
        "What is the virtual DOM and how does React use it?",
        "Explain the difference between useEffect and useLayoutEffect.",
        "How do you optimize a React application for performance?",
    ],
    "JavaScript": [
        "Explain event delegation in JavaScript.",
        "What is the difference between == and === ?",
        "How does the JavaScript event loop work?",
    ],
    "TypeScript": [
        "What is the difference between interface and type in TypeScript?",
        "Explain generics with a practical example.",
        "How do you handle null and undefined safely in TypeScript?",
    ],
    "Node.js": [
        "How does Node.js handle asynchronous operations?",
        "What is the event emitter pattern?",
        "How do you prevent callback hell in Node.js?",
    ],
    "Django": [
        "Explain Django's ORM and how it maps to database tables.",
        "What is middleware in Django?",
        "How does Django handle authentication and authorization?",
    ],
    "FastAPI": [
        "How does FastAPI handle request validation?",
        "Explain dependency injection in FastAPI.",
        "How do you implement background tasks in FastAPI?",
    ],
    # Databases
    "PostgreSQL": [
        "What is the difference between a B-tree and a GIN index?",
        "How do you analyze and optimize a slow query in PostgreSQL?",
        "Explain MVCC in PostgreSQL.",
    ],
    "MongoDB": [
        "When would you embed a document vs. use a reference?",
        "How does MongoDB handle transactions?",
        "Explain the aggregation pipeline.",
    ],
    # General
    "System Design": [
        "How would you design a URL shortener?",
        "Explain the CAP theorem with a real-world example.",
        "How do you design a system for high availability?",
    ],
    "Git": [
        "What is the difference between git merge and git rebase?",
        "How do you resolve a merge conflict?",
        "Explain git cherry-pick and when you'd use it.",
    ],
    "Linux": [
        "How do you find the process using a specific port?",
        "Explain the difference between hard links and soft links.",
        "How do you schedule a recurring task in Linux?",
    ],
    # Operational
    "Customer Service": [
        "Describe a time you handled a difficult customer.",
        "How do you prioritize multiple customer requests at once?",
        "What does excellent customer service mean to you?",
    ],
    "Inventory Management": [
        "How do you perform a cycle count?",
        "What is FIFO and when is it used?",
        "How do you handle discrepancies in inventory records?",
    ],
    "Safety Compliance": [
        "What steps do you take when you identify a safety hazard?",
        "Describe your experience with OSHA regulations.",
        "How do you ensure your team follows safety protocols?",
    ],
}

PREP_STRATEGIES: dict[str, str] = {
    "Python":              "Practice LeetCode medium problems in Python. Review OOP, generators, and async/await.",
    "Machine Learning":    "Review Andrew Ng's ML course notes. Practice explaining algorithms without jargon.",
    "Deep Learning":       "Implement a small neural network from scratch. Study backpropagation math.",
    "SQL":                 "Practice window functions and CTEs on HackerRank SQL track.",
    "Statistics":          "Review hypothesis testing, A/B testing, and Bayesian inference fundamentals.",
    "TensorFlow":          "Build and deploy a small model end-to-end. Review TF2 Keras API.",
    "PyTorch":             "Implement a custom training loop. Study autograd internals.",
    "NLP":                 "Study transformer architecture. Practice with Hugging Face pipelines.",
    "Apache Spark":        "Run Spark locally on sample datasets. Practice DataFrame API and optimization.",
    "Kafka":               "Set up a local Kafka cluster. Practice producer/consumer patterns.",
    "Docker":              "Build multi-stage Dockerfiles. Practice docker-compose for local dev.",
    "Kubernetes":          "Deploy a sample app on minikube. Study CKAD exam topics.",
    "AWS":                 "Review AWS Solutions Architect Associate topics. Practice IAM policies.",
    "CI/CD":               "Build a GitHub Actions pipeline for a sample project.",
    "Terraform":           "Write Terraform modules for common AWS resources. Study state management.",
    "React":               "Build a small app with hooks. Review React performance patterns.",
    "JavaScript":          "Study event loop, closures, and prototypal inheritance deeply.",
    "TypeScript":          "Practice utility types and generics. Review strict mode patterns.",
    "Node.js":             "Build a REST API with Express. Study streams and event emitters.",
    "Django":              "Build a CRUD app with Django REST Framework. Review ORM query optimization.",
    "FastAPI":             "Build an async API with Pydantic models. Study dependency injection.",
    "PostgreSQL":          "Practice EXPLAIN ANALYZE on slow queries. Study indexing strategies.",
    "MongoDB":             "Practice aggregation pipelines. Study schema design patterns.",
    "System Design":       "Study Grokking the System Design Interview. Practice drawing architecture diagrams.",
    "Git":                 "Practice branching strategies. Study git internals (objects, refs).",
    "Linux":               "Practice shell scripting. Study process management and networking commands.",
    "Customer Service":    "Prepare STAR-format stories about customer interactions.",
    "Inventory Management":"Review WMS workflows and practice explaining cycle count procedures.",
    "Safety Compliance":   "Review OSHA 10/30 materials. Prepare examples of safety improvements you've made.",
}

_DANGER_THRESHOLDS = {
    "low":    (0,  40),
    "medium": (40, 65),
    "high":   (65, 100),
}

_READINESS_LABELS = {
    "low":    "Not Ready",
    "medium": "Partially Ready",
    "high":   "Interview Ready",
}


def _readiness_level(match_pct: int) -> str:
    for level, (lo, hi) in _DANGER_THRESHOLDS.items():
        if lo <= match_pct < hi:
            return level
    return "high"


def _pick_questions(skill_name: str, count: int = 2) -> list[str]:
    """Return up to `count` pre-built questions for a skill, or empty list."""
    for key, qs in SKILL_INTERVIEW_QUESTIONS.items():
        if key.lower() == skill_name.lower():
            return qs[:count]
    # Partial match
    for key, qs in SKILL_INTERVIEW_QUESTIONS.items():
        if key.lower() in skill_name.lower() or skill_name.lower() in key.lower():
            return qs[:count]
    return []


async def _ollama_questions(skill: str, role: str) -> list[str]:
    """Fallback: ask Ollama for 2 interview questions for an unknown skill."""
    prompt = (
        "/no_think\n"
        f"Generate 2 concise technical interview questions for '{skill}' in a '{role}' role.\n"
        "Output ONLY raw JSON array of strings:\n"
        '["Question 1?", "Question 2?"]'
    )
    raw = await call_ollama(prompt)
    if raw:
        try:
            import json
            parsed = json.loads(_extract_json(raw))
            if isinstance(parsed, list):
                return [str(q) for q in parsed[:2] if q]
        except Exception:
            pass
    return [
        f"Describe your experience with {skill}.",
        f"How have you applied {skill} in a real project?",
    ]


async def generate_interview_questions(
    skill_name: str,
    role: str,
) -> list[str]:
    """Return 2 interview questions — pre-built first, Ollama fallback."""
    qs = _pick_questions(skill_name)
    if qs:
        return qs
    return await _ollama_questions(skill_name, role)


async def build_interview_readiness(
    match_pct: int,
    gaps: list[dict[str, Any]],
    matched: list[tuple[dict[str, Any], dict[str, Any], float]],
    role: str,
) -> dict[str, Any]:
    """Build the full interview readiness payload."""

    level = _readiness_level(match_pct)
    label = _READINESS_LABELS[level]

    # ── Danger zones: top 3 gap skills ───────────────────────────────────────
    danger_zones: list[dict[str, Any]] = []
    for gap in gaps[:3]:
        name = gap.get("name", "")
        if not name:
            continue
        questions = await generate_interview_questions(name, role)
        strategy = PREP_STRATEGIES.get(name, f"Study {name} fundamentals and practice hands-on projects.")
        danger_zones.append({
            "skill": name,
            "severity": "high" if gap.get("proficiency", 80) >= 75 else "medium",
            "questions": questions,
            "prep_strategy": strategy,
        })

    # ── Strong zones: top 3 matched skills ───────────────────────────────────
    strong_zones: list[dict[str, Any]] = []
    for jd_skill, res_skill, _ in matched[:3]:
        name = res_skill.get("name", "")
        if not name:
            continue
        questions = await generate_interview_questions(name, role)
        strong_zones.append({
            "skill": name,
            "proficiency": int(res_skill.get("proficiency", 70)),
            "questions": questions,
        })

    # ── Overall confidence score ──────────────────────────────────────────────
    confidence = min(100, max(0, match_pct + (5 if len(matched) >= 5 else 0)))

    # ── Estimated prep days ───────────────────────────────────────────────────
    prep_days = max(3, len(gaps) * 4)

    return {
        "level": level,
        "label": label,
        "confidence": confidence,
        "prep_days": prep_days,
        "danger_zones": danger_zones,
        "strong_zones": strong_zones,
    }
