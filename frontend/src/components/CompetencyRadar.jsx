import { useEffect, useRef } from 'react';

export default function CompetencyRadar({ currentSkills = [], requiredSkills = [] }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Build unified skill list (up to 8 axes)
    const allNames = [
      ...new Set([
        ...requiredSkills.map(s => s.name),
        ...currentSkills.map(s => s.name),
      ]),
    ].slice(0, 8);

    if (allNames.length < 3) return;

    const reqMap = Object.fromEntries(requiredSkills.map(s => [s.name, s.pct]));
    const curMap = Object.fromEntries(currentSkills.map(s => [s.name, s.pct]));

    const axes = allNames.map(name => ({
      label: name,
      required: (reqMap[name] ?? 0) / 100,
      current: (curMap[name] ?? 0) / 100,
    }));

    const dpr = window.devicePixelRatio || 1;
    const W = canvas.offsetWidth;
    const H = canvas.offsetHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    const cx = W / 2;
    const cy = H / 2;
    const R = Math.min(W, H) * 0.36;
    const n = axes.length;

    const angle = (i) => (Math.PI * 2 * i) / n - Math.PI / 2;
    const pt = (i, r) => ({
      x: cx + Math.cos(angle(i)) * R * r,
      y: cy + Math.sin(angle(i)) * R * r,
    });

    ctx.clearRect(0, 0, W, H);

    // Grid rings
    [0.25, 0.5, 0.75, 1].forEach(r => {
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const p = pt(i, r);
        i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
      }
      ctx.closePath();
      ctx.strokeStyle = r === 1 ? 'rgba(8,8,13,0.15)' : 'rgba(8,8,13,0.07)';
      ctx.lineWidth = r === 1 ? 1.5 : 1;
      ctx.stroke();
    });

    // Axis spokes
    axes.forEach((_, i) => {
      const p = pt(i, 1);
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = 'rgba(8,8,13,0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Required polygon (pink/red fill)
    ctx.beginPath();
    axes.forEach((ax, i) => {
      const p = pt(i, ax.required);
      i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(230, 51, 41, 0.12)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(230, 51, 41, 0.55)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Current polygon (accent/blue fill)
    ctx.beginPath();
    axes.forEach((ax, i) => {
      const p = pt(i, ax.current);
      i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(124, 92, 252, 0.18)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(124, 92, 252, 0.85)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Dots on current polygon
    axes.forEach((ax, i) => {
      const p = pt(i, ax.current);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#7c5cfc';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    // Labels
    ctx.font = '600 11px "Barlow Condensed", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    axes.forEach((ax, i) => {
      const labelR = 1.22;
      const p = pt(i, labelR);
      const a = angle(i);

      // Nudge label away from center
      const nudge = 6;
      const lx = p.x + Math.cos(a) * nudge;
      const ly = p.y + Math.sin(a) * nudge;

      ctx.fillStyle = 'rgba(8,8,13,0.65)';
      ctx.letterSpacing = '1px';
      ctx.fillText(ax.label.toUpperCase(), lx, ly);
    });
  }, [currentSkills, requiredSkills]);

  return (
    <div className="radar-section">
      <div className="radar-header">
        <div className="radar-title">
          COMPETENCY <span className="radar-title-hl">RADAR</span>
        </div>
        <div className="radar-sub">// GAP VISUALIZATION</div>
        <div className="radar-legend">
          <div className="legend-row">
            <span className="legend-dot legend-dot--req" />
            <span className="legend-label">Role Required</span>
          </div>
          <div className="legend-row">
            <span className="legend-dot legend-dot--cur" />
            <span className="legend-label">Your Profile</span>
          </div>
        </div>
      </div>
      <div className="radar-canvas-wrap">
        <canvas ref={canvasRef} className="radar-canvas" />
      </div>
    </div>
  );
}
