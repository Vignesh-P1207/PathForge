<div align="center">

<img src="https://img.shields.io/badge/PATHFORGE-AI%20Career%20Intelligence-7c5cfc?style=for-the-badge&labelColor=08080d&color=7c5cfc" height="40"/>

<br/>
<br/>

**AI-powered skill gap analyzer · Learning path generator · Interview readiness predictor**

*Built for Rockverse Hackathon submission — runs 100% locally, zero cloud APIs*

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com)

</div>

---

## What It Does

Upload a resume + job description (file, pasted text, or URL). PathForge runs a full pipeline:

```
Resume + JD  →  Skill Extraction  →  Gap Analysis  →  DAG Learning Path
                                  ↓
                         ATS Score  +  Interview Readiness  +  PDF Report
```

Everything works offline via regex. Ollama (local LLM) enhances module descriptions — the app is fully functional without it.

---

## Tech Stack

<table>
<tr>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="40"/><br/>
<sub><b>React 18</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vitejs/vitejs-original.svg" width="40"/><br/>
<sub><b>Vite</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"/><br/>
<sub><b>Python 3.11</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40"/><br/>
<sub><b>FastAPI</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="40"/><br/>
<sub><b>Docker</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/networkx/networkx-original.svg" width="40" onerror="this.style.display='none'"/><br/>
<sub><b>NetworkX</b></sub>
</td>
</tr>
<tr>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" width="40"/><br/>
<sub><b>NumPy</b></sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" width="40"/><br/>
<sub><b>Pandas</b></sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/-Ollama-000?style=flat-square&logo=ollama" height="28"/><br/>
<sub><b>Ollama LLM</b></sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/-ReportLab-e63329?style=flat-square" height="28"/><br/>
<sub><b>ReportLab</b></sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/-BeautifulSoup4-4B8BBE?style=flat-square" height="28"/><br/>
<sub><b>BS4 Scraper</b></sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/-PyMuPDF-333?style=flat-square" height="28"/><br/>
<sub><b>PyMuPDF</b></sub>
</td>
</tr>
</table>

| Layer | Details |
|---|---|
| **Frontend** | React 18, Vite, vanilla CSS — no UI library, custom design system |
| **Backend** | FastAPI + Uvicorn, async throughout, Pydantic v2 validation |
| **LLM** | Ollama local inference — `qwen3:4b` or `llama3.2` |
| **Skill Extraction** | 200+ regex patterns + `SequenceMatcher` fuzzy matching (72% threshold) |
| **Skill Hierarchy** | Custom BFS transitive tree — 15+ domains, 400+ nodes |
| **Learning Path** | NetworkX DAG topological sort with prerequisite chains |
| **PDF** | ReportLab A4 — tables, styles, executive summary |
| **Scraping** | httpx + BeautifulSoup4 — 11 job sites + JSON-LD fallback |
| **File Parsing** | PyMuPDF (PDF), python-docx (DOCX), plain text |

---

## Features

<details>
<summary><b>Single Resume Analyzer</b></summary>

- Upload resume (PDF / DOCX / TXT) + job description
- Match score, critical gap count, time-saved percentage
- Skill proficiency bars — current vs. required
- Competency radar chart (canvas-based, zero chart library)
- AI reasoning trace showing every decision step
- DAG-ordered learning pathway with week-by-week estimates

</details>

<details>
<summary><b>ATS Compatibility Panel</b></summary>

- 5-dimension scoring:
  - Keyword Match — 35%
  - Format & Structure — 20%
  - Section Coverage — 20%
  - Achievement Quantification — 15%
  - Action Verb Usage — 10%
- Keyword hit/miss lists, section presence check, improvement tips
- Animated ring gauge

</details>

<details>
<summary><b>Interview Readiness Predictor</b></summary>

- Confidence arc gauge (0–100%)
- Readiness level: `Not Ready` / `Partially Ready` / `Interview Ready`
- **Danger zones** — top gap skills with 2 likely interview questions + prep strategy each
- **Strong zones** — top matched skills with showcase questions
- 30+ pre-built question banks; Ollama fallback for unknown skills

</details>

<details>
<summary><b>Bulk Resume Analyzer</b></summary>

- Upload multiple resumes against one JD
- Ranked leaderboard with match scores, top skills, critical gaps
- Common gaps across all candidates

</details>

<details>
<summary><b>Standalone ATS Scanner</b></summary>

- Resume-only or resume + JD scan
- Formatting issue detection (word count, email, phone presence)
- Keyword and section analysis

</details>

<details>
<summary><b>Multi-Site JD Scraper</b></summary>

Paste a job URL — scraper handles:

