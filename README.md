# PATHFORGE

> AI-powered skill gap analyzer, learning path generator, and interview readiness predictor — built for IISc submission.

PathForge takes a candidate's resume and a job description, then produces a complete, personalized upskilling roadmap with ATS scoring, competency radar, interview prep questions, and a downloadable PDF report. Everything runs locally — no cloud APIs, no data leaves your machine.

---

## What It Does

Upload a resume + job description (file, pasted text, or URL). PathForge:

1. Extracts skills from both documents using 200+ regex patterns across 14 categories
2. Runs a transitive skill hierarchy match (e.g. "Deep Learning" covers TensorFlow, PyTorch, NLP, NumPy automatically)
3. Computes a match score, identifies critical gaps, and builds a DAG-ordered learning path
4. Scores the resume against ATS criteria across 5 weighted dimensions
5. Generates an interview readiness report with likely questions and prep strategies
6. Produces a downloadable PDF report

All skill extraction works offline via regex. Ollama (local LLM) is used only for generating training module descriptions for unknown skills — the app is fully functional without it.

---

## Key Features

### Single Resume Analyzer
- Upload resume (PDF, DOCX, TXT) + job description
- Match score, critical gap count, time-saved percentage
- Skill proficiency bars for current vs. required skills
- Competency radar chart (canvas-based, no chart library)
- AI reasoning trace showing every decision step
- DAG-ordered learning pathway with week estimates

### ATS Compatibility Panel
- 5-dimension scoring: keyword match (35%), format/structure (20%), section coverage (20%), quantification (15%), action verbs (10%)
- Keyword hit/miss lists, section presence check, improvement tips
- Animated ring gauge

### Interview Readiness Predictor
- Confidence arc gauge (0–100%)
- Readiness level: Not Ready / Partially Ready / Interview Ready
- Danger zones: top gap skills with 2 likely interview questions each + prep strategy
- Strong zones: top matched skills with showcase questions
- 30+ pre-built question banks; Ollama fallback for unknown skills

### Bulk Resume Analyzer
- Upload multiple resumes against one JD
- Ranked leaderboard with match scores, top skills, critical gaps
- Common gaps across all candidates

### Standalone ATS Scanner
- Resume-only or resume + JD scan
- Formatting issue detection (word count, email, phone)
- Keyword and section analysis

### Multi-Site JD Scraper
- Paste a job URL — scraper handles LinkedIn, Indeed, Naukri, Glassdoor, Internshala, Wellfound, Greenhouse, Lever, Workday, Monster, ZipRecruiter
- JSON-LD schema.org/JobPosting extraction as primary strategy
- Company name auto-detected from URL domain
- Graceful fallback with user-friendly error messages when sites block bots

### Operational Role Support
- 6 operational/labor role templates: Warehouse/Logistics, Retail/Store Ops, Field Technician, Healthcare Support, Hospitality/F&B, Construction/Site
- Template skills supplement extracted JD skills (not replace them)
- 45+ pre-built quick modules for operational skills — no Ollama needed

### PDF Report
- Full A4 report via ReportLab: executive summary, ATS profile, skill tables, reasoning log, learning pathway
- Download directly from results page

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, vanilla CSS (no UI library) |
| Backend | FastAPI, Python 3.11, Uvicorn |
| LLM | Ollama (local) — qwen3:4b or llama3.2 |
| Skill Extraction | Regex (200+ patterns) + SequenceMatcher fuzzy matching |
| Skill Hierarchy | Custom BFS transitive tree (15+ domains, 400+ nodes) |
| Learning Path | NetworkX DAG topological sort |
| PDF | ReportLab |
| Scraping | httpx + BeautifulSoup4 |
| File Parsing | PyMuPDF (PDF), python-docx (DOCX) |
| Containerization | Docker + docker-compose |

---

## Quick Start (Windows)

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) (optional — app works without it)

### 1. Start the backend

Double-click `start-backend.bat` or run:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

### 2. Start the frontend

Double-click `start-frontend.bat` or run:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. (Optional) Pull an Ollama model

```bash
ollama pull qwen3:4b
```

The app works without Ollama — it falls back to regex extraction and catalog-based module descriptions.

---

## Docker (Full Stack)

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Ollama | http://localhost:11434 |

---

## Project Structure

```
pathforge/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes (/api/analyze, /api/bulk-analyze, /api/ats-scan, /api/report)
│   │   ├── analyzer.py      # Skill extraction, SKILL_TREE hierarchy, compute_gap()
│   │   ├── dag.py           # Learning path DAG, module catalog, operational role templates
│   │   ├── interview.py     # Interview readiness predictor, question bank, prep strategies
│   │   ├── ats.py           # ATS scoring engine (5 dimensions)
│   │   ├── bulk.py          # Bulk resume analysis
│   │   ├── scraper.py       # Multi-site JD URL scraper
│   │   ├── extractor.py     # PDF/DOCX/TXT text extraction
│   │   └── models.py        # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx                      # Root — state machine, routing, API calls
│       └── components/
│           ├── Header.jsx               # Sticky nav, status pill
│           ├── Hero.jsx                 # Landing hero section
│           ├── UploadSection.jsx        # Resume + JD upload, role selector
│           ├── ScoreBanner.jsx          # Match %, gaps, time saved
│           ├── AtsPanel.jsx             # ATS score panel
│           ├── SkillsGrid.jsx           # Current vs required skill bars
│           ├── CompetencyRadar.jsx      # Canvas radar chart
│           ├── ReasoningTrace.jsx       # AI decision log
│           ├── PathwayTable.jsx         # Learning pathway table
│           ├── InterviewReadiness.jsx   # Interview readiness section
│           ├── BulkAnalyzer.jsx         # Bulk mode UI
│           ├── ATSScanner.jsx           # Standalone ATS scanner UI
│           ├── ReportDownload.jsx       # PDF download button
│           ├── HowItWorks.jsx           # How It Works page
│           ├── LoadingPanel.jsx         # Full-screen loading overlay
│           └── ErrorModal.jsx           # In-app error modal (no browser alerts)
├── sample_jds/                          # Sample job descriptions for testing
├── start-backend.bat
├── start-frontend.bat
├── docker-compose.yml
└── README.md
```

