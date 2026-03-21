import { useState } from 'react';
import ErrorModal from './ErrorModal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ReportDownload({ results }) {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleDownload = async () => {
    if (!results) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results),
      });
      if (!resp.ok) throw new Error('PDF generation failed');
      const { pdf_base64 } = await resp.json();
      const bytes = Uint8Array.from(atob(pdf_base64), c => c.charCodeAt(0));
      const blob = new Blob([bytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pathforge-report.pdf';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setErrorMsg(`PDF download failed.\n\n${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-download-wrap">
      <ErrorModal message={errorMsg} onClose={() => setErrorMsg('')} />
      <button className="report-download-btn" onClick={handleDownload} disabled={loading}>
        {loading ? (
          <><span className="report-btn-icon">⏳</span>GENERATING PDF...</>
        ) : (
          <><span className="report-btn-icon">↓</span>DOWNLOAD REPORT</>
        )}
      </button>
      <div className="report-download-sub">Full analysis · ATS score · Learning pathway · PDF</div>
    </div>
  );
}
