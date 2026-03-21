import useAnimatedCount from '../hooks/useAnimatedCount';

export default function TimelineFooter({ weeks, headline }) {
  const weeksDisplay = useAnimatedCount(weeks, 900, '');

  return (
    <div className="timeline-footer">
      <div className="tf-left">
        <div className="tf-left-label">Estimated time to competency</div>
        <div className="tf-left-headline">{headline}</div>
      </div>
      <div className="tf-right">
        <div className="tf-weeks">{weeksDisplay}</div>
        <div className="tf-weeks-label">Weeks to Role-Ready</div>
      </div>
    </div>
  );
}
