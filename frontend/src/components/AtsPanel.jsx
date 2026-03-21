import { useEffect, useRef } from 'react';

const DIMENSIONS = [
  { key: 'keyword_match',    label: 'Keyword Match',      weight: '35%' },
  { key: 'format_structure', label: 'Format & Structure', weight: '20%' },
  { key: 'section_coverage', label: 'Section Coverage',   weight: '20%' },
  { key: 'quantification',   label: 'Quantification',     weight: '15%' },
  { key: 'action_verbs',     label: 'Action Verbs',       weight: '10%' },
];

function ScoreRing({ score, grade }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const size = canvas.offsetWidth;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    const cx = size / 2;
    const cy = size / 2;
    const r = size * 0.38;
    const lineW = size * 0.07;
    const startAngle = -Math.PI / 2;
    const endAngle = startAngle + (score / 100) * Math.PI * 2;

    // Track ring
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(8,8,13,0.08)';
    ctx.lineWidth = lineW;
    ctx.stroke();

    // Score arc — color by grade
    const color =
      score >= 85 ? '#7c5cfc' :
      score >= 70 ? '#1a2fff' :
      score >= 55 ? '#f59e0b' : '#e63329';

    ctx.beginPath();
    ctx.arc(cx, cy, r, startAngle, endAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineW;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Score text
    ctx.fillStyle = '#08080d';
    ctx.font = `800 ${size * 0.22}px 'Bebas Neue', sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${score}`, cx, cy - size * 0.04);

    ctx.fillStyle = '#8a8880';
    ctx.font = `600 ${size * 0.08}px 'Barlow Condensed', sans-serif`;
    ctx.letterSpacing = '2px';
    ctx.fillText(grade, cx, cy + size * 0.14);
  }, [score, grade]);

  return <canvas ref={canvasRef} className="ats-ring-canvas" />;
}

export default function AtsPanel({ ats }) {
  if (!ats) return null;

  const { ats_score, ats_grade, dimensions, tips, keyword_hits, keyword_misses, sections_found } = ats;

  return (
    <div className="ats-section">
      {/* Header */}
      <div className="ats-header">
        <div className="ats-title-block">
          <div className="ats-eyebrow">// APPLICANT TRACKING SYSTEM</div>
          <div className="ats-title">
            ATS <span className="ats-title-hl">SCORE</span>
          </div>
          <div className="ats-sub">Resume compatibility analysis against job description</div>
        </div>
        <div className="ats-ring-wrap">
          <ScoreRing score={ats_score} grade={ats_grade} />
        </div>
      </div>

      {/* Dimension bars */}
      <div className="ats-dimensions">
        {DIMENSIONS.map(({ key, label, weight }) => {
          const val = dimensions[key] ?? 0;
          const color = val >= 80 ? 'var(--accent)' : val >= 60 ? 'var(--blue)' : val >= 40 ? '#f59e0b' : 'var(--red)';
          return (
            <div key={key} className="ats-dim">
              <div className="ats-dim-header">
                <span className="ats-dim-label">{label}</span>
                <span className="ats-dim-meta">
                  <span className="ats-dim-weight">wt {weight}</span>
                  <span className="ats-dim-val" style={{ color }}>{val}%</span>
                </span>
              </div>
              <div className="ats-dim-track">
                <div
                  className="ats-dim-fill"
                  style={{ width: `${val}%`, background: color }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Keywords + Sections */}
      <div className="ats-grid">
        {/* Keywords */}
        <div className="ats-card">
          <div className="ats-card-title">KEYWORD ANALYSIS</div>
          <div className="ats-kw-groups">
            <div className="ats-kw-group">
              <div className="ats-kw-group-label ats-kw-hit">✓ Found ({keyword_hits.length})</div>
              <div className="ats-kw-list">
                {keyword_hits.slice(0, 8).map(k => (
                  <span key={k} className="ats-kw-tag ats-kw-tag--hit">{k}</span>
                ))}
              </div>
            </div>
            <div className="ats-kw-group">
              <div className="ats-kw-group-label ats-kw-miss">✗ Missing ({keyword_misses.length})</div>
              <div className="ats-kw-list">
                {keyword_misses.slice(0, 8).map(k => (
                  <span key={k} className="ats-kw-tag ats-kw-tag--miss">{k}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sections */}
        <div className="ats-card">
          <div className="ats-card-title">SECTION COVERAGE</div>
          <div className="ats-sections-list">
            {Object.keys({ experience: 1, education: 1, skills: 1, summary: 1, projects: 1, certifications: 1, achievements: 1 }).map(sec => {
              const found = sections_found.includes(sec);
              return (
                <div key={sec} className={`ats-section-row ${found ? 'found' : 'missing'}`}>
                  <span className="ats-section-icon">{found ? '✓' : '✗'}</span>
                  <span className="ats-section-name">{sec.charAt(0).toUpperCase() + sec.slice(1)}</span>
                  {!found && <span className="ats-section-badge">Add this</span>}
                </div>
              );
            })}
          </div>
        </div>

        {/* Tips */}
        <div className="ats-card ats-card--tips">
          <div className="ats-card-title">IMPROVEMENT TIPS</div>
          {tips.length === 0 ? (
            <div className="ats-tip ats-tip--ok">Your resume is well-optimized for ATS systems.</div>
          ) : (
            <ol className="ats-tips-list">
              {tips.map((tip, i) => (
                <li key={i} className="ats-tip">{tip}</li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}
