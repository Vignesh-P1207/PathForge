"""DAG-based learning path generator — PathForge Backend."""

import json
from typing import Any

import networkx as nx

from .analyzer import call_ollama, _extract_json

# ── Prerequisite map ──────────────────────────────────────────────────────────
PREREQUISITES: dict[str, list[str]] = {
    "Kubernetes": ["Docker", "Linux"],
    "Helm": ["Kubernetes"],
    "ArgoCD": ["Kubernetes", "Git"],
    "Istio": ["Kubernetes"],
    "CI/CD": ["Git", "Docker"],
    "CI/CD Pipelines": ["Git", "Docker"],
    "Terraform": ["Linux"],
    "Ansible": ["Linux", "Python"],
    "Jenkins": ["Git", "Linux"],
    "Machine Learning": ["Python", "Statistics"],
    "Deep Learning": ["Machine Learning", "Python"],
    "TensorFlow": ["Deep Learning", "Python"],
    "PyTorch": ["Deep Learning", "Python"],
    "Keras": ["Deep Learning", "Python"],
    "MLOps": ["Machine Learning", "Docker"],
    "LLMOps": ["MLOps"],
    "Fine-tuning": ["Deep Learning"],
    "RAG": ["Python"],
    "LangChain": ["Python"],
    "Computer Vision": ["Deep Learning", "Python"],
    "NLP": ["Python", "Machine Learning"],
    "Reinforcement Learning": ["Machine Learning", "Python"],
    "XGBoost": ["Machine Learning", "Python"],
    "LightGBM": ["Machine Learning", "Python"],
    "Apache Spark": ["Python", "SQL"],
    "Spark": ["Python", "SQL"],
    "Hadoop": ["Linux"],
    "Kafka": ["Python"],
    "Apache Kafka": ["Python"],
    "Airflow": ["Python", "SQL"],
    "dbt": ["SQL"],
    "Data Modeling": ["SQL"],
    "A/B Testing": ["Statistics", "SQL"],
    "Feature Engineering": ["Python", "Machine Learning"],
    "React": ["JavaScript"],
    "Next.js": ["React", "JavaScript"],
    "Vue.js": ["JavaScript"],
    "Angular": ["TypeScript", "JavaScript"],
    "TypeScript": ["JavaScript"],
    "GraphQL": ["JavaScript"],
    "NestJS": ["Node.js", "TypeScript"],
    "Redux": ["React", "JavaScript"],
    "Django": ["Python"],
    "FastAPI": ["Python"],
    "Flask": ["Python"],
    "Spring Boot": ["Java"],
    "Node.js": ["JavaScript"],
    "AWS": ["Linux"],
    "Azure": ["Linux"],
    "GCP": ["Linux"],
    "System Design": ["Networking"],
    "Microservices": ["Docker"],
    "Databricks": ["Apache Spark", "Python"],
    "Snowflake": ["SQL"],
    "Power BI": ["SQL"],
}

