import useAnimatedCount from '../hooks/useAnimatedCount';
import NeuralCanvas from './NeuralCanvas';

export default function ScoreBanner({ matchPct, criticalGaps, timeSavedPct, company }) {
  const matchDisplay = useAnimatedCount(matchPct, 900, '%');
  const gapsDisplay = useAnimatedCount(criticalGaps, 900, '');
  const savedDisplay = useAnimatedCount(timeSavedPct, 900, '%');

  return (
    <div className="score-banner">
      <NeuralCanvas opacity={0.15} />
      {company && (
        <div className="score-banner-company">
          <span className="score-banner-company-label">// ANALYZING FOR</span>
          <span className="score-banner-company-name">{company}</span>
        </div>
      )}
      <div className="score-banner-metrics">
        <div className="score-block">
          <div className="score-value c-accent">{matchDisplay}</div>
          <div className="score-label">Skill Match Score</div>
        </div>
        <div className="score-block">
          <div className="score-value c-red">{gapsDisplay}</div>
          <div className="score-label">Critical Gaps Found</div>
        </div>
        <div className="score-block">
          <div className="score-value c-blue">{savedDisplay}</div>
          <div className="score-label">Training Time Saved</div>
        </div>
      </div>
    </div>
  );
}