`LinkedIn` · `Indeed` · `Naukri` · `Glassdoor` · `Internshala` · `Wellfound` · `Greenhouse` · `Lever` · `Workday` · `Monster` · `ZipRecruiter`

- JSON-LD `schema.org/JobPosting` as primary extraction strategy
- Company name auto-detected from URL domain
- Graceful fallback with user-friendly error messages when sites block bots

</details>

<details>
<summary><b>Operational Role Support</b></summary>

6 operational/labor role templates with pre-built skill sets:

| Role | Sample Skills |
|---|---|
| Warehouse / Logistics | Inventory Management, WMS Software, Forklift Operation |
| Retail / Store Ops | POS Systems, Visual Merchandising, Loss Prevention |
| Field Technician | Electrical Systems, Equipment Maintenance, Mobile Reporting |
| Healthcare Support | HIPAA Compliance, EHR, Vital Signs Monitoring |
| Hospitality / F&B | Food Safety & Hygiene, Upselling Techniques, POS Systems |
| Construction / Site | Blueprint Reading, OSHA Regulations, Material Estimation |

Template skills supplement (not replace) JD-extracted skills. 45+ quick modules — no LLM needed.

</details>

<details>
<summary><b>PDF Report</b></summary>

Full A4 report via ReportLab:
- Executive summary table (match score, gaps, time saved, weeks to ready)
- ATS compatibility profile with dimension breakdown
- Validated competencies + critical gaps tables
- AI reasoning log
- Prescribed upskilling pathway

</details>

---

## Quick Start

Choose your method — Docker (recommended) or Manual.

---

### Method 1 — Docker (Recommended)

> Requires: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

#### First-time setup

```powershell
# Step 1 — Clone the repo
git clone https://github.com/YOUR_USERNAME/pathforge.git
cd pathforge

# Step 2 — Build and start all containers
docker compose up --build

# Step 3 — Pull models (new terminal, first time only)
docker exec -it pathforge-ollama-1 ollama pull qwen3:4b
docker exec -it pathforge-ollama-1 ollama pull nomic-embed-text

# Step 4 — Open the app
start http://localhost:3000
```

#### Every run after that

```powershell
# Models are cached in the Docker volume — no re-pulling needed
docker compose up

# Open the app
start http://localhost:3000
```

#### What you should see when ready

```
pathforge-backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8000
pathforge-frontend-1  | ➜  Local: http://localhost:3000/
pathforge-ollama-1    | Ollama is running
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Ollama | http://localhost:11434 |

---

### Method 2 — Manual (PowerShell)

> Requires: Python 3.11+, Node.js 18+, two terminal windows

#### Terminal 1 — Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Wait for: `INFO: Uvicorn running on http://127.0.0.1:8000`

#### Terminal 2 — Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

#### Ollama (optional — enhances module descriptions)

```powershell
# Install from https://ollama.com, then:
ollama pull qwen3:4b
```

The app works fully without Ollama. Regex extraction covers all skill detection — Ollama only enriches module descriptions for skills outside the built-in catalog.

#### One-click start (Windows)

Double-click `start-backend.bat` and `start-frontend.bat` in the project root.

---

## Project Structure

```
pathforge/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes — /api/analyze, /api/bulk-analyze, /api/ats-scan, /api/report
│   │   ├── analyzer.py      # Skill extraction, SKILL_TREE hierarchy (400+ nodes), compute_gap()
│   │   ├── dag.py           # Learning path DAG, module catalog, operational role templates
│   │   ├── interview.py     # Interview readiness predictor, 30+ question banks, prep strategies
│   │   ├── ats.py           # ATS scoring engine — 5 weighted dimensions
│   │   ├── bulk.py          # Bulk resume analysis
│   │   ├── scraper.py       # Multi-site JD URL scraper — 11 sites + JSON-LD
│   │   ├── extractor.py     # PDF / DOCX / TXT text extraction
│   │   └── models.py        # Pydantic schemas
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── App.jsx                      # Root — state machine, routing, API calls
│       └── components/
│           ├── Header.jsx               # Sticky nav, status pill
│           ├── Hero.jsx                 # Landing hero
│           ├── UploadSection.jsx        # Resume + JD upload, role selector (14 roles)
│           ├── ScoreBanner.jsx          # Match %, gaps, time saved
│           ├── AtsPanel.jsx             # ATS score panel with ring gauge
│           ├── SkillsGrid.jsx           # Current vs required skill bars
│           ├── CompetencyRadar.jsx      # Canvas radar chart
│           ├── ReasoningTrace.jsx       # AI decision log
│           ├── PathwayTable.jsx         # Learning pathway table
│           ├── InterviewReadiness.jsx   # Interview readiness section
│           ├── BulkAnalyzer.jsx         # Bulk mode UI
│           ├── ATSScanner.jsx           # Standalone ATS scanner
│           ├── ReportDownload.jsx       # PDF download
│           ├── HowItWorks.jsx           # How It Works page
│           ├── LoadingPanel.jsx         # Full-screen loading overlay
│           └── ErrorModal.jsx           # In-app error modal
│
├── sample_jds/                          # 9 sample JDs for testing
├── start-backend.bat
├── start-frontend.bat
├── docker-compose.yml
└── README.md
```

