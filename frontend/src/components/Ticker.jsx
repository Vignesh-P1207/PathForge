export default function Ticker() {
  const items = [
    { text: 'PATHFORGE AI', cls: 'hi' },
    { text: '◆', cls: 'sep' },
    { text: 'ADAPTIVE ONBOARDING ENGINE', cls: 'hi2' },
    { text: '◆', cls: 'sep' },
    { text: 'SKILL GAP ANALYSIS', cls: '' },
    { text: '◆', cls: 'sep' },
    { text: 'PERSONALIZED LEARNING PATHWAYS', cls: 'hi2' },
    { text: '◆', cls: 'sep' },
    { text: 'ZERO HALLUCINATIONS', cls: 'hi' },
    { text: '◆', cls: 'sep' },
    { text: 'GROUNDED AI', cls: '' },
    { text: '◆', cls: 'sep' },
    { text: 'ROLE-SPECIFIC COMPETENCY', cls: 'hi2' },
    { text: '◆', cls: 'sep' },
  ];

  const renderItems = () =>
    items.map((item, i) => (
      <span key={i} className={item.cls}>
        {item.text}
      </span>
    ));

  return (
    <div className="ticker">
      <div className="ticker-track">
        <div className="ticker-inner">{renderItems()}</div>
        <div className="ticker-inner">{renderItems()}</div>
      </div>
    </div>
  );
}
