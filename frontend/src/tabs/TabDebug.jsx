// src/tabs/TabDebug.jsx — Kiểm tra Chunks & Giám sát chi tiết Pipeline RAG
import { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function TabDebug({ initialChunks = [], lastQuery = '', config }) {
  const [query, setQuery] = useState(lastQuery || 'Kinh nghiệm du lịch Đà Lạt mùa đông tiết kiệm');
  const [chunks, setChunks] = useState(initialChunks);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [filterMethod, setFilterMethod] = useState('all');

  // If initialChunks changes from external chat, update
  useEffect(() => {
    if (initialChunks && initialChunks.length > 0) {
      setChunks(initialChunks);
    }
  }, [initialChunks]);

  useEffect(() => {
    if (lastQuery) {
      setQuery(lastQuery);
    }
  }, [lastQuery]);

  // Initial load if no chunks
  useEffect(() => {
    if (!chunks || chunks.length === 0) {
      handleSearch('Kinh nghiệm du lịch Đà Lạt mùa đông tiết kiệm');
    }
  }, []);

  async function handleSearch(searchQuery) {
    const q = (searchQuery || query).trim();
    if (!q || loading) return;
    setLoading(true);
    try {
      const res = await api.retrieve(q, config?.topK || 5, 'hybrid');
      setChunks(res.chunks || []);
    } catch {
      setChunks([]);
    } finally {
      setLoading(false);
    }
  }

  const scores = chunks.map(c => Number(c.score) || 0);
  const maxScore = scores.length > 0 ? Math.max(...scores).toFixed(3) : '0.000';
  const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(3) : '0.000';

  const methodCounts = chunks.reduce((acc, c) => {
    const m = c.retrieval_method || 'hybrid';
    acc[m] = (acc[m] || 0) + 1;
    return acc;
  }, {});

  const filteredChunks = filterMethod === 'all'
    ? chunks
    : chunks.filter(c => (c.retrieval_method || 'hybrid') === filterMethod);

  return (
    <div className="tab-debug-container">
      {/* Header & Search Bar */}
      <div className="debug-header-box">
        <div>
          <h2 className="debug-page-title">🔬 Debug Chunks & Kiểm định Hợp nhất RRF</h2>
          <p className="debug-page-sub">
            Trực quan hóa quá trình xếp hạng các đoạn trích từ ChromaDB Vectorstore và BM25 Lexical Index theo quy chuẩn <code>SearchResult</code>.
          </p>
        </div>

        <form
          className="debug-search-form"
          onSubmit={e => {
            e.preventDefault();
            handleSearch(query);
          }}
        >
          <div className="debug-input-wrap">
            <span className="debug-input-icon">🔍</span>
            <input
              type="text"
              className="debug-query-input"
              placeholder="Nhập câu hỏi để kiểm tra quá trình truy xuất chunks..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Đang truy xuất...' : 'Truy xuất Chunks'}
          </button>
        </form>
      </div>

      {/* KPI Stat Cards */}
      <div className="debug-stats-grid">
        <div className="debug-stat-card">
          <div className="stat-card-label">Tổng số Chunks lấy về</div>
          <div className="stat-card-value text-primary">{chunks.length} chunks</div>
          <div className="stat-card-sub">Theo cấu hình Top-K = {config?.topK || 5}</div>
        </div>

        <div className="debug-stat-card">
          <div className="stat-card-label">Điểm số cao nhất (Max Score)</div>
          <div className="stat-card-value text-emerald">{maxScore}</div>
          <div className="stat-card-sub">Tương đồng ngữ nghĩa cao nhất</div>
        </div>

        <div className="debug-stat-card">
          <div className="stat-card-label">Điểm số trung bình (Avg Score)</div>
          <div className="stat-card-value text-indigo">{avgScore}</div>
          <div className="stat-card-sub">Trung bình cộng các đoạn trích</div>
        </div>

        <div className="debug-stat-card">
          <div className="stat-card-label">Phân bổ Phương thức</div>
          <div className="stat-card-value text-teal" style={{ fontSize: '1.15rem', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {Object.entries(methodCounts).map(([m, cnt]) => (
              <span key={m} className="method-pill">{m}: {cnt}</span>
            ))}
            {Object.keys(methodCounts).length === 0 && 'Chưa có'}
          </div>
          <div className="stat-card-sub">Dense, BM25 hoặc RRF Hybrid</div>
        </div>
      </div>

      {/* Filter by Method */}
      <div className="debug-filter-row">
        <div className="filter-pills-row">
          <button
            className={`filter-pill ${filterMethod === 'all' ? 'active' : ''}`}
            onClick={() => setFilterMethod('all')}
          >
            Tất cả ({chunks.length})
          </button>
          <button
            className={`filter-pill ${filterMethod === 'hybrid' ? 'active' : ''}`}
            onClick={() => setFilterMethod('hybrid')}
          >
            ⚡ Hybrid RRF ({methodCounts['hybrid'] || 0})
          </button>
          <button
            className={`filter-pill ${filterMethod === 'dense' ? 'active' : ''}`}
            onClick={() => setFilterMethod('dense')}
          >
            ☊ Dense Vector ({methodCounts['dense'] || 0})
          </button>
          <button
            className={`filter-pill ${filterMethod === 'bm25' ? 'active' : ''}`}
            onClick={() => setFilterMethod('bm25')}
          >
            📍 BM25 Lexical ({methodCounts['bm25'] || 0})
          </button>
        </div>

        <span className="results-counter">
          Hiển thị <strong>{filteredChunks.length}</strong> / {chunks.length} chunks
        </span>
      </div>

      {/* Table of Chunks */}
      <div className="debug-table-card">
        <table className="debug-data-table">
          <thead>
            <tr>
              <th style={{ width: '60px' }}>Rank</th>
              <th style={{ width: '220px' }}>Tiêu đề tài liệu nguồn</th>
              <th>Nội dung đoạn trích (Chunk Content Preview)</th>
              <th style={{ width: '90px' }}>Score</th>
              <th style={{ width: '110px' }}>Phương thức</th>
              <th style={{ width: '130px' }}>Loại tài liệu</th>
              <th style={{ width: '90px' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredChunks.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                  Không có chunk nào phù hợp với bộ lọc hiện tại.
                </td>
              </tr>
            ) : (
              filteredChunks.map((chunk, idx) => {
                const meta = chunk.metadata || {};
                const isExpanded = expandedId === (chunk.id || idx);
                return (
                  <tr key={chunk.id || idx} className={isExpanded ? 'tr-expanded' : ''}>
                    <td>
                      <div className="rank-badge">#{idx + 1}</div>
                    </td>
                    <td>
                      <div className="chunk-title-cell" title={meta.title || 'N/A'}>
                        {meta.title || `Chunk #${idx + 1}`}
                      </div>
                      <div className="chunk-meta-sub">
                        {meta.page ? `${meta.page} • ` : ''}Chunk #{meta.chunk_index ?? idx + 1}
                      </div>
                    </td>
                    <td>
                      <div className="chunk-preview-text">
                        {chunk.content || '(Nội dung rỗng)'}
                      </div>
                    </td>
                    <td>
                      <span className="score-pill">{Number(chunk.score || 0).toFixed(3)}</span>
                    </td>
                    <td>
                      <span className={`method-pill method-${chunk.retrieval_method || 'hybrid'}`}>
                        {chunk.retrieval_method || 'hybrid'}
                      </span>
                    </td>
                    <td>
                      <span className={`pdf-badge ${meta.doc_type === 'legal' ? 'badge-legal' : 'badge-news'}`}>
                        {meta.doc_type === 'legal' ? 'Pháp lý' : 'Cẩm nang'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-toggle-expand"
                        onClick={() => setExpandedId(isExpanded ? null : (chunk.id || idx))}
                      >
                        {isExpanded ? 'Thu gọn' : 'Chi tiết'}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Expanded Detail Panel if one chunk is opened */}
      {expandedId !== null && (
        <div className="expanded-chunk-viewer">
          {(() => {
            const active = filteredChunks.find((c, i) => (c.id || i) === expandedId) || filteredChunks[0];
            if (!active) return null;
            const meta = active.metadata || {};
            return (
              <div>
                <div className="viewer-header">
                  <div className="viewer-title">
                    📄 Toàn văn Chunk: <strong>{meta.title || active.id}</strong>
                  </div>
                  <button className="btn-close-viewer" onClick={() => setExpandedId(null)}>✕ Đóng</button>
                </div>

                <div className="viewer-body">
                  <div className="viewer-text-box">
                    {active.content}
                  </div>

                  <div className="viewer-meta-box">
                    <div className="meta-box-title">Metadata Contract JSON:</div>
                    <pre className="meta-json-code">
                      {JSON.stringify(
                        {
                          id: active.id,
                          score: active.score,
                          retrieval_method: active.retrieval_method,
                          metadata: meta,
                        },
                        null,
                        2
                      )}
                    </pre>

                    <button
                      className="btn-secondary"
                      style={{ marginTop: 10, width: '100%' }}
                      onClick={() => {
                        navigator.clipboard.writeText(active.content);
                        alert('Đã sao chép nội dung chunk vào clipboard!');
                      }}
                    >
                      📋 Sao chép nội dung Chunk
                    </button>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
