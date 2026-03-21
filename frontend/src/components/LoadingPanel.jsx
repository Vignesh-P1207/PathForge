import { useState, useEffect, useRef } from 'react';
import NeuralCanvas from './NeuralCanvas';

const STEPS = [
  'EXTRACTING TEXT FROM RESUME...',
  'PARSING JOB DESCRIPTION REQUIREMENTS...',
  'RUNNING SKILL EXTRACTION ENGINE...',
  'COMPUTING SKILL GAP MATRIX...',
  'BUILDING PREREQUISITE DAG...',
  'GENERATING PERSONALISED LEARNING MODULES...',
  'GROUNDING OUTPUT AGAINST COURSE CATALOG...',
  'ASSEMBLING REASONING TRACE...',
];

export default function LoadingPanel({ visible, onComplete }) {
  const [currentStep, setCurrentStep] = useState(-1);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!visible) {
      setCurrentStep(-1);
      return;
    }

    let step = 0;
    setCurrentStep(0);

    intervalRef.current = setInterval(() => {
      step++;
      if (step < STEPS.length) {
        setCurrentStep(step);
      } else {
        clearInterval(intervalRef.current);
      }
    }, 600);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [visible, onComplete]);

  return (
    <div className={`loading-panel ${visible ? 'visible' : ''}`}>
      <NeuralCanvas opacity={0.4} />
      <div style={{ position: 'relative', zIndex: 2, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div className="loading-heading">
          ANALYZ<span className="blink">_</span>/ING.
        </div>
        <div className="loading-steps">
          {STEPS.map((text, i) => {
            let cls = '';
            if (i < currentStep) cls = 'done';
            else if (i === currentStep) cls = 'active';

            return (
              <div key={i} className={`loading-step ${cls}`}>
                <div className="step-dot" />
                <span>{text}</span>
                <div className="step-bar">
                  <div className="step-bar-fill" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
