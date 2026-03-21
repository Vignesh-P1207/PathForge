"""Skill extraction and gap analysis — PathForge Backend.

Production-quality skill hierarchy covering ALL major role domains:
Data Science, ML/AI, Backend, Frontend, DevOps, Cloud, Mobile,
Data Engineering, Security, Design, Product, QA, Blockchain, Game Dev.
"""

import json
import os
import re
from difflib import SequenceMatcher
from typing import Any

import httpx

# ─────────────────────────────────────────────────────────────────────────────
# SKILL HIERARCHY TREE
# parent -> [children it subsumes]
# If resume has parent >= PARENT_COVERS_CHILD_THRESHOLD, children = NOT a gap.
# Tree is transitive via BFS: Deep Learning -> ML -> Statistics -> Linear Algebra
# ─────────────────────────────────────────────────────────────────────────────
SKILL_TREE: dict[str, list[str]] = {

    # ══════════════════════════════════════════════════════════════════════════
    # PROGRAMMING LANGUAGE ECOSYSTEMS
    # ══════════════════════════════════════════════════════════════════════════

    "Python": [
        # Data stack — anyone writing Python has touched these
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly",
        "Jupyter", "Jupyter Notebook", "Jupyter Lab", "IPython",
        # Scripting
        "Bash", "Shell Scripting", "Shell Script",
        # Testing
        "Pytest", "unittest",
        # Packaging
        "pip", "virtualenv", "Poetry", "conda",
        # Type hints / tooling
        "mypy", "black", "flake8", "pylint",
    ],

    "JavaScript": [
        "jQuery", "ES6", "ES2015", "ES2020",
        "DOM Manipulation", "Async/Await", "Promises", "Fetch API",
        "npm", "yarn", "pnpm",
        "Webpack", "Vite", "Rollup", "Babel", "ESLint", "Prettier",
    ],

    "TypeScript": [
        "JavaScript", "Type Safety", "Interfaces", "Generics",
        "Decorators", "Enums", "Type Guards",
    ],

    "Java": [
        "Maven", "Gradle", "JUnit", "JPA", "Hibernate",
        "Spring", "Spring Boot", "Spring MVC",
        "OOP", "Design Patterns",
    ],

    "Go": [
        "Goroutines", "Channels", "Go Modules",
        "Gin", "Echo", "Fiber",
    ],

    "Rust": [
        "Cargo", "Ownership", "Borrowing", "Lifetimes",
        "Tokio", "Actix",
    ],

    "C++": [
        "STL", "Templates", "Memory Management",
        "CMake", "Boost", "OpenMP",
    ],

    "Kotlin": [
        "Coroutines", "Kotlin Multiplatform",
        "Android Development", "Jetpack Compose",
    ],

    "Swift": [
        "SwiftUI", "UIKit", "Xcode",
        "iOS Development", "Combine",
    ],

    "R": [
        "ggplot2", "dplyr", "tidyr", "tidyverse", "purrr",
        "caret", "randomForest", "xgboost",
        "R Markdown", "Shiny",
        "Statistics", "Data Analysis",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # DATA SCIENCE & MACHINE LEARNING DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Data Science": [
        # Languages
        "Python", "R", "SQL",
        # Core data stack
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly",
        "Jupyter", "Jupyter Notebook",
        # ML
        "Machine Learning", "Statistics",
        # Analysis
        "Data Analysis", "EDA", "Exploratory Data Analysis",
        # Visualization
        "Tableau", "Power BI", "Looker",
        # Concepts
        "Feature Engineering", "A/B Testing", "Hypothesis Testing",
    ],

    "Machine Learning": [
        # Core data stack — ML implies these
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly",
        "Jupyter", "Jupyter Notebook",
        # ML frameworks
        "Scikit-learn", "scikit-learn", "sklearn",
        "XGBoost", "LightGBM", "CatBoost", "AutoML",
        # Math foundations
        "Statistics", "Linear Algebra", "Calculus", "Probability",
        # Concepts
        "Feature Engineering", "A/B Testing", "Hypothesis Testing",
        "Data Analysis", "Exploratory Data Analysis", "EDA",
        "Model Evaluation", "Cross-validation", "Hyperparameter Tuning",
        "Regression", "Classification", "Clustering", "Dimensionality Reduction",
        "Ensemble Methods", "Random Forest", "Gradient Boosting",
        "Overfitting", "Regularization", "Bias-Variance Tradeoff",
    ],

    "Deep Learning": [
        # Inherits full ML stack
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
        "Scikit-learn", "sklearn",
        "Statistics", "Linear Algebra", "Calculus",
        "Feature Engineering",
        # DL frameworks
        "TensorFlow", "PyTorch", "Keras", "JAX",
        # Sub-domains
        "Computer Vision", "NLP", "Natural Language Processing",
        "Transformers", "Hugging Face",
        "Stable Diffusion", "Diffusion Models",
        "Reinforcement Learning",
        # Architectures
        "Neural Networks", "CNN", "RNN", "LSTM", "GAN", "Autoencoder",
        "Attention Mechanism", "BERT", "GPT",
        # Concepts
        "Backpropagation", "Gradient Descent", "Batch Normalization",
        "Dropout", "Transfer Learning", "Fine-tuning",
    ],

    "Data Analysis": [
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
        "Excel", "Google Sheets",
        "SQL", "Tableau", "Power BI", "Looker",
        "Statistics", "EDA", "Exploratory Data Analysis",
        "Data Cleaning", "Data Wrangling",
        "Pivot Tables", "VLOOKUP",
    ],

    "Statistics": [
        "Linear Algebra", "Calculus", "Probability",
        "Hypothesis Testing", "Regression", "Bayesian Statistics",
        "A/B Testing", "Experimental Design",
        "Descriptive Statistics", "Inferential Statistics",
        "ANOVA", "Chi-Square", "T-Test",
        "Confidence Intervals", "P-Value",
    ],

    "NLP": [
        "NLTK", "spaCy", "Gensim",
        "Transformers", "BERT", "GPT", "T5", "RoBERTa",
        "Hugging Face",
        "Text Mining", "Sentiment Analysis",
        "Named Entity Recognition", "NER",
        "Text Classification", "Topic Modeling", "LDA",
        "Word Embeddings", "Word2Vec", "GloVe", "FastText",
        "Tokenization", "Lemmatization", "Stemming",
        "Pandas", "NumPy",
    ],
    "Natural Language Processing": [
        "NLTK", "spaCy", "Gensim",
        "Transformers", "BERT", "GPT",
        "Hugging Face", "Text Mining", "Sentiment Analysis",
        "Named Entity Recognition", "NER",
        "Pandas", "NumPy",
    ],

    "Computer Vision": [
        "OpenCV", "PIL", "Pillow", "scikit-image",
        "NumPy", "Matplotlib",
        "Object Detection", "Image Segmentation", "Image Classification",
        "YOLO", "ResNet", "VGG", "EfficientNet",
        "Data Augmentation",
    ],

    "LLM": [
        "LangChain", "LlamaIndex",
        "RAG", "Retrieval Augmented Generation",
        "Prompt Engineering", "Fine-tuning", "RLHF",
        "Embeddings", "Semantic Search",
        "Vector Database", "Pinecone", "Weaviate", "ChromaDB", "Qdrant",
        "LLMOps", "Hugging Face", "Transformers",
        "OpenAI", "GPT", "BERT", "Claude", "Gemini",
        "Function Calling", "Tool Use", "Agents",
    ],
    "Generative AI": [
        "LLM", "LangChain", "RAG", "Prompt Engineering",
        "Stable Diffusion", "Diffusion Models", "DALL-E", "Midjourney",
        "Hugging Face", "Fine-tuning", "LoRA", "PEFT",
    ],

    "MLOps": [
        "MLflow", "Kubeflow", "Weights & Biases", "W&B",
        "DataOps", "Model Monitoring", "Model Registry",
        "Feature Store", "Feast",
        "Docker", "Kubernetes",
        "CI/CD", "GitHub Actions",
        "Airflow", "Prefect", "Dagster",
        "DVC", "CML",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # DATA ENGINEERING DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Data Engineering": [
        "ETL", "ELT", "Data Pipeline",
        "Data Warehouse", "Data Lake", "Data Lakehouse",
        "Data Modeling", "Data Governance", "Data Quality",
        "Fivetran", "Stitch", "Airbyte",
        "Great Expectations", "dbt",
        "Prefect", "Luigi", "Dagster", "Airflow",
        "SQL", "Python",
        "Snowflake", "BigQuery", "Redshift", "Databricks",
    ],

    "Apache Spark": [
        "Hadoop", "Hive", "Pig", "MapReduce",
        "Databricks", "Delta Lake",
        "Spark SQL", "PySpark", "Spark Streaming",
        "MLlib",
    ],
    "Spark": [
        "Hadoop", "Hive", "Pig", "MapReduce",
        "Databricks", "Spark SQL", "PySpark", "Spark Streaming",
    ],

    "Big Data": [
        "Apache Spark", "Spark", "Hadoop", "Hive", "HBase",
        "Kafka", "Apache Kafka",
        "Databricks", "Snowflake", "BigQuery", "Redshift",
        "Flink", "Apache Flink",
    ],

    "SQL": [
        "MySQL", "SQLite", "MariaDB",
        "Query Optimization", "Joins", "Aggregations",
        "Stored Procedures", "Views", "Indexes",
        "Window Functions", "CTEs", "Subqueries",
        "ACID", "Transactions",
    ],
    "PostgreSQL": [
        "SQL", "Query Optimization", "Indexing",
        "Database Administration", "JSONB",
        "Partitioning", "Replication",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # CLOUD PLATFORMS
    # ══════════════════════════════════════════════════════════════════════════

    "AWS": [
        "Amazon Web Services",
        "S3", "EC2", "Lambda", "RDS", "DynamoDB",
        "SageMaker", "Bedrock",
        "CloudFormation", "CDK", "IAM",
        "EKS", "ECS", "Fargate",
        "API Gateway", "CloudFront", "Route 53",
        "SNS", "SQS", "EventBridge",
        "Glue", "Athena", "EMR",
        "VPC", "Security Groups",
    ],
    "GCP": [
        "Google Cloud",
        "BigQuery", "Cloud Storage", "Pub/Sub",
        "Vertex AI", "Cloud Run", "GKE",
        "Cloud Functions", "Dataflow", "Dataproc",
        "Cloud SQL", "Firestore", "Spanner",
        "Cloud Build", "Artifact Registry",
    ],
    "Azure": [
        "Azure ML", "Azure DevOps", "AKS",
        "Azure Functions", "Cosmos DB", "Azure Blob Storage",
        "Azure SQL", "Azure Data Factory",
        "Azure Synapse", "Azure OpenAI",
        "Azure AD", "Key Vault",
        "Logic Apps", "Service Bus",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # DEVOPS / INFRASTRUCTURE DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "DevOps": [
        "Docker", "Kubernetes", "CI/CD",
        "Terraform", "Ansible", "Puppet", "Chef",
        "Prometheus", "Grafana", "Datadog", "New Relic",
        "Linux", "Bash",
        "Git", "GitHub", "GitLab",
        "Nginx", "HAProxy",
        "ELK Stack", "Elasticsearch", "Logstash", "Kibana",
        "Monitoring", "Alerting", "Incident Management",
        "SRE", "Reliability Engineering",
    ],

    "Kubernetes": [
        "Helm", "ArgoCD", "Flux", "Istio", "Envoy", "K8s",
        "kubectl", "Container Orchestration",
        "Kustomize", "Operators",
        "Service Mesh", "Ingress",
    ],

    "Docker": [
        "Containerization", "Docker Compose",
        "Container Registry", "Dockerfile",
        "Multi-stage Builds", "Docker Swarm",
    ],

    "CI/CD": [
        "Jenkins", "GitHub Actions", "GitLab CI",
        "CircleCI", "Travis CI", "ArgoCD",
        "Automated Testing", "Deployment Pipelines",
        "Blue-Green Deployment", "Canary Deployment",
        "Infrastructure as Code",
    ],

    "Infrastructure as Code": [
        "Terraform", "Ansible", "Pulumi",
        "CloudFormation", "CDK", "Bicep",
        "Chef", "Puppet",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # BACKEND DEVELOPMENT DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Backend Development": [
        "Python", "Java", "Go", "Node.js", "Ruby", "PHP", "Rust",
        "REST API", "GraphQL", "gRPC",
        "Django", "FastAPI", "Flask", "Spring Boot",
        "Express", "NestJS", "Rails",
        "SQL", "PostgreSQL", "MongoDB", "Redis",
        "Authentication", "Authorization", "OAuth", "JWT",
        "Microservices", "API Design",
        "Caching", "Message Queue",
    ],

    "Node.js": [
        "Express", "Express.js", "NestJS", "Fastify", "Koa",
        "npm", "yarn",
        "REST API", "Middleware", "Event Loop",
        "Streams", "Buffers",
    ],

    "Django": [
        "Python", "REST API", "ORM",
        "Django REST Framework", "DRF",
        "Celery", "Django Channels",
        "Authentication", "Permissions",
    ],

    "FastAPI": [
        "Python", "REST API", "Pydantic",
        "Async", "Uvicorn", "Starlette",
        "OpenAPI", "Swagger",
    ],

    "Spring Boot": [
        "Java", "REST API", "JPA", "Hibernate",
        "Maven", "Gradle",
        "Spring Security", "Spring Data",
        "Microservices",
    ],

    "Microservices": [
        "Docker", "Kubernetes",
        "API Gateway", "Service Discovery",
        "Circuit Breaker", "Load Balancing",
        "Message Queue", "RabbitMQ", "Kafka",
        "Distributed Tracing",
    ],

    "System Design": [
        "Microservices", "Distributed Systems", "Event-Driven Architecture",
        "CQRS", "Event Sourcing",
        "Domain-Driven Design", "DDD",
        "Clean Architecture", "Hexagonal Architecture",
        "Load Balancing", "Caching", "CDN",
        "Message Queue", "API Design",
        "Scalability", "High Availability",
        "CAP Theorem", "Consistency", "Availability",
        "Database Sharding", "Replication",
        "Rate Limiting", "Circuit Breaker",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # FRONTEND DEVELOPMENT DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Frontend Development": [
        "HTML", "HTML5", "CSS", "CSS3",
        "JavaScript", "TypeScript",
        "React", "Vue.js", "Angular", "Svelte",
        "Next.js", "Nuxt.js",
        "Responsive Design", "Accessibility", "WCAG",
        "Webpack", "Vite",
        "REST API", "GraphQL",
        "Testing", "Jest", "Cypress",
    ],

    "React": [
        "Redux", "Zustand", "Recoil",
        "React Native", "React Hooks",
        "JSX", "React Router", "Context API",
        "React Query", "SWR",
        "Next.js",
    ],

    "Vue.js": [
        "Vuex", "Pinia", "Vue Router",
        "Nuxt.js", "Composition API",
        "Vite",
    ],

    "Angular": [
        "TypeScript", "RxJS",
        "NgRx", "Angular Material",
        "Angular CLI", "Dependency Injection",
    ],

    "CSS": [
        "CSS3", "SASS", "SCSS", "Less",
        "Tailwind CSS", "Bootstrap",
        "Flexbox", "CSS Grid",
        "Animations", "Responsive Design",
        "BEM", "CSS Modules",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # MOBILE DEVELOPMENT DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Mobile Development": [
        "React Native", "Flutter", "Expo",
        "iOS", "Android",
        "Swift", "SwiftUI", "Kotlin",
        "Xamarin", "Ionic", "Cordova",
        "PWA", "Push Notifications",
        "App Store", "Play Store",
        "Mobile UI/UX",
    ],

    "Flutter": [
        "Dart", "Widgets", "State Management",
        "Provider", "Bloc", "Riverpod",
        "Firebase", "Platform Channels",
    ],

    "React Native": [
        "JavaScript", "TypeScript",
        "Expo", "React Navigation",
        "Redux", "Native Modules",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # SECURITY DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Cybersecurity": [
        "Penetration Testing", "Ethical Hacking",
        "OWASP", "OWASP Top 10",
        "Network Security", "Firewall", "IDS", "IPS",
        "Cryptography", "PKI", "TLS", "SSL",
        "Authentication", "Authorization", "OAuth", "JWT",
        "Vulnerability Assessment", "SAST", "DAST",
        "Incident Response", "Forensics",
        "Compliance", "GDPR", "SOC 2", "ISO 27001",
        "Burp Suite", "Metasploit", "Nmap", "Wireshark",
        "SIEM", "Splunk",
    ],

    "Security": [
        "OWASP", "Authentication", "Authorization",
        "OAuth", "JWT", "TLS", "SSL",
        "Encryption", "Hashing",
        "Vulnerability Assessment",
        "Secure Coding",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # DESIGN / UX DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "UX Design": [
        "User Research", "Usability Testing",
        "Wireframing", "Prototyping",
        "Figma", "Sketch", "Adobe XD", "InVision",
        "Information Architecture", "User Flows",
        "Accessibility", "WCAG",
        "Design Systems", "Component Libraries",
        "A/B Testing", "Heatmaps",
        "Persona", "Journey Mapping",
    ],

    "UI Design": [
        "Figma", "Sketch", "Adobe XD",
        "Typography", "Color Theory", "Layout",
        "Design Systems", "Component Libraries",
        "Responsive Design", "Mobile Design",
        "Prototyping", "Wireframing",
        "CSS", "HTML",
    ],

    "Figma": [
        "Prototyping", "Wireframing",
        "Auto Layout", "Components", "Variants",
        "Design Systems", "Plugins",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # PRODUCT MANAGEMENT DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Product Management": [
        "Product Strategy", "Roadmapping", "Prioritization",
        "User Stories", "Acceptance Criteria",
        "Agile", "Scrum", "Kanban",
        "Jira", "Confluence", "Notion",
        "A/B Testing", "Analytics",
        "Stakeholder Management", "Cross-functional",
        "Market Research", "Competitive Analysis",
        "OKRs", "KPIs", "Metrics",
        "Go-to-Market", "Product Launch",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # QA / TESTING DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Quality Assurance": [
        "Manual Testing", "Automated Testing",
        "Unit Testing", "Integration Testing", "E2E Testing",
        "TDD", "BDD",
        "Selenium", "Cypress", "Playwright",
        "Jest", "Pytest", "JUnit",
        "Postman", "API Testing",
        "Load Testing", "Performance Testing",
        "JMeter", "k6", "Locust",
        "Test Planning", "Test Cases", "Bug Reporting",
        "JIRA", "TestRail",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # BLOCKCHAIN DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Blockchain": [
        "Solidity", "Smart Contracts",
        "Ethereum", "Web3.js", "Ethers.js",
        "DeFi", "NFT", "DAO",
        "Hardhat", "Truffle", "Foundry",
        "IPFS", "Chainlink",
        "Consensus Mechanisms", "Proof of Work", "Proof of Stake",
        "Cryptography",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # VISUALIZATION / BI DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Tableau": [
        "Data Visualization", "Dashboards",
        "Calculated Fields", "Tableau Server", "Tableau Prep",
        "LOD Expressions",
    ],

    "Power BI": [
        "DAX", "Power Query", "M Language",
        "Data Visualization", "Dashboards",
        "Data Modeling", "Report Builder",
        "Power BI Service", "Power BI Desktop",
    ],

    "Data Visualization": [
        "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Altair",
        "D3.js", "Chart.js",
        "Tableau", "Power BI", "Looker",
        "Dashboards", "Storytelling with Data",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # GAME DEVELOPMENT DOMAIN
    # ══════════════════════════════════════════════════════════════════════════

    "Game Development": [
        "Unity", "Unreal Engine", "Godot",
        "C#", "C++", "GDScript",
        "3D Modeling", "Blender",
        "Physics Engine", "Collision Detection",
        "Shader Programming", "HLSL", "GLSL",
        "Game Design", "Level Design",
        "Multiplayer", "Networking",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # AGILE / SOFT SKILLS
    # ══════════════════════════════════════════════════════════════════════════

    "Agile": [
        "Scrum", "Kanban", "SAFe",
        "Sprint Planning", "Retrospectives", "Daily Standup",
        "User Stories", "Backlog Grooming",
        "Jira", "Confluence",
        "Velocity", "Burndown Charts",
    ],

    "Leadership": [
        "Team Management", "Mentoring", "Coaching",
        "Stakeholder Management", "Cross-functional",
        "Communication", "Presentation",
        "Strategic Thinking", "Decision Making",
        "Conflict Resolution",
    ],
}

# ── Reverse map: child_lower -> [parent names that cover it] ──────────────────
_CHILD_TO_PARENTS: dict[str, list[str]] = {}
for _parent, _children in SKILL_TREE.items():
    for _child in _children:
        _key = _child.lower()
        if _key not in _CHILD_TO_PARENTS:
            _CHILD_TO_PARENTS[_key] = []
        _CHILD_TO_PARENTS[_key].append(_parent)

# Proficiency threshold: parent >= this means all its children are covered
PARENT_COVERS_CHILD_THRESHOLD = 70

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# ── Ollama availability flag — set once at startup via check_ollama_health() ──
_OLLAMA_AVAILABLE: bool = True


async def check_ollama_health() -> bool:
    """Probe Ollama once at startup. Sets module-level flag to avoid per-call timeouts."""
    global _OLLAMA_AVAILABLE
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            _OLLAMA_AVAILABLE = True
            print(f"[INFO] Ollama reachable at {OLLAMA_URL} — LLM mode active")
    except Exception:
        _OLLAMA_AVAILABLE = False
        print(f"[INFO] Ollama not available — running in regex-only mode")
    return _OLLAMA_AVAILABLE

# ── Comprehensive skill patterns ──────────────────────────────────────────────
SKILL_PATTERNS: list[str] = [
    # Programming Languages
    r'\b(Python|Java(?:Script)?|TypeScript|C\+\+|C#|Ruby|Go(?:lang)?|Rust|PHP|Swift|Kotlin|Scala|R\b|MATLAB|Perl|Haskell|Elixir|Clojure|Dart|Julia|Lua|Groovy|Objective-C|Solidity|GDScript)\b',
    # Web Frontend
    r'\b(React(?:\.js)?|Angular(?:JS)?|Vue(?:\.js)?|Next\.js|Nuxt(?:\.js)?|Svelte|Remix|Gatsby|Ember(?:\.js)?|Backbone(?:\.js)?|jQuery|HTML5?|CSS3?|SASS|SCSS|Less|Tailwind(?:\s*CSS)?|Bootstrap|Material(?:\s*UI)?|Chakra(?:\s*UI)?|Ant(?:\s*Design)?|Storybook|WebAssembly|D3(?:\.js)?|Chart\.js)\b',
    # Web Backend
    r'\b(Node(?:\.js)?|Express(?:\.js)?|Django|Flask|FastAPI|Spring(?:\s*Boot)?|ASP\.NET|Laravel|Rails|Gin|Echo|Fiber|NestJS|Hapi|Koa|Fastify|Tornado|Pyramid|Bottle|Sinatra|Phoenix|Actix)\b',
    # Databases
    r'\b(SQL|MySQL|PostgreSQL|SQLite|MongoDB|Redis|Cassandra|Oracle|DynamoDB|Elasticsearch|Neo4j|CouchDB|InfluxDB|TimescaleDB|Snowflake|BigQuery|Redshift|Databricks|Pinecone|Weaviate|ChromaDB|Qdrant|MariaDB|MS\s*SQL(?:\s*Server)?|Firebase(?:\s*Firestore)?|Supabase|PlanetScale)\b',
    # Cloud Platforms
    r'\b(AWS|Amazon\s*Web\s*Services|Azure|GCP|Google\s*Cloud|Heroku|Vercel|Netlify|DigitalOcean|Cloudflare|Linode|IBM\s*Cloud|Oracle\s*Cloud|Alibaba\s*Cloud)\b',
    # DevOps & Infrastructure
    r'\b(Docker|Kubernetes|K8s|Helm|Terraform|Ansible|Chef|Puppet|Vagrant|Jenkins|GitLab(?:\s*CI)?|GitHub\s*Actions|CircleCI|Travis\s*CI|ArgoCD|Flux|Istio|Envoy|Nginx|HAProxy|Prometheus|Grafana|Datadog|New\s*Relic|Splunk|ELK\s*Stack|Logstash|Kibana|Pulumi|CDK)\b',
    # Data & ML
    r'\b(Machine\s*Learning|Deep\s*Learning|TensorFlow|PyTorch|Keras|JAX|Scikit-learn|Pandas|NumPy|SciPy|Matplotlib|Seaborn|Plotly|Bokeh|Altair|Tableau|Power\s*BI|Looker|Metabase|Apache\s*Spark|Apache\s*Kafka|Apache\s*Flink|Apache\s*Beam|Apache\s*Airflow|Hadoop|Hive|Pig|MLflow|Kubeflow|Weights\s*&\s*Biases|Hugging\s*Face|LangChain|LlamaIndex|OpenCV|NLTK|spaCy|Gensim|Transformers|XGBoost|LightGBM|CatBoost|AutoML|Feature\s*Engineering|A/B\s*Testing|Statistics|Linear\s*Algebra|Calculus|DVC|Feast|Delta\s*Lake|Data\s*Analysis|EDA|Exploratory\s*Data\s*Analysis)\b',
    # AI & LLM
    r'\b(LLM|Large\s*Language\s*Model|GPT|BERT|RAG|Retrieval\s*Augmented\s*Generation|Prompt\s*Engineering|Fine-tuning|Vector\s*Database|Embeddings|Semantic\s*Search|NLP|Natural\s*Language\s*Processing|Computer\s*Vision|Reinforcement\s*Learning|Generative\s*AI|Diffusion\s*Models|Stable\s*Diffusion|MLOps|DataOps|LLMOps|LoRA|PEFT|RLHF)\b',
    # APIs & Architecture
    r'\b(REST(?:ful)?(?:\s*API)?|GraphQL|gRPC|WebSocket|WebRTC|OAuth|JWT|OpenAPI|Swagger|Microservices|Serverless|Event-Driven|CQRS|Event\s*Sourcing|Domain-Driven\s*Design|DDD|Clean\s*Architecture|Hexagonal\s*Architecture|System\s*Design|Distributed\s*Systems|Message\s*Queue|RabbitMQ|Apache\s*Kafka|NATS|Celery|Redis\s*Queue|Service\s*Mesh)\b',
    # Testing
    r'\b(Jest|Pytest|JUnit|Selenium|Cypress|Playwright|Mocha|Chai|Jasmine|Karma|PHPUnit|RSpec|Go\s*Test|Unit\s*Testing|Integration\s*Testing|E2E\s*Testing|TDD|BDD|Load\s*Testing|Performance\s*Testing|Postman|Insomnia|JMeter|k6|Locust|TestRail)\b',
    # Tools & Practices
    r'\b(Git|GitHub|GitLab|Bitbucket|Jira|Confluence|Notion|Agile|Scrum|Kanban|CI/CD|DevOps|SRE|Linux|Unix|Bash|Shell\s*Script(?:ing)?|PowerShell|Webpack|Vite|Rollup|Babel|ESLint|Prettier|SonarQube|OWASP|Penetration\s*Testing|Security|Kafka|Airflow|dbt|Spark|Flink|Databricks|Snowflake|Redshift|BigQuery|Terraform|Ansible)\b',
    # Mobile
    r'\b(React\s*Native|Flutter|iOS|Android|Swift(?:UI)?|Kotlin(?:\s*Multiplatform)?|Xamarin|Ionic|Cordova|Expo|PWA|Mobile\s*Development|Jetpack\s*Compose)\b',
    # Data Engineering
    r'\b(ETL|ELT|Data\s*Pipeline|Data\s*Warehouse|Data\s*Lake(?:house)?|Data\s*Modeling|Data\s*Governance|Data\s*Quality|Apache\s*Beam|Fivetran|Stitch|Airbyte|dbt|Great\s*Expectations|Prefect|Luigi|Dagster|PySpark|Spark\s*SQL)\b',
    # Design & UX
    r'\b(Figma|Sketch|Adobe\s*XD|InVision|Zeplin|Wireframing|Prototyping|User\s*Research|Usability\s*Testing|UX\s*Design|UI\s*Design|Design\s*Systems|Information\s*Architecture|User\s*Flows|Accessibility|WCAG|Typography|Color\s*Theory)\b',
    # Security
    r'\b(Cybersecurity|Penetration\s*Testing|Ethical\s*Hacking|OWASP|Cryptography|PKI|TLS|SSL|Vulnerability\s*Assessment|SAST|DAST|Incident\s*Response|SIEM|Burp\s*Suite|Metasploit|Nmap|Wireshark|GDPR|SOC\s*2|ISO\s*27001)\b',
    # Blockchain
    r'\b(Solidity|Smart\s*Contracts|Ethereum|Web3(?:\.js)?|Ethers(?:\.js)?|DeFi|NFT|DAO|Hardhat|Truffle|Foundry|IPFS|Chainlink|Blockchain)\b',
    # Game Dev
    r'\b(Unity|Unreal\s*Engine|Godot|Game\s*Development|Shader\s*Programming|HLSL|GLSL|Blender|Level\s*Design|Game\s*Design)\b',
    # Soft Skills
    r'\b(Leadership|Communication|Problem\s*Solving|Critical\s*Thinking|Team\s*Collaboration|Project\s*Management|Time\s*Management|Mentoring|Stakeholder\s*Management|Cross-functional|Agile|Scrum|Kanban|Product\s*Management|Strategic\s*Thinking)\b',
]

# ── Proficiency context keywords ──────────────────────────────────────────────
_EXPERT_KEYWORDS = [
    "expert", "advanced", "senior", "lead", "architect", "principal",
    "extensive", "deep", "mastery", "proficient", "strong", "specialist",
    "years of experience", "yr experience", "yrs experience",
    "5+", "6+", "7+", "8+", "10+",
]
_MID_KEYWORDS = [
    "intermediate", "mid", "working knowledge", "familiar", "experience with",
    "used", "developed", "built", "implemented", "worked with",
    "2+", "3+", "4+",
]
_BEGINNER_KEYWORDS = [
    "basic", "beginner", "learning", "exposure", "introductory",
    "fundamental", "entry", "1+", "fresher", "intern",
]

# ── Category mapping ──────────────────────────────────────────────────────────
_CLOUD_SKILLS = {
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify",
    "digitalocean", "cloudflare", "amazon web services", "linode",
    "ibm cloud", "oracle cloud",
}
_TOOL_SKILLS = {
    "docker", "kubernetes", "k8s", "git", "github", "gitlab", "jenkins",
    "terraform", "ansible", "helm", "jira", "confluence", "notion",
    "figma", "sketch", "adobe xd",
}
_SOFT_SKILLS = {
    "leadership", "communication", "problem solving", "critical thinking",
    "team collaboration", "project management", "mentoring",
    "stakeholder management", "cross-functional", "strategic thinking",
}


def _get_category(skill: str) -> str:
    s = skill.lower()
    if s in _CLOUD_SKILLS:
        return "cloud"
    if s in _TOOL_SKILLS:
        return "tool"
    if s in _SOFT_SKILLS:
        return "soft"
    return "technical"


def _get_proficiency_from_context(text: str, skill: str, doc_type: str) -> int:
    """Estimate proficiency from context window around each skill mention."""
    skill_lower = skill.lower()
    text_lower = text.lower()

    positions = [m.start() for m in re.finditer(re.escape(skill_lower), text_lower)]
    if not positions:
        return 60 if doc_type == "resume" else 80

    max_prof = 0
    for pos in positions:
        window = text_lower[max(0, pos - 100): pos + 100]
        if any(kw in window for kw in _EXPERT_KEYWORDS):
            max_prof = max(max_prof, 90)
        elif any(kw in window for kw in _MID_KEYWORDS):
            max_prof = max(max_prof, 70)
        elif any(kw in window for kw in _BEGINNER_KEYWORDS):
            max_prof = max(max_prof, 45)
        else:
            max_prof = max(max_prof, 60)

    freq_boost = min(len(positions) * 5, 15)
    base = max_prof + freq_boost

    if doc_type == "job description":
        return min(base + 10, 95)
    return min(base, 95)


def _build_covered_set(resume_map: dict[str, dict[str, Any]]) -> set[str]:
    """BFS transitive walk: collect every skill covered by resume's root skills.

    Deep Learning (95%) -> TensorFlow, PyTorch, NLP, Pandas, NumPy, sklearn,
    Statistics, Linear Algebra, NLTK, spaCy ... all covered transitively.
    """
    covered: set[str] = set()
    queue: list[str] = []

    for res_key, res_skill in resume_map.items():
        if int(res_skill.get("proficiency", 0)) >= PARENT_COVERS_CHILD_THRESHOLD:
            queue.append(res_key)

    visited: set[str] = set()
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        for parent_name, children in SKILL_TREE.items():
            if parent_name.lower() == current:
                for child in children:
                    child_lower = child.lower()
                    covered.add(child_lower)
                    if child_lower not in visited:
                        queue.append(child_lower)

    return covered


def _extract_skills_section(text: str) -> set[str]:
    """Extract skills that appear in a dedicated Skills/Technical Skills section.

    Returns a set of lowercased skill names found in that section.
    Skills listed here are explicitly declared by the candidate — highest priority.
    """
    # Match common section headers for skills
    section_pattern = re.compile(
        r'(?:^|\n)\s*(?:technical\s+skills?|skills?|core\s+competenc(?:y|ies)|'
        r'key\s+skills?|proficiencies|tools?\s+&\s+technologies?|'
        r'technologies?|expertise|competenc(?:y|ies))\s*[:\-–—]?\s*\n'
        r'([\s\S]{20,800}?)(?=\n\s*(?:[A-Z][A-Z\s]{3,}|$))',
        re.IGNORECASE | re.MULTILINE,
    )
    section_skills: set[str] = set()
    for sec_match in section_pattern.finditer(text):
        section_text = sec_match.group(1)
        for pattern in SKILL_PATTERNS:
            for m in re.finditer(pattern, section_text, re.IGNORECASE):
                raw = m.group(1)
                skill = re.sub(r'\s+', ' ', raw).strip()
                section_skills.add(skill.lower())
    return section_skills


def _normalize_skill_name(raw: str) -> str:
    """Normalize a matched skill name."""
    skill = re.sub(r'\s+', ' ', raw).strip()
    # Don't strip .js — keep "Node.js", "Vue.js" etc. intact
    if skill.lower() == "r":
        return "R"
    if skill.lower() in ("go", "golang"):
        return "Go"
    return skill


def _extract_skills_regex(text: str, doc_type: str) -> list[dict[str, Any]]:
    """Regex extraction with section-aware prioritization and hierarchy deduplication.

    For resumes: skills found in the dedicated Skills section are ranked first
    and given a proficiency boost — they are explicitly declared by the candidate.
    Skills only found in project descriptions are ranked lower.
    """
    # For resumes, identify which skills are in the explicit skills section
    section_skills: set[str] = set()
    if doc_type == "resume":
        section_skills = _extract_skills_section(text)

    skills_found: dict[str, int] = {}  # skill_name_lower -> mention count
    skills_casing: dict[str, str] = {} # skill_name_lower -> actual displayed name

    for pattern in SKILL_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(1)
            skill = _normalize_skill_name(raw)
            skill_lower = skill.lower()
            
            skills_found[skill_lower] = skills_found.get(skill_lower, 0) + 1
            if skill_lower not in skills_casing:
                skills_casing[skill_lower] = skill

    raw_result: list[dict[str, Any]] = []
    for skill_lower, _count in skills_found.items():
        skill = skills_casing[skill_lower]
        prof = _get_proficiency_from_context(text, skill, doc_type)
        in_section = skill_lower in section_skills
        # Boost skills explicitly listed in the skills section
        if in_section and doc_type == "resume":
            prof = min(prof + 15, 95)
        raw_result.append({
            "name": skill,
            "proficiency": prof,
            "category": _get_category(skill),
            "_in_section": in_section,
        })

    synthetic_map = {s["name"].lower(): s for s in raw_result}
    
    # Only suppress child skills for job descriptions or inferred skills. 
    # For resumes, what they wrote is what they get.
    if doc_type == "resume":
        suppressed = set()
    else:
        suppressed = _build_covered_set(synthetic_map)

    deduped = [s for s in raw_result if s["name"].lower() not in suppressed]

    if doc_type == "resume" and section_skills:
        # Sort: section skills first (by proficiency), then rest (by proficiency)
        section_items = sorted(
            [s for s in deduped if s.get("_in_section")],
            key=lambda x: x["proficiency"], reverse=True
        )
        other_items = sorted(
            [s for s in deduped if not s.get("_in_section")],
            key=lambda x: x["proficiency"], reverse=True
        )
        deduped = section_items + other_items
    else:
        deduped.sort(key=lambda x: x["proficiency"], reverse=True)

    # Clean internal flag before returning
    for s in deduped:
        s.pop("_in_section", None)

    # Return up to 35 for resumes so we don't truncate their actual list, 20 for JD
    return deduped[:35] if doc_type == "resume" else deduped[:20]


async def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama API and return response text. Short-circuits immediately if offline."""
    if not _OLLAMA_AVAILABLE:
        return ""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data.get("response", ""))
    except Exception:
        return ""


def _extract_json(text: str) -> str:
    """Robustly extract JSON from LLM output."""
    text = text.strip()
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    for i, ch in enumerate(text):
        if ch in ('[', '{'):
            return text[i:]
    return text


async def extract_skills(text: str, doc_type: str) -> list[dict[str, Any]]:
    """Extract skills — Ollama first, regex fallback."""
    # For resumes, use exact matching to guarantee 100% accuracy and ZERO hallucination
    if doc_type == "resume":
        print(f"[INFO] Using exact regex extraction for {doc_type} to prevent hallucination")
        return _extract_skills_regex(text, doc_type)

    prompt = (
        "/no_think\n"
        f"You are a skill extraction engine. Extract ALL technical and professional skills "
        f"from this {doc_type}. Include programming languages, frameworks, tools, cloud platforms, "
        f"methodologies, domain knowledge, and soft skills.\n"
        f"Output ONLY a raw JSON array. No explanation. No markdown. No extra text.\n"
        f'Format: [{{"name": "Python", "proficiency": 85, "category": "technical"}}, ...]\n'
        f"proficiency: 0-100 integer based on context clues (years, level, frequency).\n"
        f"category: one of technical, tool, cloud, soft.\n\n"
        f"Document:\n{text[:4000]}"
    )

    raw = await call_ollama(prompt)
    if raw:
        json_str = _extract_json(raw)
        try:
            parsed: Any = json.loads(json_str)
            result: list[dict[str, Any]] = []
            items = (
                parsed if isinstance(parsed, list)
                else parsed.get("skills", []) if isinstance(parsed, dict)
                else []
            )
            for item in items:
                if isinstance(item, dict) and item.get("name"):
                    result.append({
                        "name": str(item["name"]).strip(),
                        "proficiency": max(10, min(100, int(item.get("proficiency", 60)))),
                        "category": str(item.get("category", "technical")),
                    })
            if len(result) >= 3:
                print(f"[INFO] Ollama extracted {len(result)} skills from {doc_type}")
                return result
        except Exception as e:
            print(f"[WARN] Ollama JSON parse failed: {e}")

    print(f"[INFO] Using regex extraction for {doc_type}")
    return _extract_skills_regex(text, doc_type)


def compute_gap(
    resume_skills: list[dict[str, Any]],
    jd_skills: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute skill gap with transitive hierarchy resolution.

    Examples:
    - Resume: Deep Learning 95% -> Pandas, NumPy, TensorFlow, NLP, sklearn NOT gaps
    - Resume: DevOps 90% -> Docker, Kubernetes, CI/CD, Terraform NOT gaps
    - Resume: System Design 85% -> Microservices, Distributed Systems NOT gaps
    - Resume: AWS 80% -> S3, EC2, Lambda, DynamoDB NOT gaps
    """
    resume_map: dict[str, dict[str, Any]] = {
        s["name"].lower(): s for s in resume_skills if s.get("name")
    }

    covered_by_parent: set[str] = _build_covered_set(resume_map)

    matched: list[tuple[dict[str, Any], dict[str, Any], float]] = []
    gaps: list[dict[str, Any]] = []

    for jd_skill in jd_skills:
        jd_name = jd_skill.get("name", "")
        if not jd_name:
            continue

        jd_lower = jd_name.lower()

        # Covered transitively by a parent/ancestor
        if jd_lower in covered_by_parent:
            synthetic = {
                "name": jd_name,
                "proficiency": PARENT_COVERS_CHILD_THRESHOLD,
                "category": jd_skill.get("category", "technical"),
            }
            matched.append((jd_skill, synthetic, 1.0))
            continue

        # Direct fuzzy match
        best_key: str | None = None
        best_ratio = 0.0

        if jd_lower in resume_map:
            best_key = jd_lower
            best_ratio = 1.0
        else:
            for res_key in resume_map:
                ratio = SequenceMatcher(None, jd_lower, res_key).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_key = res_key

        if best_key and best_ratio >= 0.72:
            res_skill = resume_map[best_key]
            jd_prof = int(jd_skill.get("proficiency", 80))
            res_prof = int(res_skill.get("proficiency", 50))
            ratio = res_prof / jd_prof if jd_prof > 0 else 1.0
            matched.append((jd_skill, res_skill, ratio))
        else:
            gaps.append(jd_skill)

    total = len(jd_skills)
    match_pct = round(len(matched) / total * 100) if total else 0
    time_saved_pct = round(len(matched) / total * 100) if total else 0

    return {
        "matched": matched,
        "gaps": gaps,
        "match_pct": match_pct,
        "time_saved_pct": time_saved_pct,
    }