---

## API Reference

### `POST /api/analyze`

Full skill gap analysis for a single resume.

```
resume          file (PDF/DOCX/TXT)   required
job_description file (PDF/DOCX/TXT)   one of these two
jd_url          string (URL)           one of these two
role_domain     string                 required
```

Returns `AnalysisResponse` — match score, skills, pathway, ATS result, interview readiness.

### `POST /api/bulk-analyze`

Rank multiple resumes against one JD. Same fields as above but `resumes` is a file array.

### `POST /api/ats-scan`

Standalone ATS compatibility scan. Same fields as `/api/analyze`.

### `POST /api/report`

Generate PDF. Body: `AnalysisResponse` JSON. Returns `{ "pdf_base64": "..." }`.

### `GET /api/health`

Check backend + Ollama status.

---

## How It Works

### Skill Extraction Pipeline

```
Document text
    │
    ├─ 1. Section detection  →  Skills section gets +15 proficiency boost
    ├─ 2. Regex extraction   →  200+ patterns, 14 categories
    ├─ 3. Fuzzy matching     →  SequenceMatcher @ 72% threshold
    ├─ 4. Context proficiency →  ±100 char window for expert/mid/beginner keywords
    ├─ 5. Frequency boost    →  multi-mention skills get up to +15
    └─ 6. Stop word filter   →  40+ generic words excluded
```

### Gap Analysis — Transitive Hierarchy

```
Resume has: "Deep Learning" @ 85%
                │
                └─ BFS walk of SKILL_TREE
                        ├─ TensorFlow ✓ covered
                        ├─ PyTorch    ✓ covered
                        ├─ NLP        ✓ covered
                        ├─ NumPy      ✓ covered
                        ├─ sklearn    ✓ covered
                        ├─ Statistics ✓ covered
                        └─ Linear Algebra ✓ covered

Match % = covered JD skills / total JD skills
```

### Learning Path — DAG Sort

```
Gap skills → NetworkX DiGraph with prerequisite edges
                │
                └─ Topological sort → dependency-respecting order
                        e.g. Linux → Docker → Kubernetes → Helm
                                │
                                └─ Module catalog lookup (instant)
                                        or Ollama fallback
                                                │
                                                └─ Week numbers @ 5 hrs/week
```

---

## Environment Variables

| Variable | Default | Where |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | `frontend/.env` |
| `OLLAMA_URL` | `http://localhost:11434` | backend env |
| `OLLAMA_MODEL` | `llama3.2:latest` | backend env |

---

## Design Principles

| Principle | Implementation |
|---|---|
| No static fallback data | Every result comes from uploaded documents |
| Offline-first | Regex extraction works without any LLM |
| No external APIs | No OpenAI, no cloud services, no data leaves the machine |
| Hallucination score: 0.00 | All modules grounded against verified catalog before any LLM call |
| No browser alerts | All errors via in-app `ErrorModal` component |
| Transitive skill coverage | BFS walk prevents false gaps (Deep Learning covers 20+ sub-skills) |

---

## Troubleshooting

**Backend won't start** — ensure Python 3.11+ and activate venv: `venv\Scripts\activate`

**"Analysis Failed"** — backend must be running on port 8000 before clicking Forge. Check `frontend/.env` has `VITE_API_URL=http://localhost:8000`

**No skills extracted** — resume must have selectable text (not a scanned image PDF). Try converting to DOCX or TXT.

**URL scraping fails** — Indeed, Glassdoor, Naukri actively block bots. Use "Paste Text" mode instead.

**Ollama not connected** — app works fully without it. To enable: `ollama pull qwen3:4b` then restart backend.

---

<div align="center">

Built with ♦ for Rockverse  Hackathon · MIT License

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Made with React](https://img.shields.io/badge/Made%20with-React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Runs Locally](https://img.shields.io/badge/Runs-100%25%20Locally-7c5cfc?style=flat-square)
![No Cloud APIs](https://img.shields.io/badge/Zero-Cloud%20APIs-e63329?style=flat-square)

</div>
