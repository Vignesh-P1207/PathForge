import { useState, useRef } from 'react';
import ErrorModal from './ErrorModal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ROLES = [
  'Data & Analytics', 'Software Engineering', 'Product Management',
  'DevOps / Cloud', 'Sales & Marketing', 'Operations / Labor',
  'Design / UX', 'Finance & Risk',
];

const RANK_COLORS = { 1: '#f59e0b', 2: '#8a8880', 3: '#cd7c3a' };

function MatchBadge({ pct }) {
  const color = pct >= 70 ? '#22c55e' : pct >= 40 ? '#f59e0b' : 'var(--red)';
  return <span style={{ color, fontFamily: 'var(--display)', fontSize: 22 }}>{pct}%</span>;
}

export default function BulkAnalyzer() {
  const [resumeFiles, setResumeFiles] = useState([]);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [jdUrl, setJdUrl] = useState('');
  const [jdMode, setJdMode] = useState('file'); // 'file' | 'text' | 'url'
  const [selectedRole, setSelectedRole] = useState('Data & Analytics');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const resumeInputRef = useRef(null);
  const jdInputRef = useRef(null);

  const handleResumeChange = (e) => {
    if (e.target.files?.length) setResumeFiles(Array.from(e.target.files));
  };

  const handleJdChange = (e) => {
    if (e.target.files?.[0]) setJdFile(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!resumeFiles.length) { setError('Please upload at least one resume.'); return; }
    if (jdMode === 'file' && !jdFile) { setError('Please upload a job description.'); return; }
    if (jdMode === 'text' && !jdText.trim()) { setError('Please enter a job description.'); return; }
    if (jdMode === 'url' && !jdUrl.trim()) { setError('Please enter a job URL.'); return; }

    setError('');
    setIsLoading(true);
    setResults(null);

    const formData = new FormData();
    resumeFiles.forEach(f => formData.append('resumes', f));

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
      const resp = await fetch(`${API_URL}/api/bulk-analyze`, { method: 'POST', body: formData });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${resp.status}`);
      }
      setResults(await resp.json());
    } catch (err) {
      setError(err.message || 'Analysis failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bulk-wrap">
      {/* Section header */}
      <div className="section-header">
        <span className="section-num">02</span>
        <span className="section-title">Bulk Resume Analyzer</span>
        <div className="section-rule" />
      </div>
      <div className="section-sublabel">// Upload multiple resumes against one job description</div>

      {/* Upload grid */}
      <div className="bulk-upload-grid">
        {/* Resumes zone */}
        <div
          className={`upload-zone bulk-resume-zone ${resumeFiles.length ? 'uploaded-resume' : ''}`}
          onClick={() => resumeInputRef.current?.click()}
        >
          <div className="upload-zone-ghost">A</div>
          <div className="upload-zone-label">Resumes (Multiple)</div>
          <div className="upload-zone-title">UPLOAD RESUMES</div>
          <div className="upload-zone-desc">Drag multiple PDF / DOCX files. Up to 50 candidates.</div>
          {resumeFiles.length > 0 && (
            <div className="bulk-file-badge">{resumeFiles.length} FILES SELECTED</div>
          )}
          <div className="upload-zone-arrow">↗</div>
          <input ref={resumeInputRef} type="file" multiple accept=".pdf,.doc,.docx,.txt"
            onChange={handleResumeChange} style={{ display: 'none' }} />
        </div>

        {/* JD zone */}
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
            <div
              className={`upload-zone ${jdFile ? 'uploaded-jd' : ''}`}
              style={{ minHeight: 180 }}
              onClick={() => jdInputRef.current?.click()}
            >
              <div className="upload-zone-ghost">B</div>
              <div className="upload-zone-label">Job Description</div>
              <div className="upload-zone-title">JOB DESCRIPTION</div>
              {jdFile
                ? <div className="upload-zone-filename">{jdFile.name}</div>
                : <div className="upload-zone-desc">PDF, DOCX, or TXT</div>}
              <div className="upload-zone-arrow">↗</div>
              <input ref={jdInputRef} type="file" accept=".pdf,.doc,.docx,.txt"
                onChange={handleJdChange} style={{ display: 'none' }} />
            </div>
          )}
          {jdMode === 'text' && (
            <div className="jd-text-zone">
              <div className="jd-text-label">// PASTE JOB DESCRIPTION</div>
              <textarea
                className="jd-textarea"
                placeholder="Paste the full job description here..."
                value={jdText}
                onChange={e => setJdText(e.target.value)}
                rows={8}
              />
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

      <button className="forge-btn" onClick={handleAnalyze} disabled={isLoading}>
        {isLoading
          ? `ANALYZING ${resumeFiles.length} RESUME${resumeFiles.length !== 1 ? 'S' : ''}...`
          : 'ANALYZE ALL CANDIDATES'}
      </button>

      {/* Results */}
      {results && (
        <div className="bulk-results">
          {/* Summary banner */}
          <div className="bulk-summary">
            <div className="bulk-stat">
              <div className="bulk-stat-val">{results.total_candidates}</div>
              <div className="bulk-stat-label">CANDIDATES</div>
            </div>
            <div className="bulk-stat bulk-stat--accent">
              <div className="bulk-stat-val">{results.avg_match_pct}%</div>
              <div className="bulk-stat-label">AVG MATCH</div>
            </div>
            <div className="bulk-stat bulk-stat--blue">
              <div className="bulk-stat-val">{results.best_match_pct}%</div>
              <div className="bulk-stat-label">BEST MATCH</div>
            </div>
            <div className="bulk-stat">
              <div className="bulk-stat-val">{results.job_description_skills}</div>
              <div className="bulk-stat-label">JD SKILLS</div>
            </div>
          </div>

          {/* Top 3 */}
          {results.top_candidates.length > 0 && (
            <div className="bulk-top-section">
              <div className="bulk-top-title">TOP CANDIDATES</div>
              <div className="bulk-top-grid">
                {results.top_candidates.map(c => (
                  <div key={c.rank} className="bulk-top-card"
                    style={{ borderTop: `3px solid ${RANK_COLORS[c.rank] || 'var(--muted)'}` }}>
                    <div className="bulk-rank-badge" style={{ color: RANK_COLORS[c.rank] || 'var(--muted)' }}>
                      #{c.rank}
                    </div>
                    <div className="bulk-card-name">{c.candidate}</div>
                    <div className="bulk-card-score">{c.match_pct}%</div>
                    <div className="bulk-card-chips">
                      {c.top_skills.slice(0, 3).map(s => (
                        <span key={s} className="bulk-skill-chip">{s}</span>
                      ))}
                    </div>
                    {c.critical_gaps.length > 0 && (
                      <div className="bulk-card-chips">
                        {c.critical_gaps.map(g => (
                          <span key={g} className="bulk-gap-chip">{g}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Full leaderboard */}
          <div className="bulk-table-wrap">
            <div className="bulk-table-title">FULL LEADERBOARD</div>
            <table className="bulk-table">
              <thead>
                <tr>
                  <th>RANK</th>
                  <th>CANDIDATE</th>
                  <th>MATCH %</th>
                  <th>SKILLS MATCHED</th>
                  <th>GAPS</th>
                  <th>TOP SKILLS</th>
                </tr>
              </thead>
              <tbody>
                {results.all_candidates.map((c, i) => (
                  <tr key={c.rank} className={`bulk-row ${c.is_top ? 'bulk-row--top' : ''}`}
                    style={{ animationDelay: `${i * 40}ms` }}>
                    <td className="bulk-td-rank">
                      <span style={{ color: RANK_COLORS[c.rank] || 'var(--ink)', fontFamily: 'var(--display)', fontSize: 18 }}>
                        {c.rank}
                      </span>
                    </td>
                    <td className="bulk-td-name">{c.candidate}</td>
                    <td><MatchBadge pct={c.match_pct} /></td>
                    <td style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>{c.matched_count}</td>
                    <td style={{ fontFamily: 'var(--mono)', fontSize: 13, color: c.gap_count > 3 ? 'var(--red)' : 'var(--ink)' }}>
                      {c.gap_count}
                    </td>
                    <td>
                      <div className="bulk-skills-inline">
                        {c.top_skills.slice(0, 3).map(s => (
                          <span key={s} className="bulk-skill-chip bulk-skill-chip--sm">{s}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Common gaps strip */}
          {results.common_gaps.length > 0 && (
            <div className="bulk-gaps-strip">
              <span className="bulk-gaps-label">Common skill gaps across all candidates: </span>
              {results.common_gaps.map((g, i) => (
                <span key={g}>{g}{i < results.common_gaps.length - 1 ? ' · ' : ''}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
