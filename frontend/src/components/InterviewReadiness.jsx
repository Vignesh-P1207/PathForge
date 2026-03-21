import { useEffect, useRef } from 'react';

const LEVEL_CONFIG = {
  low:    { label: 'NOT READY',         color: '#e63329', bg: 'rgba(230,51,41,0.08)'  },
  medium: { label: 'PARTIALLY READY',   color: '#f59e0b', bg: 'rgba(245,158,11,0.08)' },
  high:   { label: 'INTERVIEW READY',   color: '#22c55e', bg: 'rgba(34,197,94,0.08)'  },
};

const SEVERITY_COLOR = { high: '#e63329', medium: '#f59e0b', low: '#22c55e' };

function ConfidenceArc({ confidence }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const size = 160;
    canvas.width  = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width  = size + 'px';
    canvas.style.height = size + 'px';
    ctx.scale(dpr, dpr);

    const cx = size / 2, cy = size / 2, r = 60;
    const startAngle = Math.PI * 0.75;
    const endAngle   = Math.PI * 2.25;
    const fillAngle  = startAngle + (endAngle - startAngle) * (confidence / 100);

    // Track
    ctx.beginPath();
    ctx.arc(cx, cy, r, startAngle, endAngle);
    ctx.strokeStyle = 'rgba(8,8,13,0.08)';
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Fill
    const grad = ctx.createLinearGradient(0, 0, size, 0);
    grad.addColorStop(0, '#e63329');
    grad.addColorStop(0.5, '#f59e0b');
    grad.addColorStop(1, '#22c55e');
    ctx.beginPath();
    ctx.arc(cx, cy, r, startAngle, fillAngle);
    ctx.strokeStyle = grad;
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Center text
    ctx.fillStyle = '#08080d';
    ctx.font = 'bold 28px "Bebas Neue", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${confidence}%`, cx, cy - 6);

    ctx.fillStyle = '#8a8880';
    ctx.font = '10px "Courier Prime", monospace';
    ctx.fillText('CONFIDENCE', cx, cy + 16);
  }, [confidence]);

  return <canvas ref={canvasRef} />;
}

export default function InterviewReadiness({ data }) {
  if (!data) return null;

  const cfg = LEVEL_CONFIG[data.level] || LEVEL_CONFIG.medium;

  return (
    <section className="ir-section">
      {/* Header */}
      <div className="ir-header">
        <div className="ir-header-left">
          <div className="ir-eyebrow">// INTERVIEW READINESS PREDICTOR</div>
          <div className="ir-title">
            INTERVIEW<br />
            <span className="ir-title-hl">READINESS</span>
          </div>
          <div className="ir-sub">
            AI-assessed confidence score based on skill match, gap severity, and role requirements.
          </div>
        </div>

        <div className="ir-header-right">
          <ConfidenceArc confidence={data.confidence} />
          <div className="ir-level-badge" style={{ background: cfg.bg, color: cfg.color, borderColor: cfg.color }}>
            {cfg.label}
          </div>
          <div className="ir-prep-days">
            <span className="ir-prep-days-val">{data.prep_days}</span>
            <span className="ir-prep-days-label">days to prep</span>
          </div>
        </div>
      </div>

      {/* Danger Zones */}
      {data.danger_zones && data.danger_zones.length > 0 && (
        <div className="ir-zones-wrap">
          <div className="ir-zones-title">
            <span className="ir-zones-icon">⚠</span> DANGER ZONES — Skills to Master Before Interview
          </div>
          <div className="ir-zones-grid">
            {data.danger_zones.map((dz, i) => (
              <div key={i} className="ir-danger-card">
                <div className="ir-danger-card-top">
                  <div className="ir-danger-skill">{dz.skill}</div>
                  <div
                    className="ir-severity-badge"
                    style={{ color: SEVERITY_COLOR[dz.severity], borderColor: SEVERITY_COLOR[dz.severity] }}
                  >
                    {dz.severity.toUpperCase()}
                  </div>
                </div>
                <div className="ir-questions-label">// LIKELY INTERVIEW QUESTIONS</div>
                <ul className="ir-questions-list">
                  {dz.questions.map((q, qi) => (
                    <li key={qi} className="ir-question">{q}</li>
                  ))}
                </ul>
                <div className="ir-prep-strategy">
                  <span className="ir-prep-strategy-label">PREP: </span>
                  {dz.prep_strategy}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strong Zones */}
      {data.strong_zones && data.strong_zones.length > 0 && (
        <div className="ir-zones-wrap ir-zones-wrap--strong">
          <div className="ir-zones-title ir-zones-title--strong">
            <span className="ir-zones-icon ir-zones-icon--strong">✓</span> STRONG ZONES — Leverage These in Interview
          </div>
          <div className="ir-zones-grid">
            {data.strong_zones.map((sz, i) => (
              <div key={i} className="ir-strong-card">
                <div className="ir-strong-card-top">
                  <div className="ir-strong-skill">{sz.skill}</div>
                  <div className="ir-strong-pct">{sz.proficiency}%</div>
                </div>
                <div className="ir-questions-label ir-questions-label--strong">// SHOWCASE QUESTIONS</div>
                <ul className="ir-questions-list ir-questions-list--strong">
                  {sz.questions.map((q, qi) => (
                    <li key={qi} className="ir-question ir-question--strong">{q}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
