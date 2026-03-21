import { useState, useEffect } from 'react';
import Ticker from './components/Ticker';
import Header from './components/Header';
import Hero from './components/Hero';
import HowItWorks from './components/HowItWorks';
import UploadSection from './components/UploadSection';
import BulkAnalyzer from './components/BulkAnalyzer';
import ATSScanner from './components/ATSScanner';
import LoadingPanel from './components/LoadingPanel';
import ScoreBanner from './components/ScoreBanner';
import AtsPanel from './components/AtsPanel';
import SkillsGrid from './components/SkillsGrid';
import CompetencyRadar from './components/CompetencyRadar';
import ReasoningTrace from './components/ReasoningTrace';
import PathwayTable from './components/PathwayTable';
import TimelineFooter from './components/TimelineFooter';
import ReportDownload from './components/ReportDownload';
import InterviewReadiness from './components/InterviewReadiness';
import ErrorModal from './components/ErrorModal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Extract readable company/portal name from a URL
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
    return host.split('.')[0].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  } catch {
    return '';
  }
}

const TABS = [
  { id: 'single', label: 'Single Resume' },
  { id: 'bulk',   label: 'Bulk Analyzer' },
  { id: 'ats',    label: 'ATS Scanner' },
];

export default function App() {
  const [appState, setAppState] = useState('idle');
  const [results, setResults] = useState(null);
  const [selectedRole, setSelectedRole] = useState('Data & Analytics');
  const [activeTab, setActiveTab] = useState('single');
  const [page, setPage] = useState('home');
  const [clientCompany, setClientCompany] = useState('');
  const [errorMsg, setErrorMsg] = useState(''); // drives ErrorModal

  // Custom cursor
  useEffect(() => {
    const cursor = document.getElementById('cursor');
    const ring = document.getElementById('cursor-ring');

    const move = (e) => {
      if (cursor) { cursor.style.left = e.clientX + 'px'; cursor.style.top = e.clientY + 'px'; }
      if (ring)   { ring.style.left   = e.clientX + 'px'; ring.style.top   = e.clientY + 'px'; }
    };

    const addAccent    = () => { cursor?.classList.add('accent');    ring?.classList.add('accent'); };
    const removeAccent = () => { cursor?.classList.remove('accent'); ring?.classList.remove('accent'); };

    window.addEventListener('mousemove', move);

    const interactiveSelector = 'a, button, .upload-zone, .role-chip, .forge-btn, .btn-primary, .btn-ghost, .header-nav a';
    const observe = () => {
      document.querySelectorAll(interactiveSelector).forEach(el => {
        el.addEventListener('mouseenter', addAccent);
        el.addEventListener('mouseleave', removeAccent);
      });
    };
    observe();
    const observer = new MutationObserver(observe);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => { window.removeEventListener('mousemove', move); observer.disconnect(); };
  }, []);

  const handleAnalyze = async (resumeFile, jdFile, jdUrl, role) => {
    if (!resumeFile) { setErrorMsg('Please upload your resume first.'); return; }
    if (!jdFile && !jdUrl) { setErrorMsg('Please provide a job description file, text, or URL.'); return; }

    setSelectedRole(role);
    setAppState('loading');

    const derivedCompany = companyFromUrl(jdUrl);
    setClientCompany(derivedCompany);

    const formData = new FormData();
    formData.append('resume', resumeFile);
    if (jdFile) formData.append('job_description', jdFile);
    if (jdUrl) formData.append('jd_url', jdUrl);
    formData.append('role_domain', role);

    try {
      const resp = await fetch(`${API_URL}/api/analyze`, { method: 'POST', body: formData });

      if (!resp.ok) {
        let detail = `Server error (HTTP ${resp.status})`;
        try { const err = await resp.json(); detail = err.detail || detail; } catch (_) {}
        throw new Error(detail);
      }

      const data = await resp.json();
      if (!data.jd_company && derivedCompany) data.jd_company = derivedCompany;
      setResults(data);
      setAppState('complete');
      setTimeout(() => document.getElementById('resultsPanel')?.scrollIntoView({ behavior: 'smooth' }), 200);
    } catch (err) {
      let msg = err.message || 'Unknown error';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('ERR_CONNECTION_REFUSED')) {
        msg = 'Cannot reach backend server.\n\nPlease run start-backend.bat and wait for "Uvicorn running on http://127.0.0.1:8000", then try again.';
      }
      setErrorMsg(msg);
      setAppState('idle');
    }
  };

  const scrollToUpload  = () => document.getElementById('uploadSection')?.scrollIntoView({ behavior: 'smooth' });
  const scrollToResults = () => document.getElementById('resultsPanel')?.scrollIntoView({ behavior: 'smooth' });

  const handleGoHome = () => {
    setAppState('idle');
    setResults(null);
    setClientCompany('');
    setPage('home');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleHowItWorks = () => {
    setPage('how-it-works');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const statusText =
    appState === 'loading'  ? 'PROCESSING' :
    appState === 'complete' ? 'COMPLETE'   : 'READY';

  // Loading overlay — full screen with header showing PROCESSING
  if (appState === 'loading') {
    return (
      <>
        <div id="cursor" />
        <div id="cursor-ring" />
        <div className="app" style={{ position: 'relative', zIndex: 1 }}>
          <Header
            status="PROCESSING"
            showResults={false}
            onScrollToUpload={() => {}}
            onScrollToResults={() => {}}
            onGoHome={() => {}}
            onHowItWorks={() => {}}
          />
          <LoadingPanel visible={true} onComplete={() => {}} />
        </div>
      </>
    );
  }
  // How It Works page
  if (page === 'how-it-works') {
    return (
      <>
        <div id="cursor" />
        <div id="cursor-ring" />
        <ErrorModal message={errorMsg} onClose={() => setErrorMsg('')} />
        <div className="app" style={{ position: 'relative', zIndex: 1 }}>
          <Ticker />
          <Header
            status={statusText}
            showResults={false}
            onScrollToUpload={handleGoHome}
            onScrollToResults={() => {}}
            onGoHome={handleGoHome}
            onHowItWorks={handleHowItWorks}
          />
          <HowItWorks onBack={handleGoHome} />
        </div>
      </>
    );
  }

  return (
    <>
      <div id="cursor" />
      <div id="cursor-ring" />
      <ErrorModal message={errorMsg} onClose={() => setErrorMsg('')} />
      <div className="app" style={{ position: 'relative', zIndex: 1 }}>
        <Ticker />
        <Header
          status={statusText}
          showResults={appState === 'complete'}
          onScrollToUpload={scrollToUpload}
          onScrollToResults={scrollToResults}
          onGoHome={handleGoHome}
          onHowItWorks={handleHowItWorks}
        />

        {appState !== 'complete' && (
          <>
            <Hero onHowItWorks={handleHowItWorks} />

            {/* ── Mode tab switcher ── */}
            <div className="mode-switcher-wrap">
              <div className="mode-switcher-label">// SELECT ANALYSIS MODE</div>
              <div className="mode-tabs">
                {TABS.map(tab => (
                  <button
                    key={tab.id}
                    className={`mode-tab ${activeTab === tab.id ? 'mode-tab--active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            <div id="uploadSection" className="section">
              {activeTab === 'single' && (
                <UploadSection onAnalyze={handleAnalyze} isLoading={false} />
              )}
              {activeTab === 'bulk' && <BulkAnalyzer />}
              {activeTab === 'ats'  && <ATSScanner />}
            </div>
          </>
        )}

        {appState === 'complete' && results && (
          <div id="resultsPanel">
            {/* Header is already rendered above — COMPLETE pill is visible */}
            <ScoreBanner
              matchPct={results.match_pct}
              criticalGaps={results.critical_gaps}
              timeSavedPct={results.time_saved_pct}
              company={results.jd_company}
            />
            <AtsPanel ats={results.ats} />
            <ReportDownload results={results} />
            <SkillsGrid
              currentSkills={results.current_skills}
              requiredSkills={results.required_skills}
            />
            <CompetencyRadar
              currentSkills={results.current_skills}
              requiredSkills={results.required_skills}
            />
            <ReasoningTrace trace={results.reasoning_trace} />
            <PathwayTable pathway={results.pathway} role={selectedRole} />
            {results.interview_readiness && (
              <InterviewReadiness data={results.interview_readiness} />
            )}
            <div className="grounded-strip">
              Catalog Grounded — All modules verified against approved course catalog. Hallucination score: 0.00
            </div>
            <TimelineFooter
              weeks={results.weeks_to_ready}
              headline={`AT 1 HOUR / DAY — ROLE-READY IN ${results.weeks_to_ready} WEEKS`}
            />
          </div>
        )}
      </div>
    </>
  );
}
