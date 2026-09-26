// src/tabs/TabAB.jsx — So sánh A/B Retrieval: Dense-only vs Hybrid + RRF
import { useState, useEffect } from 'react';
import { api } from '../api/client';

const PRESET_QUERIES = [
  'Đà Lạt mùa đông hoa dã quỳ và lẩu gà lá é',
  'Phú Quốc 3N2Đ cáp treo Hòn Thơm và lặn san hô',
  'Đặc sản Hội An mì Cao Lầu giếng Bá Lễ và bánh mì',
  'Hồ sơ thủ tục xin visa du lịch tự túc Nhật Bản VFS',
];

export default function TabAB({ config }) {
  const [query, setQuery] = useState(PRESET_QUERIES[0]);
  const [running, setRunning] = useState(false);
  const [denseResults, setDenseResults] = useState([]);
  const [hybridResults, setHybridResults] = useState([]);
  useEffect(() => {
    runComparison(PRESET_QUERIES[0]);
  }, []);

  async function runComparison(targetQuery) {
    const q = (targetQuery || query).trim();
    if (!q || running) return;
    setRunning(true);
    setQuery(q);

    try {
      const [denseRes, hybridRes] = await Promise.all([
        api.retrieve(q, config?.topK || 5, 'dense'),
        api.retrieve(q, config?.topK || 5, 'hybrid'),
      ]);
      setDenseResults(denseRes.chunks || []);
      setHybridResults(hybridRes.chunks || []);
    } catch {
      setDenseResults([]);
      setHybridResults([]);
    } finally {
      setRunning(false);
    }
  }

  // Calculate statistics
  const denseScores = denseResults.map(c => Number(c.score) || 0);
  const hybridScores = hybridResults.map(c => Number(c.score) || 0);

  const denseMax = denseScores.length > 0 ? Math.max(...denseScores).toFixed(3) : '0.000';
  const denseAvg = denseScores.length > 0 ? (denseScores.reduce((a, b) => a + b, 0) / denseScores.length).toFixed(3) : '0.000';

  const hybridMax = hybridScores.length > 0 ? Math.max(...hybridScores).toFixed(3) : '0.000';
  const hybridAvg = hybridScores.length > 0 ? (hybridScores.reduce((a, b) => a + b, 0) / hybridScores.length).toFixed(3) : '0.000';

  return (
    <div className="tab-ab-container">
      {/* Header Banner */}
      <div className="ab-header-banner">
        <div>
          <h2 className="ab-page-title">⚖️ So sánh A/B Retrieval: Dense-only vs Hybrid + RRF</h2>
          <p className="ab-page-sub">
            Đáp ứng yêu cầu đồ án: Đo lường và đối chứng trực tiếp giữa <strong>ChromaDB Dense Search thuần túy</strong> và <strong>Hybrid Retrieval (Dense + BM25) hợp nhất qua RRF</strong> trên cùng một tập chunks.
          </p>
        </div>

        {/* Quick query presets */}
        <div className="ab-preset-row">
          <span className="preset-label">Query thử nghiệm:</span>
          {PRESET_QUERIES.map((q, idx) => (
            <button
              key={idx}
              className={`preset-btn ${query === q ? 'active' : ''}`}
              onClick={() => runComparison(q)}
            >
              {q.slice(0, 24)}…
            </button>
          ))}
        </div>
      </div>

      {/* Query Search Form */}
      <form
        className="ab-search-form"
        onSubmit={e => {
          e.preventDefault();
          runComparison(query);
        }}
      >
        <div className="ab-input-wrap">
          <span className="ab-search-icon">🔍</span>
          <input
            type="text"
            className="ab-query-input"
            placeholder="Nhập bất kỳ câu hỏi nào để so sánh hiệu năng 2 phương pháp..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={running}>
          {running ? 'Đang so sánh...' : 'Chạy so sánh A/B'}
        </button>
      </form>

      {/* Comparison Summary Banner */}
      <div className="ab-summary-banner">
        <div className="summary-col">
          <div className="summary-label">PHƯƠNG PHÁP A: DENSE ONLY</div>
          <div className="summary-desc">Chỉ dựa trên khoảng cách Cosine từ Vector Embedding</div>
          <div className="summary-metrics">
            <span>Score cao nhất: <strong>{denseMax}</strong></span>
            <span>Score TB: <strong>{denseAvg}</strong></span>
            <span>Chunks: <strong>{denseResults.length}</strong></span>
          </div>
        </div>

        <div className="summary-vs-badge">
          VS
        </div>

        <div className="summary-col col-highlight">
          <div className="summary-label">PHƯƠNG PHÁP B: HYBRID + RRF (KHUYẾN NGHỊ)</div>
          <div className="summary-desc">Kết hợp từ khóa địa danh (BM25) và ngữ nghĩa qua RRF</div>
          <div className="summary-metrics">
            <span>Score cao nhất: <strong className="text-emerald">{hybridMax}</strong> (+{(Number(hybridMax) - Number(denseMax)).toFixed(3)})</span>
            <span>Score TB: <strong className="text-emerald">{hybridAvg}</strong></span>
            <span>RRF Fusion: <strong className="text-teal">k = 60</strong></span>
          </div>
        </div>
      </div>

      {/* Side-by-side Columns */}
      <div className="ab-columns-grid">
        {/* Column A: Dense */}
        <div className="ab-column">
          <div className="ab-col-header col-dense-header">
            <div className="col-header-title">
              <span>☊</span>
              <span>Cột A: Dense Semantic (ChromaDB)</span>
            </div>
            <span className="col-header-badge">Vector Search</span>
          </div>

          <div className="ab-chunks-list">
            {denseResults.length === 0 ? (
              <div className="ab-empty-col">Không có dữ liệu chunks.</div>
            ) : (
              denseResults.map((chunk, i) => {
                const meta = chunk.metadata || {};
                return (
                  <div key={chunk.id || i} className="ab-chunk-item">
                    <div className="ab-chunk-top">
                      <span className="ab-rank-badge">#{i + 1}</span>
                      <span className="ab-chunk-title" title={meta.title}>{meta.title || `Chunk #${i + 1}`}</span>
                      <span className="score-pill">{Number(chunk.score || 0).toFixed(3)}</span>
                    </div>

                    <p className="ab-chunk-content">
                      {chunk.content}
                    </p>

                    <div className="ab-chunk-footer">
                      <span className="method-pill method-dense">dense</span>
                      <span className="ab-meta-tag">{meta.doc_type || 'news'}</span>
                      <span className="ab-meta-tag">{meta.page || `Trang ${i + 1}`}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Column B: Hybrid + RRF */}
        <div className="ab-column">
          <div className="ab-col-header col-hybrid-header">
            <div className="col-header-title">
              <span>⚡</span>
              <span>Cột B: Hybrid (Dense + BM25) + RRF</span>
            </div>
            <span className="col-header-badge badge-active">Hợp nhất RRF</span>
          </div>

          <div className="ab-chunks-list">
            {hybridResults.length === 0 ? (
              <div className="ab-empty-col">Không có dữ liệu chunks.</div>
            ) : (
              hybridResults.map((chunk, i) => {
                const meta = chunk.metadata || {};
                return (
                  <div key={chunk.id || i} className="ab-chunk-item item-promoted">
                    <div className="ab-chunk-top">
                      <span className="ab-rank-badge rank-gold">#{i + 1}</span>
                      <span className="ab-chunk-title" title={meta.title}>{meta.title || `Chunk #${i + 1}`}</span>
                      <span className="score-pill score-highlight">{Number(chunk.score || 0).toFixed(3)}</span>
                    </div>

                    <p className="ab-chunk-content">
                      {chunk.content}
                    </p>

                    <div className="ab-chunk-footer">
                      <span className="method-pill method-hybrid">hybrid rrf</span>
                      <span className="ab-meta-tag">{meta.doc_type || 'news'}</span>
                      <span className="ab-meta-tag">{meta.page || `Trang ${i + 1}`}</span>
                      <span className="rrf-gain-badge">Tối ưu thứ hạng</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
