// src/components/SourceCards.jsx
import { useState } from 'react';
import { ScoreBadge, MethodBadge, TypeChip } from './Badges';

export default function SourceCards({ sources }) {
  const [selectedSource, setSelectedSource] = useState(null);

  if (!sources?.length) return null;

  return (
    <>
      <div className="source-cards-grid">
        {sources.map((src, i) => {
          const meta = src.metadata || {};
          const title = meta.title || `Tài liệu tham khảo #${i + 1}`;
          const url = meta.url || '#';
          const content = src.content || '';
          const score = Number(src.score) || 0;
          const pct = Math.round(score * 100);

          const shortUrl = url.replace(/^https?:\/\//, '');
          const displayUrl = shortUrl.length > 32 ? shortUrl.slice(0, 32) + '…' : shortUrl;

          return (
            <div
              className="source-card"
              key={src.id || i}
              onClick={() => setSelectedSource({ ...src, index: i + 1 })}
              title="Nhấn để xem chi tiết trích dẫn"
            >
              <div className="source-card-header">
                <span className="source-index-badge">#{i + 1}</span>
                <span className="source-title" title={title}>{title}</span>
              </div>

              {content && (
                <p className="source-snippet">
                  {content.slice(0, 115)}…
                </p>
              )}

              {/* Progress bar */}
              <div className="source-score-bar-wrap">
                <div className="source-score-bar">
                  <div
                    className="source-score-fill"
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>

              <div className="source-card-footer">
                <div className="source-badges-row">
                  <ScoreBadge score={score} />
                  <MethodBadge method={src.retrieval_method || 'dense'} />
                  {meta.doc_type && <TypeChip type={meta.doc_type} />}
                </div>

                {url !== '#' && (
                  <a
                    className="source-link-btn"
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={e => e.stopPropagation()}
                    title="Mở tài liệu gốc"
                  >
                    🔗 {displayUrl}
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal preview source */}
      {selectedSource && (
        <div className="modal-backdrop" onClick={() => setSelectedSource(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-wrap">
                <span className="source-index-badge">#{selectedSource.index}</span>
                <h3 className="modal-title">
                  {selectedSource.metadata?.title || 'Chi tiết đoạn trích'}
                </h3>
              </div>
              <button
                className="modal-close-btn"
                onClick={() => setSelectedSource(null)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="modal-meta-row">
                <ScoreBadge score={selectedSource.score ?? 0} />
                <MethodBadge method={selectedSource.retrieval_method || 'dense'} />
                {selectedSource.metadata?.doc_type && (
                  <TypeChip type={selectedSource.metadata.doc_type} />
                )}
                {selectedSource.metadata?.url && (
                  <a
                    href={selectedSource.metadata.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="modal-ext-link"
                  >
                    🌐 Mở liên kết gốc
                  </a>
                )}
              </div>

              <div className="modal-section-title">📄 Nội dung trích dẫn:</div>
              <div className="modal-text-content">
                {selectedSource.content || '(Không có nội dung)'}
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-copy-modal"
                onClick={() => {
                  navigator.clipboard.writeText(selectedSource.content || '');
                  alert('Đã sao chép đoạn trích vào clipboard!');
                }}
              >
                📋 Sao chép trích dẫn
              </button>
              <button
                className="btn-close-modal"
                onClick={() => setSelectedSource(null)}
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
