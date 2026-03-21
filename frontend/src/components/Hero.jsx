import NeuralCanvas from './NeuralCanvas';

export default function Hero({ onHowItWorks }) {
  const scrollToUpload = () => {
    document.getElementById('uploadSection')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="hero">
      <div className="hero-watermark">PF</div>

      <div className="hero-left">
        <div className="hero-eyebrow">Intelligent Skill Gap Analysis</div>
        <h1 className="hero-title">
          <span className="line-solid">YOUR</span>
          <span className="line-outline">CAREER</span>
          <span className="line-accent">FORGED.</span>
        </h1>
        <p className="hero-desc">
          Upload your resume and a target job description. Our AI engine extracts
          skills, computes gap matrices, and generates a precision learning pathway
          — all running locally on your machine. Zero cloud APIs. Zero hallucinations.
        </p>
        <div className="hero-cta">
          <button className="btn-primary" onClick={scrollToUpload}>
            Start Analysis
          </button>
          <button className="btn-ghost" onClick={onHowItWorks}>How It Works ↗</button>
        </div>
      </div>

      <div className="hero-right">
        <NeuralCanvas opacity={0.55} />
        <div className="hero-right-content">
          <div className="hero-metric">
            <div className="hero-metric-value c-red">42%</div>
            <div className="hero-metric-label">Avg training time saved</div>
          </div>
          <div className="hero-metric">
            <div className="hero-metric-value c-acc2">0</div>
            <div className="hero-metric-label">Hallucinations. Zero.</div>
          </div>
          <div className="hero-metric">
            <div className="hero-metric-value c-accent">6+</div>
            <div className="hero-metric-label">Role domains supported</div>
          </div>
        </div>
      </div>
    </section>
  );
}