---

## API Reference

### `POST /api/analyze`
Full skill gap analysis for a single resume.

| Field | Type | Required |
|---|---|---|
| `resume` | file (PDF/DOCX/TXT) | yes |
| `job_description` | file (PDF/DOCX/TXT) | one of these |
| `jd_url` | string (URL) | one of these |
| `role_domain` | string | yes |

Returns `AnalysisResponse` — match score, skills, pathway, ATS result, interview readiness.

### `POST /api/bulk-analyze`
Rank multiple resumes against one JD.

| Field | Type | Required |
|---|---|---|
| `resumes` | files[] | yes |
| `job_description` | file | one of these |
| `jd_url` | string | one of these |
| `role_domain` | string | yes |

### `POST /api/ats-scan`
Standalone ATS compatibility scan.

Same fields as `/api/analyze`.

### `POST /api/report`
Generate a PDF report.

Body: JSON matching `AnalysisResponse` shape.
Returns: `{ "pdf_base64": "..." }`

### `GET /api/health`
Check backend and Ollama status.

---

## How Skill Extraction Works

1. **Section detection** — identifies dedicated Skills sections in the resume and boosts those skills +15 proficiency
2. **Regex extraction** — 200+ patterns across 14 categories (languages, frameworks, cloud, ML, DevOps, design, etc.)
3. **Fuzzy matching** — `SequenceMatcher` at 72% threshold catches typos and abbreviations
4. **Context-aware proficiency** — scans a ±100 character window around each mention for expert/mid/beginner keywords
5. **Frequency boost** — skills mentioned multiple times get up to +15 proficiency
6. **Stop word filter** — 40+ generic words (experience, knowledge, strong, etc.) are excluded

## How Gap Analysis Works

1. Resume skills and JD skills are fuzzy-matched
2. **Transitive hierarchy coverage** — if resume has "Deep Learning" at ≥70%, then TensorFlow, PyTorch, NLP, NumPy, sklearn, Statistics, Linear Algebra, etc. are all marked as covered via BFS walk of `SKILL_TREE`
3. Unmatched JD skills become gaps
4. Match % = covered JD skills / total JD skills

## How the Learning Path Works

1. Gap skills are fed into a NetworkX directed graph with prerequisite edges (e.g. Kubernetes → Docker → Linux)
2. Topological sort produces a dependency-respecting order
3. Each skill maps to a built-in module catalog (instant, no LLM) or falls back to Ollama
4. Week numbers are calculated at 5 hours/week

---

## Role Domains

**Knowledge Roles** (8): Data & Analytics, Software Engineering, Product Management, DevOps / Cloud, Sales & Marketing, Operations / Labor, Design / UX, Finance & Risk

**Operational Roles** (6): Warehouse / Logistics, Retail / Store Ops, Field Technician, Healthcare Support, Hospitality / F&B, Construction / Site

Operational roles use pre-built skill templates that supplement (not replace) JD-extracted skills, with 45+ quick training modules requiring no LLM.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend URL (frontend) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL (backend) |
| `OLLAMA_MODEL` | `llama3.2:latest` | Model to use |

Set `VITE_API_URL` in `frontend/.env`.

---

## Sample Job Descriptions

The `sample_jds/` folder contains ready-to-use JD files for testing:

- `data_analyst_jd.txt` — Data Analyst role
- `07_design_ux_jd.txt` — UX Designer role
- `sample_data_scientist_jd.txt` — Data Scientist role (root folder)

---

## Design Principles

- **No static fallback data** — every result comes from the uploaded documents
- **Offline-first** — regex extraction works without Ollama; LLM is enhancement only
- **No external APIs** — no OpenAI, no cloud services, no data leaves the machine
- **Hallucination score: 0.00** — all modules are grounded against a verified catalog before any LLM call
- **No browser alerts** — all errors shown via in-app `ErrorModal`

---

## Troubleshooting

**Backend won't start**
- Ensure Python 3.11+ is installed: `python --version`
- Activate the venv before running: `venv\Scripts\activate`

**"Analysis Failed" error**
- Backend must be running on port 8000 before clicking Forge
- Check `frontend/.env` has `VITE_API_URL=http://localhost:8000`

**No skills extracted**
- Ensure the resume is not a scanned image PDF (text must be selectable)
- Try converting to DOCX or TXT

**URL scraping fails**
- Indeed, Glassdoor, and Naukri actively block bots — use "Paste Text" mode instead
- LinkedIn works for public job postings

**Ollama not connected**
- App works fully without Ollama — only module descriptions fall back to generic text
- To enable: install Ollama, run `ollama pull qwen3:4b`, restart backend

---

## License

MIT