# ── Built-in module catalog — instant, no Ollama needed ──────────────────────
_CATALOG: dict[str, dict[str, Any]] = {
    "Python": {"title": "Python for Professionals", "desc": "Advanced Python patterns, OOP, async, and performance optimization.", "hrs": 10, "mods": 5},
    "Machine Learning": {"title": "Machine Learning Fundamentals", "desc": "Supervised, unsupervised learning, model evaluation, and deployment.", "hrs": 16, "mods": 6},
    "Deep Learning": {"title": "Deep Learning & Neural Networks", "desc": "CNNs, RNNs, transformers, and practical model training.", "hrs": 18, "mods": 7},
    "TensorFlow": {"title": "TensorFlow & Keras Mastery", "desc": "Build, train, and deploy neural networks with TensorFlow 2.x.", "hrs": 14, "mods": 5},
    "PyTorch": {"title": "PyTorch for Deep Learning", "desc": "Dynamic computation graphs, custom layers, and model deployment.", "hrs": 14, "mods": 5},
    "Scikit-learn": {"title": "Scikit-learn Applied ML", "desc": "Pipelines, cross-validation, feature selection, and ensemble methods.", "hrs": 10, "mods": 4},
    "MLOps": {"title": "MLOps Engineering", "desc": "Model versioning, CI/CD for ML, monitoring, and production deployment.", "hrs": 16, "mods": 6},
    "Apache Spark": {"title": "Apache Spark & Big Data", "desc": "Distributed data processing, Spark SQL, MLlib, and streaming.", "hrs": 14, "mods": 5},
    "Spark": {"title": "Apache Spark & Big Data", "desc": "Distributed data processing, Spark SQL, MLlib, and streaming.", "hrs": 14, "mods": 5},
    "Kafka": {"title": "Apache Kafka Streaming", "desc": "Event-driven architecture, producers, consumers, and stream processing.", "hrs": 10, "mods": 4},
    "Apache Kafka": {"title": "Apache Kafka Streaming", "desc": "Event-driven architecture, producers, consumers, and stream processing.", "hrs": 10, "mods": 4},
    "Kubernetes": {"title": "Kubernetes Orchestration", "desc": "Pods, deployments, services, Helm charts, and cluster management.", "hrs": 14, "mods": 5},
    "Docker": {"title": "Docker & Containerization", "desc": "Images, containers, Compose, networking, and security best practices.", "hrs": 10, "mods": 4},
    "AWS": {"title": "AWS Cloud Practitioner to Pro", "desc": "Core services, IAM, S3, EC2, Lambda, and cloud architecture.", "hrs": 16, "mods": 6},
    "GCP": {"title": "Google Cloud Platform", "desc": "GCP core services, BigQuery, Vertex AI, and cloud-native development.", "hrs": 14, "mods": 5},
    "Azure": {"title": "Microsoft Azure Fundamentals", "desc": "Azure services, AKS, Azure ML, and enterprise cloud solutions.", "hrs": 14, "mods": 5},
    "NLP": {"title": "Natural Language Processing", "desc": "Text preprocessing, embeddings, transformers, and NLP pipelines.", "hrs": 14, "mods": 5},
    "LLM": {"title": "Large Language Models", "desc": "LLM architecture, prompt engineering, fine-tuning, and RAG systems.", "hrs": 16, "mods": 6},
    "RAG": {"title": "Retrieval Augmented Generation", "desc": "Vector databases, embeddings, retrieval pipelines, and LLM grounding.", "hrs": 12, "mods": 5},
    "LangChain": {"title": "LangChain & LLM Applications", "desc": "Chains, agents, tools, memory, and production LLM app development.", "hrs": 10, "mods": 4},
    "Hugging Face": {"title": "Hugging Face Transformers", "desc": "Pre-trained models, fine-tuning, tokenizers, and model hub.", "hrs": 12, "mods": 5},
    "Airflow": {"title": "Apache Airflow Orchestration", "desc": "DAGs, operators, scheduling, and production data pipeline management.", "hrs": 10, "mods": 4},
    "dbt": {"title": "dbt Data Transformation", "desc": "SQL-based transformations, testing, documentation, and data modeling.", "hrs": 8, "mods": 3},
    "Databricks": {"title": "Databricks Lakehouse Platform", "desc": "Delta Lake, MLflow, Spark on Databricks, and collaborative notebooks.", "hrs": 12, "mods": 5},
    "Snowflake": {"title": "Snowflake Data Cloud", "desc": "Data warehousing, virtual warehouses, data sharing, and optimization.", "hrs": 10, "mods": 4},
    "Terraform": {"title": "Terraform Infrastructure as Code", "desc": "Providers, modules, state management, and cloud provisioning.", "hrs": 10, "mods": 4},
    "React": {"title": "React & Modern Frontend", "desc": "Hooks, state management, performance optimization, and testing.", "hrs": 12, "mods": 5},
    "TypeScript": {"title": "TypeScript Advanced Patterns", "desc": "Type system, generics, decorators, and large-scale app architecture.", "hrs": 8, "mods": 4},
    "System Design": {"title": "System Design & Architecture", "desc": "Scalability, distributed systems, CAP theorem, and design patterns.", "hrs": 18, "mods": 7},
    "Statistics": {"title": "Applied Statistics for Data Science", "desc": "Probability, hypothesis testing, regression, and Bayesian methods.", "hrs": 12, "mods": 5},
    "Feature Engineering": {"title": "Feature Engineering Mastery", "desc": "Feature selection, encoding, scaling, and domain-specific transformations.", "hrs": 8, "mods": 4},
    "A/B Testing": {"title": "A/B Testing & Experimentation", "desc": "Experimental design, statistical significance, and causal inference.", "hrs": 8, "mods": 3},
    "XGBoost": {"title": "Gradient Boosting with XGBoost", "desc": "Boosting theory, hyperparameter tuning, and competition-winning techniques.", "hrs": 8, "mods": 3},
    "LightGBM": {"title": "LightGBM for Production ML", "desc": "Fast gradient boosting, categorical features, and large dataset handling.", "hrs": 8, "mods": 3},
    "Computer Vision": {"title": "Computer Vision with Deep Learning", "desc": "Image classification, object detection, segmentation, and OpenCV.", "hrs": 14, "mods": 5},
    "PostgreSQL": {"title": "PostgreSQL Advanced", "desc": "Query optimization, indexing, partitioning, and database administration.", "hrs": 8, "mods": 4},
    "MongoDB": {"title": "MongoDB & NoSQL Design", "desc": "Document modeling, aggregation pipelines, indexing, and Atlas.", "hrs": 8, "mods": 3},
    "Redis": {"title": "Redis Caching & Data Structures", "desc": "Caching strategies, pub/sub, streams, and Redis cluster.", "hrs": 6, "mods": 3},
    "GraphQL": {"title": "GraphQL API Design", "desc": "Schema design, resolvers, subscriptions, and Apollo integration.", "hrs": 8, "mods": 4},
    "CI/CD": {"title": "CI/CD Pipeline Engineering", "desc": "GitHub Actions, Jenkins, automated testing, and deployment strategies.", "hrs": 10, "mods": 4},
    "CI/CD Pipelines": {"title": "CI/CD Pipeline Engineering", "desc": "GitHub Actions, Jenkins, automated testing, and deployment strategies.", "hrs": 10, "mods": 4},
    "Microservices": {"title": "Microservices Architecture", "desc": "Service decomposition, API gateways, service mesh, and observability.", "hrs": 14, "mods": 5},
    "Power BI": {"title": "Power BI Data Visualization", "desc": "DAX, data modeling, interactive dashboards, and report publishing.", "hrs": 8, "mods": 3},
    "Tableau": {"title": "Tableau Visual Analytics", "desc": "Charts, calculated fields, dashboards, and Tableau Server.", "hrs": 8, "mods": 3},
    "MLflow": {"title": "MLflow Experiment Tracking", "desc": "Experiment logging, model registry, and ML lifecycle management.", "hrs": 6, "mods": 3},
    "Kubeflow": {"title": "Kubeflow ML Pipelines", "desc": "ML workflows on Kubernetes, pipeline components, and serving.", "hrs": 10, "mods": 4},
    "Django": {"title": "Django Web Framework", "desc": "Models, views, REST APIs, authentication, and deployment.", "hrs": 12, "mods": 5},
    "FastAPI": {"title": "FastAPI Modern APIs", "desc": "Async endpoints, Pydantic validation, OpenAPI docs, and deployment.", "hrs": 8, "mods": 4},
    "Node.js": {"title": "Node.js Backend Development", "desc": "Event loop, streams, Express, async patterns, and microservices.", "hrs": 10, "mods": 4},
    "Linux": {"title": "Linux for Developers", "desc": "Shell scripting, process management, networking, and system administration.", "hrs": 8, "mods": 4},
    "Git": {"title": "Git & Version Control", "desc": "Branching strategies, rebasing, hooks, and collaborative workflows.", "hrs": 6, "mods": 3},
}


