export default function HowItWorks({ onBack }) {
  return (
    <div className="hiw-page">

      {/* ── Hero banner ── */}
      <div className="hiw-hero">
        <div className="hiw-hero-eyebrow">// DOCUMENTATION</div>
        <h1 className="hiw-hero-title">
          HOW<br />
          <span className="hiw-hero-accent">PATHFORGE</span><br />
          WORKS.
        </h1>
        <p className="hiw-hero-sub">
          A complete walkthrough of the AI pipeline — from document upload
          to personalised learning pathway. Zero cloud APIs. Zero hallucinations.
          Everything runs on your machine.
        </p>
        <button className="hiw-back-btn" onClick={onBack}>← Back to App</button>
      </div>

      {/* ── Pipeline steps ── */}
      <div className="hiw-steps-section">
        <div className="hiw-steps-label">// THE PIPELINE — 8 STAGES</div>

        {[
          {
            num: '01',
            title: 'Document Ingestion',
            tag: 'PARSE',
            color: 'var(--accent)',
            desc: 'Upload your resume and job description in PDF, DOCX, or TXT format. PathForge uses PyMuPDF for PDFs and python-docx for Word files to extract raw text with full fidelity — no OCR errors, no layout corruption.',
            details: ['Supports PDF, DOCX, DOC, TXT', 'PyMuPDF for PDF extraction', 'python-docx for Word files', 'Plain text passthrough for TXT'],
          },
          {
            num: '02',
            title: 'Skill Extraction Engine',
            tag: 'EXTRACT',
            color: 'var(--blue)',
            desc: 'A 200+ pattern regex engine scans both documents across 14 skill categories — Python ecosystem, ML/DL, Data Science, NLP, DevOps, Cloud, Frontend, Backend, and more. If Ollama is running locally, a qwen3:4b LLM pass enriches the extraction. Fuzzy matching (72% threshold via SequenceMatcher) catches abbreviations and alternate spellings.',
            details: ['200+ regex patterns across 14 categories', 'Context-aware proficiency scoring', 'Fuzzy matching via SequenceMatcher (72%)', 'Optional Ollama LLM enrichment (qwen3:4b)', 'Skill hierarchy tree — parent skills suppress child gaps'],
          },
          {
            num: '03',
            title: 'Skill Gap Matrix',
            tag: 'GAP',
            color: 'var(--red)',
            desc: 'Resume skills are matched against JD requirements using fuzzy similarity. The gap matrix identifies which required skills are missing, partially covered, or fully covered. A transitive skill tree ensures that if you know "Deep Learning" at ≥70%, child skills like TensorFlow, PyTorch, and scikit-learn are automatically marked as covered.',
            details: ['Fuzzy skill matching with similarity scoring', 'Transitive coverage via BFS skill tree walk', 'Proficiency delta calculation per skill', 'Critical gap flagging for must-have skills'],
          },
          {
            num: '04',
            title: 'ATS Compatibility Score',
            tag: 'ATS',
            color: '#f59e0b',
            desc: 'Your resume is scored across 5 weighted dimensions against the job description: Keyword Match (35%), Format & Structure (20%), Section Coverage (20%), Quantification (15%), and Action Verbs (10%). The result is a 0–100 ATS score with grade and actionable improvement tips.',
            details: ['Keyword Match — skill/keyword overlap with JD', 'Format & Structure — length, contact info, no tables', 'Section Coverage — Experience, Education, Skills, Summary', 'Quantification — numbers, metrics, impact statements', 'Action Verbs — strong opening verbs per bullet point'],
          },
          {
            num: '05',
            title: 'Prerequisite DAG',
            tag: 'DAG',
            color: 'var(--accent)',
            desc: 'Gap skills are ordered using a Directed Acyclic Graph of prerequisites. You never learn Kubernetes before Docker, or PyTorch before Python. The DAG covers 50+ prerequisite chains across all major tech domains, ensuring your learning path is always logically sequenced.',
            details: ['50+ prerequisite chains', 'Topological sort via NetworkX', 'Existing skills used to skip covered prerequisites', 'Handles circular dependency detection'],
          },
          {
            num: '06',
            title: 'Module Generation',
            tag: 'GENERATE',
            color: 'var(--blue)',
            desc: 'For each gap skill in the ordered path, a training module is generated with a title, description, estimated hours, and module count. If Ollama is available, qwen3:4b generates contextual module descriptions. Otherwise, a deterministic template engine produces grounded output from the built-in course catalog.',
            details: ['Up to 6 modules generated in parallel', 'Ollama qwen3:4b for contextual descriptions', 'Deterministic fallback — zero hallucinations', 'Hour estimates based on skill complexity', 'All /no_think prefixed prompts for speed'],
          },
          {
            num: '07',
            title: 'Competency Radar',
            tag: 'VISUALISE',
            color: '#22c55e',
            desc: 'A canvas-based radar chart plots your current skill profile (blue polygon) against the role requirements (pink/red polygon) across up to 10 axes. The visual gap between the two polygons shows exactly where you need to grow.',
            details: ['Canvas-rendered, no external chart library', 'Blue polygon = your current profile', 'Pink/red polygon = role requirements', 'Up to 10 skill axes', 'Responsive and high-DPI aware'],
          },
          {
            num: '08',
            title: 'Learning Pathway & Report',
            tag: 'OUTPUT',
            color: 'var(--accent)',
            desc: 'The final output is a week-by-week learning pathway showing which modules to complete, in what order, with estimated hours per week. A full PDF report can be downloaded containing your ATS score, skill gaps, and complete pathway — generated server-side via ReportLab.',
            details: ['Week-by-week timeline at 5 hrs/week', 'Gap / Bridge / Enhance tags per module', 'PDF report via ReportLab (server-side)', 'Reasoning trace showing every AI decision', 'Grounded against course catalog — hallucination score: 0.00'],
          },
        ].map((step, i) => (
          <div key={step.num} className="hiw-step" style={{ '--step-color': step.color }}>
            <div className="hiw-step-left">
              <div className="hiw-step-num">{step.num}</div>
              <div className="hiw-step-connector" />
            </div>
            <div className="hiw-step-body">
              <div className="hiw-step-tag" style={{ color: step.color, borderColor: step.color }}>
                {step.tag}
              </div>
              <div className="hiw-step-title">{step.title}</div>
              <p className="hiw-step-desc">{step.desc}</p>
              <div className="hiw-step-details">
                {step.details.map(d => (
                  <div key={d} className="hiw-step-detail">
                    <span className="hiw-detail-dot" style={{ background: step.color }} />
                    {d}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Architecture diagram ── */}
      <div className="hiw-arch-section">
        <div className="hiw-arch-label">// SYSTEM ARCHITECTURE</div>
        <div className="hiw-arch-title">TECH STACK</div>
        <div className="hiw-arch-grid">
          {[
            {
              layer: 'FRONTEND',
              color: 'var(--accent)',
              items: ['React 18 + Vite', 'Canvas API (Radar, ATS Ring)', 'CSS Variables Design System', 'Bebas Neue + Barlow Condensed'],
            },
            {
              layer: 'BACKEND',
              color: 'var(--blue)',
              items: ['FastAPI + Uvicorn', 'Python 3.11', 'Async/await throughout', 'Pydantic v2 schemas'],
            },
            {
              layer: 'AI / NLP',
              color: '#f59e0b',
              items: ['Ollama (local LLM host)', 'qwen3:4b model', '200+ regex skill patterns', 'SequenceMatcher fuzzy match'],
            },
            {
              layer: 'DATA',
              color: '#22c55e',
              items: ['PyMuPDF (PDF parsing)', 'python-docx (Word parsing)', 'NetworkX (DAG / topo sort)', 'ReportLab (PDF generation)'],
            },
          ].map(({ layer, color, items }) => (
            <div key={layer} className="hiw-arch-card" style={{ borderTop: `3px solid ${color}` }}>
              <div className="hiw-arch-card-layer" style={{ color }}>{layer}</div>
              {items.map(item => (
                <div key={item} className="hiw-arch-card-item">
                  <span className="hiw-arch-dot" style={{ background: color }} />
                  {item}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* ── Privacy note ── */}
      <div className="hiw-privacy">
        <div className="hiw-privacy-icon">🔒</div>
        <div>
          <div className="hiw-privacy-title">100% LOCAL — YOUR DATA NEVER LEAVES YOUR MACHINE</div>
          <div className="hiw-privacy-body">
            PathForge runs entirely on localhost. No resume data is sent to any cloud API.
            No analytics. No tracking. The Ollama LLM runs locally on your GPU/CPU.
            If Ollama is offline, the regex engine handles everything — still zero external calls.
          </div>
        </div>
      </div>

      {/* ── CTA ── */}
      <div className="hiw-cta-section">
        <div className="hiw-cta-title">READY TO FORGE YOUR PATH?</div>
        <button className="forge-btn hiw-cta-btn" onClick={onBack}>
          START ANALYSIS ↗
        </button>
      </div>

    </div>
  );
}
