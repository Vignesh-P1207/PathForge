import { useRef, useEffect } from 'react';

export default function NeuralCanvas({ opacity = 0.4 }) {
  const canvasRef = useRef(null);
  const nodesRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const parent = canvas.parentElement;

    const resize = () => {
      const rect = parent.getBoundingClientRect();
      canvas.width = rect.width * 2;
      canvas.height = rect.height * 2;
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      ctx.scale(2, 2);
    };

    resize();

    const ro = new ResizeObserver(resize);
    ro.observe(parent);

    // Generate 35 stable nodes
    if (!nodesRef.current) {
      nodesRef.current = Array.from({ length: 35 }, () => ({
        x: Math.random(),
        y: Math.random(),
        speed: 0.0003 + Math.random() * 0.0008,
        phase: Math.random() * Math.PI * 2,
        radius: 2 + Math.random() * 2,
      }));
    }

    const nodes = nodesRef.current;

    const draw = (time) => {
      const w = canvas.width / 2;
      const h = canvas.height / 2;
      ctx.clearRect(0, 0, w, h);

      const positions = nodes.map((n) => ({
        x: n.x * w + Math.sin(time * n.speed + n.phase) * 20,
        y: n.y * h + Math.cos(time * n.speed + n.phase * 0.7) * 15,
        radius: n.radius,
      }));

      // Draw connections
      for (let i = 0; i < positions.length; i++) {
        for (let j = i + 1; j < positions.length; j++) {
          const dx = positions[i].x - positions[j].x;
          const dy = positions[i].y - positions[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            const alpha = (1 - dist / 120) * 0.15;
            ctx.beginPath();
            ctx.moveTo(positions[i].x, positions[i].y);
            ctx.lineTo(positions[j].x, positions[j].y);
            ctx.strokeStyle = `rgba(124, 92, 252, ${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for (const pos of positions) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(124, 92, 252, 0.3)';
        ctx.fill();
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);

    return () => {
      ro.disconnect();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="neural-canvas"
      style={{ opacity }}
    />
  );
}