def build_learning_path(gap_skills: list[str], existing_skills: list[str]) -> list[str]:
    """Build a topologically sorted learning path respecting prerequisites."""
    if not gap_skills:
        return []

    existing_lower: set[str] = {s.lower() for s in existing_skills}
    gap_lower_map: dict[str, str] = {s.lower(): s for s in gap_skills}

    graph: nx.DiGraph = nx.DiGraph()
    for skill in gap_skills:
        graph.add_node(skill)

    for skill in gap_skills:
        for prereq in PREREQUISITES.get(skill, []):
            pl = prereq.lower()
            if pl in gap_lower_map and pl not in existing_lower:
                graph.add_edge(gap_lower_map[pl], skill)
            elif pl not in existing_lower and pl not in gap_lower_map:
                graph.add_node(prereq)
                graph.add_edge(prereq, skill)

    try:
        ordered = list(nx.topological_sort(graph))
        return [s for s in ordered if s in gap_skills]
    except nx.NetworkXUnfeasible:
        return list(gap_skills)


async def generate_module(skill: str, role: str, existing_skills: str = "") -> dict[str, Any]:
    """Return a training module — catalog first, Ollama for unknowns, smart fallback."""

    # ── 1. Check built-in catalog first (instant) ─────────────────────────────
    if skill in _CATALOG:
        return dict(_CATALOG[skill])

    # ── 2. Try Ollama for skills not in catalog ────────────────────────────────
    context = f" Candidate already knows: {existing_skills}." if existing_skills else ""
    prompt = (
        "/no_think\n"
        f"Training module for '{skill}' in a '{role}' role.{context}\n"
        "Output ONLY raw JSON:\n"
        f'{{"title": "...", "desc": "One sentence under 15 words.", "hrs": 8, "mods": 4}}'
    )

    raw = await call_ollama(prompt)
    if raw:
        try:
            parsed: Any = json.loads(_extract_json(raw))
            if isinstance(parsed, dict) and parsed.get("title"):
                return {
                    "title": str(parsed["title"]),
                    "desc": str(parsed.get("desc", f"Master {skill} for {role} roles.")),
                    "hrs": max(4, min(20, int(parsed.get("hrs", 8)))),
                    "mods": max(2, min(8, int(parsed.get("mods", 4)))),
                }
        except Exception:
            pass

    # ── 3. Smart fallback ─────────────────────────────────────────────────────
    hrs = _estimate_hours(skill)
    return {
        "title": f"{skill} for {role}",
        "desc": f"Core {skill} concepts, hands-on projects, and real-world application.",
        "hrs": hrs,
        "mods": max(2, hrs // 3),
    }


def _estimate_hours(skill: str) -> int:
    s = skill.lower()
    if any(k in s for k in ["machine learning", "deep learning", "system design", "kubernetes", "mlops", "llm", "spark", "hadoop"]):
        return 16
    if any(k in s for k in ["docker", "react", "django", "aws", "azure", "gcp", "typescript", "kafka", "airflow", "tensorflow", "pytorch"]):
        return 10
    return 8


# ── Operational Role Templates ────────────────────────────────────────────────

OPERATIONAL_ROLE_NAMES: list[str] = [
    "Warehouse / Logistics",
    "Retail / Store Ops",
    "Field Technician",
    "Healthcare Support",
    "Hospitality / F&B",
    "Construction / Site",
]

OPERATIONAL_ROLE_TEMPLATES: dict[str, list[str]] = {
    "Warehouse / Logistics": [
        "Inventory Management", "Forklift Operation", "WMS Software",
        "Supply Chain Basics", "Safety Compliance", "Barcode Scanning",
        "Shipping & Receiving", "Order Fulfillment",
    ],
    "Retail / Store Ops": [
        "POS Systems", "Customer Service", "Inventory Control",
        "Visual Merchandising", "Cash Handling", "Loss Prevention",
        "Sales Techniques", "CRM Basics",
    ],
    "Field Technician": [
        "Electrical Systems", "Troubleshooting", "Safety Protocols",
        "Equipment Maintenance", "Technical Documentation", "Tools & Calibration",
        "Customer Communication", "Mobile Reporting",
    ],
    "Healthcare Support": [
        "Patient Care Basics", "Medical Terminology", "HIPAA Compliance",
        "Vital Signs Monitoring", "Electronic Health Records", "Infection Control",
        "Emergency Procedures", "Communication Skills",
    ],
    "Hospitality / F&B": [
        "Food Safety & Hygiene", "Customer Service", "POS Systems",
        "Menu Knowledge", "Upselling Techniques", "Inventory Management",
        "Team Coordination", "Complaint Handling",
    ],
    "Construction / Site": [
        "Blueprint Reading", "Safety Regulations (OSHA)", "Power Tools",
        "Site Coordination", "Material Estimation", "Quality Inspection",
        "Heavy Equipment Basics", "Project Documentation",
    ],
}

OPERATIONAL_QUICK_MODULES: dict[str, dict[str, Any]] = {
    "Inventory Management":       {"title": "Inventory Management Essentials", "desc": "Stock control, cycle counts, and warehouse management systems.", "hrs": 6, "mods": 3},
    "Forklift Operation":         {"title": "Forklift & Material Handling", "desc": "Safe operation, load handling, and certification prep.", "hrs": 4, "mods": 2},
    "WMS Software":               {"title": "Warehouse Management Systems", "desc": "WMS platforms, scanning workflows, and reporting.", "hrs": 6, "mods": 3},
    "Supply Chain Basics":        {"title": "Supply Chain Fundamentals", "desc": "End-to-end logistics, procurement, and vendor management.", "hrs": 8, "mods": 4},
    "Safety Compliance":          {"title": "Workplace Safety & Compliance", "desc": "OSHA standards, hazard identification, and incident reporting.", "hrs": 4, "mods": 2},
    "Barcode Scanning":           {"title": "Barcode & RFID Systems", "desc": "Scanning technology, data entry accuracy, and inventory tracking.", "hrs": 3, "mods": 2},
    "Shipping & Receiving":       {"title": "Shipping & Receiving Operations", "desc": "Inbound/outbound logistics, documentation, and carrier coordination.", "hrs": 5, "mods": 3},
    "Order Fulfillment":          {"title": "Order Fulfillment & Picking", "desc": "Pick-pack-ship workflows, accuracy metrics, and SLA management.", "hrs": 5, "mods": 3},
    "POS Systems":                {"title": "Point-of-Sale Systems", "desc": "POS operation, transaction processing, and end-of-day reconciliation.", "hrs": 4, "mods": 2},
    "Customer Service":           {"title": "Customer Service Excellence", "desc": "Communication, conflict resolution, and customer satisfaction.", "hrs": 6, "mods": 3},
    "Inventory Control":          {"title": "Retail Inventory Control", "desc": "Stock management, shrinkage prevention, and replenishment.", "hrs": 5, "mods": 3},
    "Visual Merchandising":       {"title": "Visual Merchandising", "desc": "Display design, planogram execution, and sales floor optimization.", "hrs": 4, "mods": 2},
    "Cash Handling":              {"title": "Cash Handling & Reconciliation", "desc": "Accurate cash management, till balancing, and fraud prevention.", "hrs": 3, "mods": 2},
    "Loss Prevention":            {"title": "Loss Prevention Fundamentals", "desc": "Theft deterrence, surveillance, and incident documentation.", "hrs": 4, "mods": 2},
    "Sales Techniques":           {"title": "Retail Sales Techniques", "desc": "Consultative selling, upselling, and closing strategies.", "hrs": 6, "mods": 3},
    "CRM Basics":                 {"title": "CRM for Customer-Facing Roles", "desc": "CRM data entry, customer history, and follow-up workflows.", "hrs": 4, "mods": 2},
    "Electrical Systems":         {"title": "Electrical Systems Fundamentals", "desc": "Wiring, circuit diagnosis, and safe electrical work practices.", "hrs": 8, "mods": 4},
    "Troubleshooting":            {"title": "Technical Troubleshooting", "desc": "Systematic fault diagnosis, root cause analysis, and repair.", "hrs": 6, "mods": 3},
    "Safety Protocols":           {"title": "Field Safety Protocols", "desc": "PPE, lockout/tagout, and site-specific safety procedures.", "hrs": 4, "mods": 2},
    "Equipment Maintenance":      {"title": "Preventive Equipment Maintenance", "desc": "Maintenance schedules, lubrication, and equipment longevity.", "hrs": 6, "mods": 3},
    "Technical Documentation":    {"title": "Technical Documentation", "desc": "Work orders, service reports, and maintenance logs.", "hrs": 3, "mods": 2},
    "Tools & Calibration":        {"title": "Tools & Instrument Calibration", "desc": "Hand tools, power tools, and precision measurement instruments.", "hrs": 4, "mods": 2},
    "Customer Communication":     {"title": "Customer Communication Skills", "desc": "Professional communication, expectation setting, and follow-up.", "hrs": 4, "mods": 2},
    "Mobile Reporting":           {"title": "Mobile Field Reporting", "desc": "Field service apps, photo documentation, and digital sign-off.", "hrs": 3, "mods": 2},
    "Patient Care Basics":        {"title": "Patient Care Fundamentals", "desc": "Bedside manner, patient rights, and basic care procedures.", "hrs": 6, "mods": 3},
    "Medical Terminology":        {"title": "Medical Terminology", "desc": "Clinical vocabulary, abbreviations, and documentation standards.", "hrs": 6, "mods": 3},
    "HIPAA Compliance":           {"title": "HIPAA & Healthcare Compliance", "desc": "Patient privacy, data security, and regulatory requirements.", "hrs": 4, "mods": 2},
    "Vital Signs Monitoring":     {"title": "Vital Signs & Patient Monitoring", "desc": "BP, pulse, temperature, and SpO2 measurement and recording.", "hrs": 5, "mods": 3},
    "Electronic Health Records":  {"title": "Electronic Health Records (EHR)", "desc": "EHR navigation, data entry, and clinical documentation.", "hrs": 6, "mods": 3},
    "Infection Control":          {"title": "Infection Control & Prevention", "desc": "Hand hygiene, PPE, sterilization, and isolation protocols.", "hrs": 4, "mods": 2},
    "Emergency Procedures":       {"title": "Emergency Response Procedures", "desc": "Code response, CPR basics, and emergency escalation.", "hrs": 5, "mods": 3},
    "Communication Skills":       {"title": "Professional Communication", "desc": "Verbal, written, and interpersonal communication in the workplace.", "hrs": 4, "mods": 2},
    "Food Safety & Hygiene":      {"title": "Food Safety & Hygiene", "desc": "HACCP principles, allergen awareness, and kitchen sanitation.", "hrs": 4, "mods": 2},
    "Menu Knowledge":             {"title": "Menu Knowledge & Pairing", "desc": "Ingredients, preparation methods, and beverage pairing.", "hrs": 3, "mods": 2},
    "Upselling Techniques":       {"title": "Upselling & Revenue Techniques", "desc": "Suggestive selling, add-ons, and guest experience enhancement.", "hrs": 3, "mods": 2},
    "Team Coordination":          {"title": "Team Coordination & Shift Management", "desc": "Shift handover, task delegation, and team communication.", "hrs": 4, "mods": 2},
    "Complaint Handling":         {"title": "Complaint Handling & Recovery", "desc": "De-escalation, service recovery, and guest satisfaction.", "hrs": 4, "mods": 2},
    "Blueprint Reading":          {"title": "Blueprint & Technical Drawing Reading", "desc": "Architectural drawings, symbols, and site plan interpretation.", "hrs": 6, "mods": 3},
    "Safety Regulations (OSHA)":  {"title": "OSHA Safety Regulations", "desc": "Construction safety standards, hazard communication, and compliance.", "hrs": 6, "mods": 3},
    "Power Tools":                {"title": "Power Tools & Equipment Safety", "desc": "Safe operation, maintenance, and selection of power tools.", "hrs": 4, "mods": 2},
    "Site Coordination":          {"title": "Construction Site Coordination", "desc": "Scheduling, subcontractor management, and progress tracking.", "hrs": 6, "mods": 3},
    "Material Estimation":        {"title": "Material Takeoff & Estimation", "desc": "Quantity surveying, cost estimation, and procurement planning.", "hrs": 6, "mods": 3},
    "Quality Inspection":         {"title": "Quality Inspection & Control", "desc": "Inspection checklists, defect identification, and reporting.", "hrs": 4, "mods": 2},
    "Heavy Equipment Basics":     {"title": "Heavy Equipment Operation Basics", "desc": "Excavator, loader, and crane operation fundamentals.", "hrs": 6, "mods": 3},
    "Project Documentation":      {"title": "Construction Project Documentation", "desc": "RFIs, submittals, daily logs, and change order management.", "hrs": 4, "mods": 2},
}
