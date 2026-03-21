export default function ErrorModal({ message, onClose }) {
  if (!message) return null;

  // Split message into title + body on first newline
  const lines = message.split('\n').filter(Boolean);
  const title = lines[0] || 'Analysis Failed';
  const body  = lines.slice(1).join('\n').trim();

  return (
    <div className="err-overlay" onClick={onClose}>
      <div className="err-modal" onClick={e => e.stopPropagation()}>

        {/* top bar */}
        <div className="err-bar">
          <span className="err-tag">// ERROR</span>
          <button className="err-close" onClick={onClose}>✕</button>
        </div>

        {/* icon + title */}
        <div className="err-head">
          <div className="err-icon">⚠</div>
          <div className="err-title">{title}</div>
        </div>

        {/* body */}
        {body && (
          <div className="err-body">
            {body.split('\n').map((line, i) =>
              line.trim() ? <p key={i}>{line}</p> : null
            )}
          </div>
        )}

        {/* actions */}
        <div className="err-actions">
          <button className="err-btn-primary" onClick={onClose}>
            DISMISS
          </button>
        </div>
      </div>
    </div>
  );
}
