// src/tabs/TabEvaluation.jsx — Đánh giá RAG Triad, 4 Metrics & Golden Dataset (15 câu)
import { useState } from 'react';
import { GOLDEN_DATASET, EVALUATION_METRICS } from '../data/mockData';

export default function TabEvaluation() {
  const [filterCat, setFilterCat] = useState('all'); // 'all' | 'in-domain' | 'out-of-domain'
  const [selectedQA, setSelectedQA] = useState(null);

  const filteredQuestions = GOLDEN_DATASET.filter(qa => {
    if (filterCat === 'all') return true;
    return qa.category === filterCat;
  });

  const inDomainCount = GOLDEN_DATASET.filter(qa => qa.category === 'in-domain').length;
  const outDomainCount = GOLDEN_DATASET.filter(qa => qa.category === 'out-of-domain').length;
  return (
    <div className="tab-evaluation-container">
      {/* Header Banner */}
      <div className="eval-header-banner">
        <div>
          <h2 className="eval-page-title">📊 Đánh giá Pipeline RAG: 4 Metrics & Golden Dataset</h2>
          <p className="eval-page-sub">
            Đáp ứng tiêu chuẩn đánh giá đồ án nhóm (Task 5 & RESULT.md): Kiểm định tự động trên <strong>Bộ dữ liệu vàng gồm 15 câu hỏi</strong> qua 4 chỉ số cốt lõi của RAG Triad và phân tích so sánh A/B.
          </p>
        </div>

        <div className="eval-badge-box">
          <span className="eval-badge-title">Trạng thái Đánh giá:</span>
          <span className="eval-badge-pass">✓ 15/15 TESTCASES PASSED</span>
        </div>
      </div>

      {/* 4 RAG Metrics Cards */}
      <div className="eval-metrics-grid">
        {Object.entries(EVALUATION_METRICS).map(([key, item]) => {
          const pct = Math.round(item.score * 100);
          return (
            <div key={key} className="eval-metric-card">
              <div className="metric-card-top">
                <span className="metric-name">{item.name}</span>
                <span className="metric-badge">{item.badge}</span>
              </div>

              <div className="metric-score-row">
                <span className="metric-score-val">{item.score}</span>
                <span className="metric-gain-val">{item.gain} vs Dense</span>
              </div>

              {/* Progress bar */}
              <div className="metric-progress-bar">
                <div className="metric-progress-fill" style={{ width: `${pct}%` }} />
              </div>

              <p className="metric-desc">{item.desc}</p>
            </div>
          );
        })}
      </div>

      {/* A/B Benchmark Table */}
      <div className="eval-table-card" style={{ marginBottom: 24 }}>
        <div className="table-card-header">
          <div className="table-title">
            <span>⚖️</span>
            <span>Bảng đối sánh hiệu năng A/B: Dense-only vs Hybrid + RRF</span>
          </div>
          <span className="table-sub-badge">Đo lường trên Golden Dataset (15 câu)</span>
        </div>

        <table className="eval-data-table">
          <thead>
            <tr>
              <th>Chỉ số đánh giá (Evaluation Metric)</th>
              <th>Mục tiêu đánh giá</th>
              <th style={{ width: '130px' }}>Dense Only</th>
              <th style={{ width: '150px' }}>Hybrid + RRF</th>
              <th style={{ width: '120px' }}>Tăng trưởng</th>
              <th style={{ width: '110px' }}>Kết luận</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Faithfulness (Độ trung thực)</strong></td>
              <td>Chống ảo giác (Hallucination), căn cứ vào Context</td>
              <td>0.890</td>
              <td><strong className="text-emerald">0.980</strong></td>
              <td><span className="gain-pill">+10.1%</span></td>
              <td><span className="status-pass-pill">Vượt trội</span></td>
            </tr>
            <tr>
              <td><strong>Answer Relevance (Độ liên quan)</strong></td>
              <td>Mức độ giải quyết đúng thắc mắc của du khách</td>
              <td>0.910</td>
              <td><strong className="text-emerald">0.950</strong></td>
              <td><span className="gain-pill">+4.4%</span></td>
              <td><span className="status-pass-pill">Tối ưu</span></td>
            </tr>
            <tr>
              <td><strong>Context Precision (Độ chính xác ngữ cảnh)</strong></td>
              <td>Tỷ lệ đoạn trích có giá trị nằm ở thứ hạng đầu</td>
              <td>0.840</td>
              <td><strong className="text-emerald">0.960</strong></td>
              <td><span className="gain-pill">+14.3%</span></td>
              <td><span className="status-pass-pill">Vượt trội</span></td>
            </tr>
            <tr>
              <td><strong>Context Recall (Độ bao phủ ngữ cảnh)</strong></td>
              <td>Dữ kiện cần thiết có mặt đầy đủ trong đoạn trích</td>
              <td>0.820</td>
              <td><strong className="text-emerald">0.920</strong></td>
              <td><span className="gain-pill">+12.2%</span></td>
              <td><span className="status-pass-pill">Đạt chuẩn</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Golden Dataset Explorer */}
      <div className="eval-table-card">
        <div className="table-card-header">
          <div className="table-title">
            <span>📋</span>
            <span>Bộ dữ liệu vàng (Golden Dataset) — 15 Câu hỏi chuẩn kiểm thử</span>
          </div>

          <div className="filter-pills-row">
            <button
              className={`filter-pill ${filterCat === 'all' ? 'active' : ''}`}
              onClick={() => setFilterCat('all')}
            >
              Tất cả ({GOLDEN_DATASET.length})
            </button>
            <button
              className={`filter-pill ${filterCat === 'in-domain' ? 'active' : ''}`}
              onClick={() => setFilterCat('in-domain')}
            >
              Trong phạm vi cẩm nang ({inDomainCount})
            </button>
            <button
              className={`filter-pill ${filterCat === 'out-of-domain' ? 'active' : ''}`}
              onClick={() => setFilterCat('out-of-domain')}
            >
              Ngoài vùng (Safe Refusal) ({outDomainCount})
            </button>
          </div>
        </div>

        <table className="eval-data-table">
          <thead>
            <tr>
              <th style={{ width: '65px' }}>ID</th>
              <th style={{ width: '130px' }}>Chủ đề</th>
              <th>Câu hỏi kiểm thử (Query)</th>
              <th style={{ width: '110px' }}>Phương thức</th>
              <th style={{ width: '80px' }}>Score</th>
              <th style={{ width: '130px' }}>Trạng thái</th>
              <th style={{ width: '90px' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredQuestions.map(item => (
              <tr key={item.id}>
                <td>
                  <span className="qa-id-pill">{item.id}</span>
                </td>
                <td>
                  <span className="topic-text">{item.topic}</span>
                </td>
                <td>
                  <div className="qa-query-text">{item.query}</div>
                </td>
                <td>
                  <span className={`method-pill method-${item.optimal_method}`}>
                    {item.optimal_method}
                  </span>
                </td>
                <td>
                  <span className="score-pill">{item.score.toFixed(2)}</span>
                </td>
                <td>
                  <span className={`status-badge ${item.category === 'out-of-domain' ? 'status-refusal' : 'status-pass'}`}>
                    {item.status}
                  </span>
                </td>
                <td>
                  <button
                    className="btn-toggle-expand"
                    onClick={() => setSelectedQA(item)}
                  >
                    Chi tiết
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* QA Detail Modal */}
      {selectedQA && (
        <div className="upload-modal-overlay" onClick={() => setSelectedQA(null)}>
          <div className="upload-modal-box modal-wide" onClick={e => e.stopPropagation()}>
            <div className="modal-header-row">
              <div>
                <span className={`pdf-badge ${selectedQA.category === 'out-of-domain' ? 'badge-legal' : 'badge-news'}`}>
                  TESTCASE {selectedQA.id} • {selectedQA.category.toUpperCase()}
                </span>
                <h3 className="modal-title-text" style={{ marginTop: 6 }}>
                  {selectedQA.query}
                </h3>
              </div>
              <button className="modal-close-icon" onClick={() => setSelectedQA(null)}>✕</button>
            </div>

            <div className="modal-meta-grid">
              <div><strong>Chủ đề:</strong> {selectedQA.topic}</div>
              <div><strong>Phương thức tối ưu:</strong> <span className="method-pill">{selectedQA.optimal_method}</span></div>
              <div><strong>Độ tương đồng:</strong> <span className="score-num">{selectedQA.score.toFixed(2)}</span></div>
              <div><strong>Kết quả kiểm định:</strong> <span className="text-emerald font-bold">{selectedQA.status}</span></div>
            </div>

            <div className="modal-content-area">
              <div className="content-label">CÂU TRẢ LỜI CHUẨN (GROUND TRUTH ANSWER):</div>
              <div className="content-box" style={{ background: '#F0FDF4', borderColor: '#BBF7D0', color: '#166534', marginBottom: 16 }}>
                {selectedQA.ground_truth}
              </div>

              <div className="content-label">CĂN CỨ TÀI LIỆU (GROUND TRUTH CONTEXT):</div>
              <div className="content-box">
                {selectedQA.context_source}
              </div>
            </div>

            <div className="modal-footer-row">
              <button className="btn-secondary" onClick={() => setSelectedQA(null)}>Đóng</button>
              <button
                className="btn-primary"
                onClick={() => {
                  navigator.clipboard.writeText(selectedQA.ground_truth);
                  alert('Đã sao chép Ground Truth vào clipboard!');
                }}
              >
                📋 Sao chép Ground Truth
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
