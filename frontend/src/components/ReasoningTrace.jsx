import { useEffect, useRef } from 'react';
import NeuralCanvas from './NeuralCanvas';

function parseMsg(msg) {
  // Replace <hi>...</hi>, <warn>...</warn>, <ok>...</ok> with styled spans
  return msg
    .replace(/<hi>(.*?)<\/hi>/g, '<span class="hi">$1</span>')
    .replace(/<warn>(.*?)<\/warn>/g, '<span class="warn">$1</span>')
    .replace(/<ok>(.*?)<\/ok>/g, '<span class="ok">$1</span>');
}

export default function ReasoningTrace({ trace = [] }) {
  const listRef = useRef(null);

  useEffect(() => {
    if (!listRef.current) return;
    const lines = listRef.current.querySelectorAll('.trace-line');
    lines.forEach((line, i) => {
      line.style.transitionDelay = `${i * 0.13}s`;
      requestAnimationFrame(() => {
        line.classList.add('visible');
      });
    });
  }, [trace]);

  return (
    <div className="reasoning">
      <NeuralCanvas opacity={0.3} />
      <div className="reasoning-content">
        <div className="reasoning-heading">
          AI <span className="hl">REASONING</span> TRACE
        </div>
        <div className="reasoning-sub">
          // Chain-of-thought output from the neural gap analysis engine
        </div>
        <div className="trace-list" ref={listRef}>
          {trace.map((item, i) => (
            <div key={i} className="trace-line">
              <span className="trace-tag">[{item.tag}]</span>
              <span dangerouslySetInnerHTML={{ __html: parseMsg(item.msg) }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
