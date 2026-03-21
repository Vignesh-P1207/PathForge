import { useState, useRef } from 'react';
import ErrorModal from './ErrorModal';

const ROLES = [
  'Data & Analytics',
  'Software Engineering',
  'Product Management',
  'DevOps / Cloud',
  'Sales & Marketing',
  'Operations / Labor',
  'Design / UX',
  'Finance & Risk',
];

const OPERATIONAL_ROLES = [
  'Warehouse / Logistics',
  'Retail / Store Ops',
  'Field Technician',
  'Healthcare Support',
  'Hospitality / F&B',
  'Construction / Site',
];

// Extract a readable company/portal name from a URL
function companyFromUrl(url) {
  if (!url) return '';
  try {
    const u = new URL(url.startsWith('http') ? url : 'https://' + url);
    const host = u.hostname.replace(/^www\./, '');
    const known = {
      'linkedin.com': 'LinkedIn', 'indeed.com': 'Indeed', 'naukri.com': 'Naukri',
      'glassdoor.com': 'Glassdoor', 'internshala.com': 'Internshala',
      'wellfound.com': 'Wellfound', 'angel.co': 'AngelList',
      'monster.com': 'Monster', 'simplyhired.com': 'SimplyHired',
      'ziprecruiter.com': 'ZipRecruiter', 'greenhouse.io': 'Greenhouse',
      'lever.co': 'Lever', 'myworkdayjobs.com': 'Workday',
      'careers.google.com': 'Google', 'amazon.jobs': 'Amazon',
      'microsoft.com': 'Microsoft', 'apple.com': 'Apple',
      'meta.com': 'Meta', 'infosys.com': 'Infosys',
      'wipro.com': 'Wipro', 'tcs.com': 'TCS',
      'hcltech.com': 'HCL Technologies', 'accenture.com': 'Accenture',
      'ibm.com': 'IBM', 'oracle.com': 'Oracle',
    };
    for (const [key, name] of Object.entries(known)) {
      if (host.includes(key)) return name;
    }
    // Fallback: capitalize root domain
    return host.split('.')[0].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  } catch {
    return '';
  }
}

export default function UploadSection({ onAnalyze, isLoading }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [jdUrl, setJdUrl] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [jdMode, setJdMode] = useState('file');
  const [selectedRole, setSelectedRole] = useState('Data & Analytics');
  const [errorMsg, setErrorMsg] = useState('');
  const resumeInputRef = useRef(null);
  const jdInputRef = useRef(null);

  const handleResumeChange = (e) => {
    if (e.target.files[0]) setResumeFile(e.target.files[0]);
  };

  const handleJdChange = (e) => {
    if (e.target.files[0]) setJdFile(e.target.files[0]);
  };

  const handleForge = () => {
    if (!resumeFile) { setErrorMsg('Please upload your resume first.'); return; }
    if (jdMode === 'text') {
      if (!jdText.trim()) { setErrorMsg('Please enter a job description.'); return; }
      const prefix = sourceUrl.trim() ? `Source: ${sourceUrl.trim()}\n\n` : '';
      const blob = new Blob([prefix + jdText], { type: 'text/plain' });
      const file = new File([blob], 'job_description.txt', { type: 'text/plain' });
      onAnalyze(resumeFile, file, sourceUrl.trim() || null, selectedRole);
    } else if (jdMode === 'url') {
      if (!jdUrl.trim()) { setErrorMsg('Please enter a job URL.'); return; }
      onAnalyze(resumeFile, null, jdUrl.trim(), selectedRole);
    } else {
      if (!jdFile) { setErrorMsg('Please upload a job description file.'); return; }
      onAnalyze(resumeFile, jdFile, null, selectedRole);
    }
  };

  return (
    <div>
      <ErrorModal message={errorMsg} onClose={() => setErrorMsg('')} />
      <div className="section-header">
        <span className="section-num">01</span>
        <span className="section-title">Upload Documents</span>
        <div className="section-rule" />
      </div>

      <div className="upload-grid">
        {/* Resume zone */}
        <div
          className={`upload-zone ${resumeFile ? 'uploaded-resume' : ''}`}
          onClick={() => resumeInputRef.current?.click()}
        >
          <div className="upload-zone-ghost">A</div>
          <div className="upload-zone-label">Document Alpha</div>
          <div className="upload-zone-title">RESUME / CV</div>
          <div className="upload-zone-desc">
            Upload your resume in PDF, DOCX, or TXT format.
            Our AI will extract skills and proficiency levels.
          </div>
          {resumeFile && (
            <div className="upload-zone-filename">{resumeFile.name}</div>
          )}
          <div className="upload-zone-arrow">↗</div>
          <input
            ref={resumeInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleResumeChange}
            style={{ display: 'none' }}
          />
        </div>

        {/* JD zone — file, text, or url */}
        <div className="bulk-jd-zone">
          <div className="jd-mode-toggle">
            <button
              className={`jd-mode-btn ${jdMode === 'file' ? 'active' : ''}`}
              onClick={() => setJdMode('file')}
            >Upload File</button>
            <button
              className={`jd-mode-btn ${jdMode === 'text' ? 'active' : ''}`}
              onClick={() => setJdMode('text')}
            >Paste Text</button>
            <button
              className={`jd-mode-btn ${jdMode === 'url' ? 'active' : ''}`}
              onClick={() => setJdMode('url')}
            >Paste Link</button>
          </div>

          {jdMode === 'file' && (
            <div
              className={`upload-zone ${jdFile ? 'uploaded-jd' : ''}`}
              style={{ minHeight: 200 }}
              onClick={() => jdInputRef.current?.click()}
            >
              <div className="upload-zone-ghost">B</div>
              <div className="upload-zone-label">Document Beta</div>
              <div className="upload-zone-title">JOB DESCRIPTION</div>
              <div className="upload-zone-desc">
                Paste or upload the target job description.
                Supports PDF, DOCX, and TXT formats.
              </div>
              {jdFile && (
                <div className="upload-zone-filename">{jdFile.name}</div>
              )}
              <div className="upload-zone-arrow">↗</div>
              <input
                ref={jdInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleJdChange}
                style={{ display: 'none' }}
              />
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
              <input
                type="url"
                className="jd-source-url"
                placeholder="Optional: paste the job URL (to show company name in results)"
                value={sourceUrl}
                onChange={e => setSourceUrl(e.target.value)}
              />
              {jdText && (
                <div className="jd-text-count">
                  {jdText.split(/\s+/).filter(Boolean).length} words
                </div>
              )}
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

      <div className="role-label">// Select Target Role Domain</div>

      <div className="role-grid">
        {ROLES.map((role) => (
          <button
            key={role}
            className={`role-chip ${selectedRole === role ? 'active' : ''}`}
            onClick={() => setSelectedRole(role)}
          >
            {role}
          </button>
        ))}
      </div>

      <div className="role-label" style={{ marginTop: 16 }}>// Operational &amp; Labor Roles</div>
      <div className="role-grid role-grid--ops">
        {OPERATIONAL_ROLES.map((role) => (
          <button
            key={role}
            className={`role-chip role-chip--ops ${selectedRole === role ? 'active' : ''}`}
            onClick={() => setSelectedRole(role)}
          >
            {role}
          </button>
        ))}
      </div>

      <button
        className="forge-btn"
        onClick={handleForge}
        disabled={isLoading}
      >
        FORGE MY PATHWAY
      </button>
    </div>
  );
}
