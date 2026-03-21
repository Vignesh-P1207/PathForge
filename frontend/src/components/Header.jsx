export default function Header({ status, showResults, onScrollToUpload, onScrollToResults, onGoHome, onHowItWorks }) {
  const pillClass =
    status === 'PROCESSING' ? 'processing' :
    status === 'COMPLETE'   ? 'complete'   : 'ready';

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-logo" onClick={onGoHome} style={{ cursor: 'pointer' }}>
          PATHFORGE
        </div>
        <div className="header-tagline">
          AI ADAPTIVE<br />ONBOARDING ENGINE
        </div>
      </div>
      <div className="header-right">
        <nav className="header-nav">
          <a onClick={onScrollToUpload}>Upload</a>
          <a onClick={onHowItWorks} style={{ cursor: 'pointer' }}>How It Works</a>
          {showResults && <a onClick={onScrollToResults}>Results</a>}
        </nav>
        <div
          className={`status-pill ${pillClass}`}
          onClick={status === 'COMPLETE' ? onGoHome : undefined}
          style={status === 'COMPLETE' ? { cursor: 'pointer' } : {}}
          title={status === 'COMPLETE' ? 'Return to home' : undefined}
        >
          {status}
        </div>
      </div>
    </header>
  );
}
