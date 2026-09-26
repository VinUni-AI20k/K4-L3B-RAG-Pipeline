// src/components/Badges.jsx — Modern badge/chip components
export function ScoreBadge({ score }) {
  const s = Number(score) || 0;
  const pct = Math.round(s * 100);
  const cls = s >= 0.8 ? 'badge-score-hi' : s >= 0.5 ? 'badge-score-md' : 'badge-score-lo';
  const icon = s >= 0.8 ? '✦' : '•';
  return (
    <span className={`badge ${cls}`} title={`Độ tương đồng: ${pct}%`}>
      <span className="badge-dot">{icon}</span>
      <span>{s.toFixed(2)}</span>
      <span className="badge-pct">({pct}%)</span>
    </span>
  );
}

export function MethodBadge({ method }) {
  const m = (method || 'dense').toLowerCase();
  const icons = {
    hybrid: '⚡',
    dense: '🎯',
    bm25: '🔍',
    pageindex: '📑',
  };
  const labels = {
    hybrid: 'HYBRID',
    dense: 'DENSE',
    bm25: 'BM25',
    pageindex: 'PAGEINDEX',
  };
  const cls = `badge-${m}`;
  return (
    <span className={`badge ${cls}`}>
      <span className="badge-icon">{icons[m] || '🔹'}</span>
      <span>{labels[m] || m.toUpperCase()}</span>
    </span>
  );
}

export function TypeChip({ type }) {
  const t = (type || 'doc').toLowerCase();
  const icons = {
    pdf: '📄',
    md: '📝',
    markdown: '📝',
    web: '🌐',
    txt: '📃',
  };
  return (
    <span className="badge badge-type">
      <span className="badge-icon">{icons[t] || '📁'}</span>
      <span>{t.toUpperCase()}</span>
    </span>
  );
}
