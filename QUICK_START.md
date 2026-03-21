# Quick Start Guide - PathForge

## Option 1: Using Batch Files (Easiest)

1. **Double-click `start-backend.bat`** - Opens backend server
2. **Double-click `start-frontend.bat`** - Opens frontend
3. **Open browser:** http://localhost:5173

## Option 2: Manual Start

### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

## How to Use

1. **Upload Resume** - Your data scientist resume (PDF, DOCX, or TXT)
2. **Upload Job Description** - The JD you're targeting
3. **Select Role** - Choose "Data & Analytics" or relevant role
4. **Click Analyze** - Get your personalized learning path!

## What You'll See

- **Skill Match %** - How well you match the job
- **Critical Gaps** - Skills you need to learn
- **Your Profile** - Skills extracted from your resume
- **Role Requires** - Skills from the job description
- **Learning Path** - Week-by-week training plan
- **Time to Ready** - Estimated weeks to become job-ready

## Troubleshooting

### Backend won't start?
- Make sure Python 3.11+ is installed: `python --version`
- Try: `pip install --upgrade pip`

### Frontend won't start?
- Make sure Node.js is installed: `node --version`
- Try: `npm cache clean --force`

### Port already in use?
- Backend: Change port in start-backend.bat (8000 → 8001)
- Frontend: Vite will auto-assign a different port

## Note About Ollama (Optional)

The app works WITHOUT Ollama using regex-based extraction. If you want AI-powered extraction:

1. Install Ollama: https://ollama.ai
2. Run: `ollama serve`
3. Pull model: `ollama pull qwen3:4b`

But it's not required - the app will work fine without it!
