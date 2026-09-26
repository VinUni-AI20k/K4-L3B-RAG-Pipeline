// src/components/Sidebar.jsx
const PROVIDERS = [
  { id: 'openai', name: 'OpenAI (GPT-4o)', icon: '⚡' },
  { id: 'gemini', name: 'Google Gemini', icon: '💎' },
  { id: 'anthropic', name: 'Anthropic Claude', icon: '🧠' },
];

const MODELS = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
  gemini: ['gemini-2.0-flash', 'gemini-1.5-pro'],
  anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
};

export default function Sidebar({
  config,
  onChange,
  onClear,
  theme,
  onToggleTheme,
  apiOnline,
}) {
  const { topK, threshold, provider, model, usePageindex } = config;

  return (
    <aside className="sidebar">
      {/* Brand Hero Card */}
      <div className="sidebar-brand-box">
        <div className="sidebar-brand-header">
          <div className="sidebar-brand-icon">🧭</div>
          <div className="sidebar-brand-text">
            <h1 className="sidebar-brand-title">TravelBot RAG</h1>
            <p className="sidebar-brand-sub">AI Travel Knowledge Base</p>
          </div>
        </div>

        <div className="sidebar-status-badge">
          <span className={`status-dot ${apiOnline ? 'status-online' : 'status-mock'}`} />
          <span>{apiOnline ? 'Live API (Port 8000)' : 'Demo Engine (Mock Active)'}</span>
        </div>
      </div>

      <div className="sidebar-content">
        {/* Theme & Mode Quick Toggle */}
        <div className="sidebar-quick-bar">
          <button
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            title={theme === 'dark' ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối'}
          >
            <span>{theme === 'dark' ? '☀️ Giao diện Sáng' : '🌙 Giao diện Tối'}</span>
          </button>
        </div>

        {/* Section: Retrieval */}
        <div className="sidebar-section">
          <div className="sidebar-section-title">
            <span>⚙️ Cấu hình Retrieval</span>
          </div>

          <div className="control-group">
            <div className="control-label">
              <span>Số chunks truy xuất (top_k)</span>
              <span className="control-val-pill">{topK}</span>
            </div>
            <input
              type="range"
              min={1}
              max={10}
              value={topK}
              onChange={e => onChange('topK', +e.target.value)}
            />
          </div>

          <div className="control-group">
            <div className="control-label">
              <span>Ngưỡng điểm (threshold)</span>
              <span className="control-val-pill">{threshold.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={threshold}
              onChange={e => onChange('threshold', +e.target.value)}
            />
          </div>

          <div className="toggle-row">
            <div className="toggle-info">
              <span className="toggle-label">PageIndex Fallback</span>
              <span className="toggle-sub">Chỉ mục vectorless khi cần</span>
            </div>
            <div
              className={`toggle ${usePageindex ? 'on' : ''}`}
              onClick={() => onChange('usePageindex', !usePageindex)}
              title="Bật/Tắt PageIndex"
            >
              <div className="toggle-thumb" />
            </div>
          </div>
        </div>

        <div className="sidebar-divider" />

        {/* Section: LLM Model */}
        <div className="sidebar-section">
          <div className="sidebar-section-title">
            <span>🤖 Mô hình ngôn ngữ</span>
          </div>

          <div className="control-group">
            <label className="control-label">Nhà cung cấp LLM</label>
            <div className="custom-select-wrap">
              <select
                value={provider}
                onChange={e => {
                  onChange('provider', e.target.value);
                  onChange('model', '');
                }}
              >
                {PROVIDERS.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.icon} {p.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="control-group">
            <label className="control-label">Tên Model</label>
            <div className="custom-select-wrap">
              <select value={model} onChange={e => onChange('model', e.target.value)}>
                <option value="">— Mặc định của hệ thống —</option>
                {(MODELS[provider] || []).map(m => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="sidebar-divider" />

        {/* Section: Actions */}
        <div className="sidebar-section">
          <button className="btn-clear-chat" onClick={onClear}>
            <span>🗑️</span>
            <span>Xoá lịch sử hội thoại</span>
          </button>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <p>K4 RAG Pipeline · Travel Knowledge Base</p>
        <span className="version-pill">v1.2 SaaS Ready</span>
      </div>
    </aside>
  );
}
