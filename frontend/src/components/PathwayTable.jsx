import { useEffect, useRef } from 'react';

export default function PathwayTable({ pathway = [], role = '' }) {
  const tbodyRef = useRef(null);

  useEffect(() => {
    if (!tbodyRef.current) return;
    const rows = tbodyRef.current.querySelectorAll('tr');
    rows.forEach((row, i) => {
      row.style.transitionDelay = `${i * 0.1}s`;
      requestAnimationFrame(() => {
        row.classList.add('visible');
      });
    });
  }, [pathway]);

  const totalHrs = pathway.reduce((sum, p) => sum + parseInt(p.hrs || 0, 10), 0);

  return (
    <section className="pathway-section">
      <div className="pathway-headline">
        LEARNING<br />
        <span className="ghost">PATHWAY</span>
      </div>
      <div className="pathway-meta">
        {pathway.length} modules &nbsp;—&nbsp; {totalHrs} total hours &nbsp;—&nbsp; {role.toUpperCase()}
      </div>

      <table className="pathway-table">
        <thead>
          <tr>
            <th>Period</th>
            <th>Module</th>
            <th>Type</th>
            <th>Duration</th>
            <th>Units</th>
          </tr>
        </thead>
        <tbody ref={tbodyRef}>
          {pathway.map((item, i) => (
            <tr key={i}>
              <td className="td-period">{item.week}</td>
              <td>
                <div className="td-module-title">{item.title}</div>
                <div className="td-module-desc">{item.desc}</div>
              </td>
              <td>
                <span className={`tag-badge ${item.tag}`}>{item.tagLabel}</span>
              </td>
              <td>
                <span className="td-hrs">
                  {item.hrs}<span className="hrs-label">HRS</span>
                </span>
              </td>
              <td className="td-units">{item.mods} units</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
