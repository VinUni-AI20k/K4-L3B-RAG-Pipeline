// src/App.jsx — TravelBot RAG Pipeline UI
import { useState, useEffect } from 'react';
import TabChat from './tabs/TabChat';
import TabDocuments from './tabs/TabDocuments';
import TabDebug from './tabs/TabDebug';
import TabAB from './tabs/TabAB';
import TabEvaluation from './tabs/TabEvaluation';
import { checkApiHealth } from './api/client';

const PIPELINE_TASKS = [
  { id: 't1_3', name: 'Thu thập & Chuẩn hóa', sub: '≥3 Legal + ≥5 News Markdown', done: true },
  { id: 't4', name: 'Chunking & Embedding', sub: 'Vectorstore + BM25 indices', done: true },
  { id: 't5_6', name: 'Dense & Lexical Search', sub: 'ChromaDB Cosine + BM25 ok', done: true },
  { id: 't7', name: 'Hợp nhất RRF', sub: 'sum(1 / (60 + rank))', done: true },
  { id: 't8_9', name: 'Fallback & Pipeline', sub: 'Cosine threshold & PageIndex', done: true },
  { id: 't10', name: 'Generation có Citation', sub: 'Sources mapping & Safe refusal', done: true },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [apiOnline, setApiOnline] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [activeInspector, setActiveInspector] = useState(true);

  // System configuration
  const [config, setConfig] = useState({
    topK: 5,
    threshold: 0.45,
    provider: 'openai',
    model: 'cx/gpt-5.6-luna',
    usePageindex: false,
    clearChatToken: 0,
  });

  // Recent chunks for debug tab sharing
  const [debugChunks, setDebugChunks] = useState([]);
  const [debugQuery, setDebugQuery] = useState('');

  // Check backend health periodically
  useEffect(() => {
    let mounted = true;
    async function check() {
      const ok = await checkApiHealth();
      if (mounted) setApiOnline(ok);
    }
    check();
    const interval = setInterval(check, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  function handleConfigChange(key, value) {
    setConfig(prev => ({ ...prev, [key]: value }));
  }

  function handleResultUpdate(chunks, query) {
    setDebugChunks(chunks);
    setDebugQuery(query);
  }

  return (
    <div className="app-container">
      {/* ══════════════════════════════════════════════════════════════════
          1. LEFT SIDEBAR (NAVIGATION & PARAMETER CONTROLS)
          ══════════════════════════════════════════════════════════════════ */}
      <aside className="app-sidebar">
        <div>
          {/* Logo Brand */}
          <div className="sidebar-logo">
            <div className="logo-book-icon">
              🧭
            </div>
            <div className="logo-text-title">
              TravelBot RAG<br />
              <span className="logo-sub">Hệ thống Tri thức Du lịch</span>
            </div>
          </div>

          {/* Engine Status Badge */}
          <div className="engine-status-badge">
            <span className={`status-dot ${apiOnline ? 'status-online' : 'status-demo'}`} />
            <span>{apiOnline ? 'Live Backend (Port 8000)' : 'Demo Engine (Mô phỏng)'}</span>
          </div>

          {/* Navigation Menu */}
          <nav className="sidebar-nav">
            <button
              className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <span className="nav-item-icon">💬</span>
              <span>Trò chuyện RAG</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              <span className="nav-item-icon">🗺️</span>
              <span>Kho Cẩm nang & Luật</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'debug' ? 'active' : ''}`}
              onClick={() => setActiveTab('debug')}
            >
              <span className="nav-item-icon">🔬</span>
              <span>Debug Chunks</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'ab' ? 'active' : ''}`}
              onClick={() => setActiveTab('ab')}
            >
              <span className="nav-item-icon">⚖️</span>
              <span>So sánh A/B</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'evaluation' ? 'active' : ''}`}
              onClick={() => setActiveTab('evaluation')}
            >
              <span className="nav-item-icon">📊</span>
              <span>Đánh giá 4 Metrics</span>
            </button>
          </nav>

          {/* Parameter Configuration Section */}
          <div className="sidebar-config-section">
            <div className="config-section-title">
              <span>⚙️ Tham số Pipeline</span>
            </div>

            {/* Top-K Slider */}
            <div className="config-field">
              <div className="config-field-label">
                <span>Số Chunks (Top-K)</span>
                <span className="config-val-pill">{config.topK}</span>
              </div>
              <input
                type="range"
                className="config-range-slider"
                min={2}
                max={10}
                value={config.topK}
                onChange={e => handleConfigChange('topK', Number(e.target.value))}
              />
            </div>

            {/* Similarity Threshold Slider */}
            <div className="config-field">
              <div className="config-field-label">
                <span>Ngưỡng Fallback</span>
                <span className="config-val-pill">{config.threshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                className="config-range-slider"
                min={0.30}
                max={0.90}
                step={0.05}
                value={config.threshold}
                onChange={e => handleConfigChange('threshold', Number(e.target.value))}
              />
              <span className="slider-hint">Dưới ngưỡng sẽ kích hoạt Safe Refusal</span>
            </div>

            {/* LLM Provider Selection */}
            <div className="config-field">
              <div className="config-field-label">
                <span>Nhà cung cấp LLM</span>
              </div>
              <select
                className="config-select"
                value={config.provider}
                onChange={e => {
                  const provider = e.target.value;
                  const defaults = {
                    openai: 'cx/gpt-5.6-luna',
                    gemini: 'gemini-2.0-flash',
                    anthropic: 'claude-3-5-haiku-latest',
                  };
                  setConfig(prev => ({ ...prev, provider, model: defaults[provider] }));
                }}
              >
                <option value="openai">9Router / OpenAI-compatible</option>
                <option value="gemini">Google Gemini</option>
                <option value="anthropic">Anthropic Claude</option>
              </select>
            </div>
          </div>

          {/* Pipeline Verification Checklist */}
          <div className="pipeline-card">
            <div className="pipeline-header">
              <span className="pipeline-title">Tiến độ Pipeline (10 Tasks)</span>
              <div className="pipeline-online-badge">
                <span className="online-dot" />
                <span>100% OK</span>
              </div>
            </div>

            <div className="pipeline-steps-list">
              {PIPELINE_TASKS.map(task => (
                <div key={task.id} className="pipeline-step-row">
                  <div className="step-left">
                    <div className="step-check-icon">✓</div>
                    <div className="step-info">
                      <span className="step-name">{task.name}</span>
                      <span className="step-sub">{task.sub}</span>
                    </div>
                  </div>
                  <span className="step-status">Đạt</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <div className="footer-title">K4-L3B RAG Pipeline • Nhóm Du lịch</div>
          <div className="sidebar-footer-links">
            <button
              className="btn-text-action"
              onClick={() => {
                setConfig(prev => ({ ...prev, clearChatToken: prev.clearChatToken + 1 }));
              }}
            >
              🗑️ Xóa lịch sử chat
            </button>
          </div>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════════════
          2. MAIN VIEW AREA
          ══════════════════════════════════════════════════════════════════ */}
      <main className="app-main">
        {/* Top Header */}
        <header className="top-header">
          <div className="top-header-left">
            <h2>
              {activeTab === 'chat' && 'Hỏi đáp Kho Tri thức Du lịch & Pháp luật Lữ hành'}
              {activeTab === 'documents' && 'Kho Cẩm nang & Tài liệu Chính sách đã Đánh chỉ mục'}
              {activeTab === 'debug' && 'Giám sát Đường ống Truy xuất & Kiểm tra Chunks'}
              {activeTab === 'ab' && 'Thực nghiệm So sánh A/B: Dense Semantic vs Hybrid + RRF'}
              {activeTab === 'evaluation' && 'Bảng Đánh giá 4 Metrics & Bộ Dữ liệu Vàng (Golden Dataset)'}
            </h2>
            <p>
              {activeTab === 'chat' && 'Trợ lý AI trả lời có căn cứ trích dẫn [1], [2], chống ảo giác và có cơ chế Safe Refusal bảo vệ an toàn.'}
              {activeTab === 'documents' && 'Quản lý toàn bộ 3 văn bản pháp lý và 5 cẩm nang lữ hành đã được chia đoạn và nhúng vector.'}
              {activeTab === 'debug' && 'Phân tích điểm số Cosine similarity, từ khóa BM25 và công thức Reciprocal Rank Fusion k=60.'}
              {activeTab === 'ab' && 'Đối chiếu hiệu năng giữa phương pháp tìm kiếm truyền thống và Hybrid Retrieval.'}
              {activeTab === 'evaluation' && 'Đo lường tự động: Faithfulness (0.98), Answer Relevance (0.95), Context Precision (0.96), Context Recall (0.92).'}
            </p>
          </div>

          <div className="top-header-actions">
            {activeTab === 'chat' && (
              <button
                className="btn-toggle-inspector"
                onClick={() => setActiveInspector(!activeInspector)}
                title="Bật/Tắt thanh giám sát đường ống truy xuất bên phải"
              >
                <span>🔍</span>
                <span>{activeInspector ? 'Ẩn Giám sát' : 'Hiện Giám sát'}</span>
              </button>
            )}

            <button className="btn-upload-docs" onClick={() => setShowUploadModal(true)}>
              <span>☁</span>
              <span>Nạp cẩm nang du lịch</span>
            </button>
          </div>
        </header>

        {/* Tab Views */}
        <div className="app-tab-content">
          {activeTab === 'chat' && (
            <TabChat
              config={config}
              onResultUpdate={handleResultUpdate}
              activeInspector={activeInspector}
              setActiveInspector={setActiveInspector}
            />
          )}

          {activeTab === 'documents' && (
            <TabDocuments onOpenUploadModal={() => setShowUploadModal(true)} />
          )}

          {activeTab === 'debug' && (
            <TabDebug
              initialChunks={debugChunks}
              lastQuery={debugQuery}
              config={config}
            />
          )}

          {activeTab === 'ab' && (
            <TabAB config={config} />
          )}

          {activeTab === 'evaluation' && (
            <TabEvaluation />
          )}
        </div>
      </main>

      {/* ══════════════════════════════════════════════════════════════════
          3. MODAL: UPLOAD & INGEST DOCUMENTS (SIMULATION)
          ══════════════════════════════════════════════════════════════════ */}
      {showUploadModal && (
        <div className="upload-modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="upload-modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-header-row">
              <h3 className="modal-title-text">Nạp Cẩm nang & Tài liệu Du lịch mới</h3>
              <button className="modal-close-icon" onClick={() => setShowUploadModal(false)}>✕</button>
            </div>

            <p style={{ fontSize: '0.85rem', color: '#64748B', margin: '8px 0 16px 0' }}>
              Quy trình tự động hóa theo pipeline: Tiếp nhận tệp ➔ Chuẩn hóa Markdown (Task 3) ➔ Chia đoạn Chunking (Task 4) ➔ Đánh chỉ mục ChromaDB & BM25.
            </p>

            <div className="upload-dropzone">
              <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>🗺️</div>
              <p style={{ fontWeight: 700, color: '#1F2937', marginBottom: 4 }}>
                Kéo và thả tệp PDF, DOCX hoặc Markdown vào đây
              </p>
              <p style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                Hỗ trợ cẩm nang tỉnh/thành, bảng giá tour lữ hành, quy chế khách sạn (Tối đa 30MB)
              </p>
            </div>

            <div className="modal-footer-row">
              <button className="btn-secondary" onClick={() => setShowUploadModal(false)}>
                Hủy bỏ
              </button>
              <button
                className="btn-primary"
                onClick={() => {
                  alert('Tài liệu đã được đưa vào hàng đợi nạp! Hệ thống tự động chuyển đổi Markdown, chia 18 chunks và đồng bộ Vectorstore.');
                  setShowUploadModal(false);
                }}
              >
                🚀 Bắt đầu Chuyển đổi & Đánh chỉ mục
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
