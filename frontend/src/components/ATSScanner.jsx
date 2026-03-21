import { useState, useRef, useEffect } from 'react';
import ErrorModal from './ErrorModal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ROLES = [
  'Data & Analytics', 'Software Engineering', 'Product Management',
  'DevOps / Cloud', 'Sales & Marketing', 'Operations / Labor',
  'Design / UX', 'Finance & Risk',
];

function ScoreCircle({ score, verdict }) {
  const [displayed, setDisplayed] = useState(0);
  const size = 220;
  const r = 88;
  const circ = 2 * Math.PI * r;
  const color =
    score >= 80 ? '#22c55e' :
    score >= 60 ? '#4f8ef7' :
    score >= 40 ? '#f59e0b' : '#e63329';

  useEffect(() => {
    let frame;
    let current = 0;
    const step = () => {
      current = Math.min(current + 2, score);
      setDisplayed(current);
      if (current < score) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  const dash = (displayed / 100) * circ;

  return (
    <div className="ats-score-circle-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background track — visible on dark bg */}
        <circle cx={size/2} cy={size/2} r={r} fill="none"
          stroke="rgba(255,255,255,0.12)" strokeWidth={16} />
        {/* Progress arc */}
        <circle cx={size/2} cy={size/2} r={r} fill="none"
          stroke={color} strokeWidth={16} strokeLinecap="round"
          strokeDasharray={`${dash} ${circ}`}
          strokeDashoffset={0}
          transform={`rotate(-90 ${size/2} ${size/2})`} />
        {/* Score number — white on dark bg */}
        <text x={size/2} y={size/2 - 6} textAnchor="middle"
          fontFamily="'Bebas Neue', sans-serif" fontSize={58} fill="#f0ede6">
          {displayed}
        </text>
        {/* Verdict label */}
        <text x={size/2} y={size/2 + 24} textAnchor="middle"
          fontFamily="'Courier Prime', monospace" fontSize={11} fill={color}
          letterSpacing={3}>
          {verdict.toUpperCase()}
        </text>
      </svg>
    </div>
  );
}

export default function ATSScanner() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [jdUrl, setJdUrl] = useState('');
  const [jdMode, setJdMode] = useState('file');
  const [selectedRole, setSelectedRole] = useState('Data & Analytics');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const resumeRef = useRef(null);
  const jdRef = useRef(null);

  const handleScan = async () => {
    if (!resumeFile) { setError('Please upload your resume.'); return; }
    if (jdMode === 'file' && !jdFile) { setError('Please upload a job description.'); return; }
    if (jdMode === 'text' && !jdText.trim()) { setError('Please enter a job description.'); return; }
    if (jdMode === 'url' && !jdUrl.trim()) { setError('Please enter a job URL.'); return; }

    setError('');
    setIsLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append('resume', resumeFile);

    if (jdMode === 'text') {
      const blob = new Blob([jdText], { type: 'text/plain' });
      formData.append('job_description', blob, 'job_description.txt');
    } else if (jdMode === 'url') {
      formData.append('jd_url', jdUrl.trim());
    } else {
      formData.append('job_description', jdFile);
    }
    formData.append('role_domain', selectedRole);

    try {
      const resp = await fetch(`${API_URL}/api/ats-scan`, { method: 'POST', body: formData });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${resp.status}`);
      }
      setResults(await resp.json());
    } catch (err) {
      setError(err.message || 'Scan failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="ats-scanner-wrap">
      {/* Section header */}
      <div className="section-header">
        <span className="section-num">03</span>
        <span className="section-title">ATS Resume Scanner</span>
        <div className="section-rule" />
      </div>
      <div className="section-sublabel">// Check how well your resume passes automated screening</div>

      {/* Upload zones */}
      <div className="upload-grid">
        <div className={`upload-zone ${resumeFile ? 'uploaded-resume' : ''}`}
          onClick={() => resumeRef.current?.click()}>
          <div className="upload-zone-ghost">A</div>
          <div className="upload-zone-label">Document Alpha</div>
          <div className="upload-zone-title">RESUME / CV</div>
          <div className="upload-zone-desc">PDF, DOCX, or TXT format.</div>
          {resumeFile && <div className="upload-zone-filename">{resumeFile.name}</div>}
          <div className="upload-zone-arrow">↗</div>
          <input ref={resumeRef} type="file" accept=".pdf,.doc,.docx,.txt"
            onChange={e => e.target.files?.[0] && setResumeFile(e.target.files[0])}
            style={{ display: 'none' }} />
        </div>

        <div className="bulk-jd-zone">
          <div className="jd-mode-toggle">
            <button className={`jd-mode-btn ${jdMode === 'file' ? 'active' : ''}`}
              onClick={() => setJdMode('file')}>Upload File</button>
            <button className={`jd-mode-btn ${jdMode === 'text' ? 'active' : ''}`}
              onClick={() => setJdMode('text')}>Paste Text</button>
            <button className={`jd-mode-btn ${jdMode === 'url' ? 'active' : ''}`}
              onClick={() => setJdMode('url')}>Paste Link</button>
          </div>

          {jdMode === 'file' && (
            <div className={`upload-zone ${jdFile ? 'uploaded-jd' : ''}`}
              style={{ minHeight: 180 }}
              onClick={() => jdRef.current?.click()}>
              <div className="upload-zone-ghost">B</div>
              <div className="upload-zone-label">Job Description</div>
              <div className="upload-zone-title">JOB DESCRIPTION</div>
              {jdFile
                ? <div className="upload-zone-filename">{jdFile.name}</div>
                : <div className="upload-zone-desc">PDF, DOCX, or TXT</div>}
              <div className="upload-zone-arrow">↗</div>
              <input ref={jdRef} type="file" accept=".pdf,.doc,.docx,.txt"
                onChange={e => e.target.files?.[0] && setJdFile(e.target.files[0])}
                style={{ display: 'none' }} />
            </div>
          )}
          {jdMode === 'text' && (
            <div className="jd-text-zone">
              <div className="jd-text-label">// PASTE JOB DESCRIPTION</div>
              <textarea className="jd-textarea"
                placeholder="Paste the full job description here..."
                value={jdText} onChange={e => setJdText(e.target.value)} rows={8} />
              {jdText && <div className="jd-text-count">{jdText.split(/\s+/).filter(Boolean).length} words</div>}
            </div>
          )}
          {jdMode === 'url' && (
            <div className="jd-text-zone">
              <div className="jd-text-label">// PASTE JOB LINK</div>
              <input
                type="url"
                className="jd-textarea"
                style={{ minHeight: '60px', padding: '16px', fontSize: '15px' }}
                placeholder="https://example.com/job-posting..."
                value={jdUrl}
                onChange={e => setJdUrl(e.target.value)}
              />
            </div>
          )}
        </div>
      </div>

      {/* Role chips */}
      <div className="role-label">// Select Target Role Domain</div>
      <div className="role-grid">
        {ROLES.map(r => (
          <button key={r} className={`role-chip ${selectedRole === r ? 'active' : ''}`}
            onClick={() => setSelectedRole(r)}>{r}</button>
        ))}
      </div>

      {error && <ErrorModal message={error} onClose={() => setError('')} />}

      <button className="forge-btn" onClick={handleScan} disabled={isLoading}>
        {isLoading ? 'SCANNING RESUME...' : 'SCAN RESUME'}
      </button>

      {/* Results */}
      {results && (
        <div className="ats-scan-results">
          {/* Score hero */}
          <div className="ats-scan-hero">
            <ScoreCircle score={results.ats_score} verdict={results.verdict} />
            <div className="ats-scan-hero-label">ATS COMPATIBILITY SCORE</div>
          </div>

          {/* 3 sub-scores */}
          <div className="ats-sub-scores">
            {[
              { label: 'KEYWORD MATCH', val: results.keyword_score },
              { label: 'SECTION COMPLETE', val: results.section_score },
              { label: 'FORMATTING SCORE', val: results.formatting_score },
            ].map(({ label, val }) => (
              <div key={label} className="ats-sub-score-block">
                <div className="ats-sub-score-val">{val}%</div>
                <div className="ats-sub-score-label">{label}</div>
              </div>
            ))}
          </div>

          {/* Keyword analysis */}
          <div className="ats-kw-grid">
            <div className="ats-kw-col ats-kw-col--found">
              <div className="ats-kw-col-title">KEYWORDS FOUND</div>
              <div className="ats-kw-list">
                {results.present_keywords.map(k => (
                  <span key={k} className="ats-kw-tag ats-kw-tag--hit">{k}</span>
                ))}
                {results.present_keywords.length === 0 && (
                  <span className="ats-kw-empty">None detected</span>
                )}
              </div>
            </div>
            <div className="ats-kw-col ats-kw-col--missing">
              <div className="ats-kw-col-title">KEYWORDS MISSING</div>
              <div className="ats-kw-sub">Add these to your resume</div>
              <div className="ats-kw-list">
                {results.missing_keywords.map(k => (
                  <span key={k} className="ats-kw-tag ats-kw-tag--miss">{k}</span>
                ))}
                {results.missing_keywords.length === 0 && (
                  <span className="ats-kw-empty" style={{ color: '#22c55e' }}>All keywords present</span>
                )}
              </div>
            </div>
          </div>

          {/* Formatting issues */}
          <div className="ats-issues-section">
            <div className="ats-issues-title">FORMATTING ISSUES</div>
            {results.formatting_issues.length === 0 ? (
              <div className="ats-issues-ok">No formatting issues detected</div>
            ) : (
              results.formatting_issues.map((issue, i) => (
                <div key={i} className="ats-issue-row">
                  <span className={`ats-issue-dot ats-issue-dot--${issue.severity}`} />
                  <span className="ats-issue-msg">{issue.message}</span>
                  <span className={`ats-issue-badge ats-issue-badge--${issue.severity}`}>
                    {issue.severity.toUpperCase()}
                  </span>
                </div>
              ))
            )}
          </div>

          {/* Suggestions */}
          {results.suggestions.length > 0 && (
            <div className="ats-suggestions-section">
              <div className="ats-suggestions-title">IMPROVEMENT SUGGESTIONS</div>
              {results.suggestions.map((tip, i) => (
                <div key={i} className="ats-suggestion-card">
                  <div className="ats-suggestion-num">0{i + 1}</div>
                  <div className="ats-suggestion-text">{tip}</div>
                </div>
              ))}
            </div>
          )}

          {/* Found sections strip */}
          {results.found_sections.length > 0 && (
            <div className="ats-sections-strip">
              <span className="ats-sections-strip-label">Sections detected: </span>
              {results.found_sections.map((s, i) => (
                <span key={s}>{s.charAt(0).toUpperCase() + s.slice(1)}
                  {i < results.found_sections.length - 1 ? ' · ' : ''}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
