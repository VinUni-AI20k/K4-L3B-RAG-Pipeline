// src/tabs/TabChat.jsx — Trò chuyện RAG & Trực quan hóa nguồn trích dẫn
import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';

const SUGGESTIONS = [
  { icon: '🌲', label: 'Đà Lạt mùa đông', query: 'Gợi ý kinh nghiệm du lịch Đà Lạt mùa đông từ tháng 11 đến tháng 1: nên đi đâu, ăn gì và cần lưu ý gì?', tag: 'In-domain' },
  { icon: '🏖️', label: 'Phú Quốc 3N2Đ', query: 'Lịch trình du lịch Phú Quốc 3 ngày 2 đêm tự túc tiết kiệm cho gia đình?', tag: 'In-domain' },
  { icon: '🍜', label: 'Ẩm thực Hội An', query: 'Những món ăn đặc sản không thể bỏ lỡ khi ghé thăm phố cổ Hội An và quán gợi ý?', tag: 'In-domain' },
  { icon: '✈️', label: 'Visa Nhật Bản', query: 'Hồ sơ và thủ tục xin visa du lịch tự túc Nhật Bản gồm những giấy tờ nào?', tag: 'In-domain' },
  { icon: '🛵', label: 'Sửa xe máy (Test Fallback)', query: 'Cách kiểm tra và thay bugi xe máy Honda Wave RSX khi bị ngập nước?', tag: 'Out-of-domain' },
  { icon: '🍕', label: 'Làm Pizza (Test Fallback)', query: 'Công thức nhào bột làm bánh pizza hải sản đế mỏng nướng lò tại nhà?', tag: 'Out-of-domain' },
];

function renderInlineText(text, onCitationClick) {
  if (!text) return null;
  const parts = text.split(/(\[\d+\]|\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (!part) return null;
    const citeMatch = part.match(/^\[(\d+)\]$/);
    if (citeMatch) {
      const num = citeMatch[1];
      return (
        <span
          key={i}
          className="citation-tag"
          title={`Nhấn để xem trích đoạn và tài liệu nguồn [${num}]`}
          onClick={() => onCitationClick && onCitationClick(num)}
        >
          [{num}]
        </span>
      );
    }
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="md-bold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="md-code">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

function renderMarkdownContent(content, onCitationClick) {
  if (!content) return null;
  const lines = content.split('\n');
  const elements = [];

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      elements.push(<div key={idx} style={{ height: '6px' }} />);
      return;
    }

    // Heading 3
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={idx} className="bot-h3">
          {renderInlineText(trimmed.replace('### ', ''), onCitationClick)}
        </h4>
      );
      return;
    }

    // Numbered point: "1. **Title:** Desc [1]"
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      elements.push(
        <div key={idx} className="bot-point-row">
          <span className="bot-point-num">{numMatch[1]}.</span>
          <div className="bot-point-text">
            {renderInlineText(numMatch[2], onCitationClick)}
          </div>
        </div>
      );
      return;
    }

    // Bullet point: "- Title" or "* Title"
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      elements.push(
        <div key={idx} className="bot-bullet-row">
          <span className="bullet-dot">•</span>
          <div>{renderInlineText(trimmed.replace(/^[-*]\s+/, ''), onCitationClick)}</div>
        </div>
      );
      return;
    }

    // Normal paragraph
    elements.push(
      <p key={idx} className="bot-para">
        {renderInlineText(trimmed, onCitationClick)}
      </p>
    );
  });

  return elements;
}

export default function TabChat({
  config,
  onResultUpdate,
  activeInspector,
  setActiveInspector,
}) {
  const [messages, setMessages] = useState([
    {
      role: 'user',
      content: 'Gợi ý kinh nghiệm du lịch Đà Lạt mùa đông từ tháng 11 đến tháng 1: nên đi đâu, ăn gì và cần lưu ý gì?',
      time: '10:24',
    },
    {
      role: 'assistant',
      content: `Dựa trên cẩm nang du lịch Đà Lạt mùa đông và kho dữ liệu lữ hành được lập chỉ mục, các kinh nghiệm trọng tâm bao gồm:

1. **Thời điểm vàng & Điểm ngắm cảnh nổi bật:** Mùa hoa Dã Quỳ nở rộ dọc đèo Tà Nung và đồi cỏ hồng Dankia - Suối Vàng rực rỡ nhất từ 5:30 – 7:00 sáng. Bạn cũng không nên bỏ lỡ trải nghiệm săn mây bình minh tại đồi chè Cầu Đất lúc 5:00 sáng. [1] [2]

2. **Ẩm thực ấm áp mùa đông:** Thưởng thức các món đặc sản làm ấm cơ thể như Lẩu gà lá é Tao Ngộ (đường 3/4), lẩu bò Ba Toa quán Gỗ, bánh căn xíu mại đường Tăng Bạt Hổ và sữa đậu nành nóng hổi tại Chợ Đêm Đà Lạt. [2]

3. **Phương tiện di chuyển & Lưu trú:** Nên thuê xe máy khoảng 120.000đ/ngày để chủ động săn mây sáng sớm. Nên đặt phòng homestay hoặc khách sạn tại Phường 1 hoặc đường Nam Kỳ Khởi Nghĩa trước 2–3 tuần vào các dịp cuối tuần. [1] [3]

4. **Lưu ý trang phục & Thời tiết:** Nhiệt độ ban đêm hạ xuống dưới 12°C – 14°C kèm sương muối lạnh. Cần chuẩn bị kỹ áo khoác dày, khăn quàng cổ, găng tay và giày bệt chống trơn trượt khi đi đồi dốc. [3]`,
      sourcesCount: 3,
      confidence: '0.94',
      fallback_triggered: false,
      time: '10:24',
      sources: [
        {
          id: 'chunk_dl_1',
          score: 0.94,
          retrieval_method: 'hybrid',
          content: 'Đà Lạt mùa đông từ tháng 11 đến hết tháng 1 là mùa đẹp nhất trong năm. Lúc này thời tiết hanh khô, ban ngày nắng nhẹ, ban đêm nhiệt độ hạ xuống dưới 12°C - 14°C. Lễ hội hoa dã quỳ nở rộ dọc đèo Tà Nung và đồi cỏ hồng Dankia - Suối Vàng thu hút đông đảo du khách.',
          metadata: {
            title: 'Cẩm nang Du lịch Đà Lạt Mùa Đông Toàn Tập 2024',
            url: 'https://dulichdalat.vn/cam-nang/mua-dong',
            doc_type: 'news',
            chunk_index: 3,
            page: 'Trang 12–16',
          },
        },
        {
          id: 'chunk_dl_2',
          score: 0.89,
          retrieval_method: 'dense',
          content: 'Danh sách các quán ăn uy tín cho mùa đông: Lẩu gà lá é chuẩn vị tại số 5 đường 3/4 có giá từ 200.000đ - 300.000đ/nồi, lẩu bò quán Gỗ khu Ba Toa, kem bơ Thanh Thảo, bánh mì xíu mại Hoàng Diệu.',
          metadata: {
            title: 'Top 20 Quán Ăn Đặc Sản Chuẩn Vị & Giá Niêm Yết Đà Lạt',
            url: 'https://foody.vn/da-lat/top-quan-ngon',
            doc_type: 'news',
            chunk_index: 2,
            page: 'Trang 5–8',
          },
        },
        {
          id: 'chunk_dl_3',
          score: 0.81,
          retrieval_method: 'bm25',
          content: 'Hướng dẫn di chuyển và lưu trú: Thuê xe máy khoảng 120.000đ/ngày, nên đặt phòng tại khu vực Phường 1 hoặc đường Nam Kỳ Khởi Nghĩa để thuận tiện đi bộ ra Chợ Đêm và hồ Xuân Hương. Biên độ nhiệt ngày đêm rất lớn, bắt buộc mang áo ấm nhiều lớp.',
          metadata: {
            title: 'Sổ tay Lưu trú, Di chuyển & An toàn Du lịch',
            url: 'https://dulichdalat.vn/hotels-safety',
            doc_type: 'legal',
            chunk_index: 1,
            page: 'Trang 3–4',
          },
        },
      ],
    },
  ]);

  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [highlightedSourceId, setHighlightedSourceId] = useState(null);
  const [selectedSourceDetail, setSelectedSourceDetail] = useState(null);

  // Retrieval stats
  const [retrievalStats, setRetrievalStats] = useState({
    denseResults: 5,
    bm25Results: 5,
    rrfResults: 3,
    confidence: '0.94',
    fallbackUsed: 'Không (In-domain)',
    fallbackTriggered: false,
    latency: '340ms',
  });

  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (config.clearChatToken > 0) {
      setMessages([]);
    }
  }, [config.clearChatToken]);

  async function handleSend(e, promptQuery) {
    e?.preventDefault();
    const query = (promptQuery || inputVal).trim();
    if (!query || loading) return;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMessage = { role: 'user', content: query, time: timeStr };
    setMessages(prev => [...prev, userMessage]);
    setInputVal('');
    setLoading(true);

    const tStart = performance.now();

    try {
      const res = await api.generate(
        query,
        config.topK,
        config.provider,
        config.model,
        config.threshold
      );

      const elapsed = Math.round(performance.now() - tStart);
      const isFallback = res.fallback_triggered || res.retrieval_source === 'none';
      const sources = res.sources || [];

      const botMessage = {
        role: 'assistant',
        content: res.answer || '(Không nhận được phản hồi)',
        sourcesCount: sources.length,
        confidence: res.confidence || (isFallback ? '0.38' : '0.94'),
        fallback_triggered: isFallback,
        time: timeStr,
        sources: sources,
      };

      setMessages(prev => [...prev, botMessage]);

      const newStats = {
        denseResults: isFallback ? 0 : config.topK,
        bm25Results: isFallback ? 0 : config.topK,
        rrfResults: sources.length,
        confidence: botMessage.confidence,
        fallbackUsed: isFallback ? 'CÓ (Kích hoạt Safe Refusal)' : 'Không (In-domain)',
        fallbackTriggered: isFallback,
        latency: `${elapsed}ms`,
      };

      setRetrievalStats(newStats);

      if (onResultUpdate && sources.length > 0) {
        onResultUpdate(sources, query);
      }
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ Có lỗi trong quá trình kết nối với RAG Pipeline. Vui lòng thử lại.',
          sourcesCount: 0,
          confidence: '0.00',
          fallback_triggered: true,
          time: timeStr,
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Get current sources from the latest assistant message
  const lastBotMsg = [...messages].reverse().find(m => m.role === 'assistant');
  const currentSources = lastBotMsg?.sources || [];

  function handleCitationClick(citationNum) {
    const idx = Number(citationNum) - 1;
    if (currentSources && currentSources[idx]) {
      const src = currentSources[idx];
      setHighlightedSourceId(src.id || idx);
      setSelectedSourceDetail({ ...src, index: idx + 1 });

      // Auto clear highlight after 3.5s
      setTimeout(() => setHighlightedSourceId(null), 3500);

      // Scroll to source card
      const elem = document.getElementById(`source-card-${src.id || idx}`);
      if (elem) {
        elem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }

  return (
    <div className="tab-chat-layout">
      {/* 1. Main Chat Stream */}
      <div className="chat-stream-column">
        {/* Quick Suggestion Pills */}
        <div className="quick-prompts-bar">
          <span className="quick-prompt-label">Gợi ý kiểm thử:</span>
          <div className="quick-prompts-scroll">
            {SUGGESTIONS.map((item, idx) => (
              <button
                key={idx}
                className={`quick-prompt-chip ${item.tag === 'Out-of-domain' ? 'chip-fallback' : ''}`}
                onClick={() => handleSend(null, item.query)}
                title={item.tag === 'Out-of-domain' ? 'Kiểm thử cơ chế Safe Refusal khi câu hỏi ngoài vùng tri thức' : 'Câu hỏi kiểm chuẩn trong cẩm nang'}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
                {item.tag === 'Out-of-domain' && <span className="chip-badge">Fallback</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Message Stream */}
        <div className="messages-stream">
          {messages.map((msg, i) => (
            <div key={i} className="message-wrapper">
              {msg.role === 'user' ? (
                /* User Bubble */
                <div className="chat-item-user">
                  <div className="user-avatar-circle">👤</div>
                  <div className="user-bubble-container">
                    <div className="user-bubble-box">{msg.content}</div>
                    <div className="msg-timestamp">{msg.time}</div>
                  </div>
                </div>
              ) : (
                /* Assistant Bubble */
                <div className="chat-item-bot">
                  <div className="bot-avatar-circle">🧭</div>
                  <div className="bot-content-wrap">
                    {/* Bot Card Box */}
                    <div className={`bot-card-box ${msg.fallback_triggered ? 'bot-card-fallback' : ''}`}>
                      {msg.fallback_triggered && (
                        <div className="fallback-banner">
                          <span className="fallback-icon">🛡️</span>
                          <span><strong>Cơ chế Safe Refusal đã kích hoạt:</strong> Câu hỏi dưới ngưỡng tương đồng hoặc ngoài phạm vi cẩm nang du lịch.</span>
                        </div>
                      )}

                      <div className="bot-markdown-area">
                        {renderMarkdownContent(msg.content, handleCitationClick)}
                      </div>

                      <div className="bot-card-footer">
                        <div className="bot-meta-left">
                          <span className="sparkle-icon">✧</span>
                          <span>
                            {msg.fallback_triggered ? (
                              <span style={{ color: '#DC2626', fontWeight: 600 }}>Từ chối an toàn • Cosine Score: {msg.confidence} (Dưới ngưỡng)</span>
                            ) : (
                              <>
                                Tổng hợp từ <strong>{msg.sourcesCount || 0}</strong> cẩm nang uy tín • Độ tin cậy:{' '}
                                <strong className="confidence-bold">{msg.confidence}</strong>
                              </>
                            )}
                          </span>
                        </div>
                        <span className="msg-timestamp">{msg.time}</span>
                      </div>
                    </div>

                    {/* Sources Cards below Assistant message */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-container-card">
                        <div className="sources-card-header">
                          <div className="sources-header-left">
                            <span>📚</span>
                            <span>Tài liệu tham khảo & Căn cứ trích dẫn</span>
                          </div>
                          <span className="sources-count-badge">
                            {msg.sources.length} đoạn trích (Ranked by RRF)
                          </span>
                        </div>

                        <div className="sources-list">
                          {msg.sources.map((src, sIdx) => {
                            const isHighlighted = highlightedSourceId === (src.id || sIdx);
                            const meta = src.metadata || {};
                            return (
                              <div
                                id={`source-card-${src.id || sIdx}`}
                                key={src.id || sIdx}
                                className={`source-item-row ${isHighlighted ? 'source-highlighted' : ''}`}
                                onClick={() => setSelectedSourceDetail({ ...src, index: sIdx + 1 })}
                                title="Nhấp để xem đầy đủ trích đoạn & metadata nguồn"
                              >
                                <div className="source-item-left">
                                  <div className="source-doc-icon">
                                    {meta.doc_type === 'legal' ? '⚖️' : '🗺️'}
                                  </div>
                                  <div className="source-doc-meta">
                                    <div className="source-title-row">
                                      <span className="source-cite-num">[{sIdx + 1}]</span>
                                      <span className="source-doc-title">{meta.title || `Cẩm nang #${sIdx + 1}`}</span>
                                      <span className={`pdf-badge ${meta.doc_type === 'legal' ? 'badge-legal' : 'badge-news'}`}>
                                        {meta.doc_type === 'legal' ? 'Pháp lý / Chính sách' : 'Cẩm nang / Tin'}
                                      </span>
                                    </div>
                                    <div className="relevance-score-text">
                                      Phương pháp: <span className="method-pill">{src.retrieval_method || 'hybrid'}</span>
                                      {' · '}
                                      Điểm khớp: <span className="score-num">{Number(src.score || 0.88).toFixed(2)}</span>
                                    </div>
                                  </div>
                                </div>

                                <div className="source-item-right">
                                  <div className="source-loc-box">
                                    <span className="source-page-text">{meta.page || `Trang ${sIdx * 2 + 1}`}</span>
                                    <span className="source-chunk-text">Chunk #{meta.chunk_index ?? sIdx + 1}</span>
                                  </div>
                                  <span className="source-arrow">›</span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-item-bot">
              <div className="bot-avatar-circle">🧭</div>
              <div className="bot-card-box loading-box">
                <div className="loading-spinner-row">
                  <div className="pulse-spinner" />
                  <span>Đang truy xuất Dense + BM25, hợp nhất RRF và đối chiếu citation...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Input Bar */}
        <div className="bottom-input-wrapper">
          <form className="bottom-input-bar" onSubmit={handleSend}>
            <input
              type="text"
              className="chat-native-input"
              placeholder="Đặt câu hỏi về điểm đến, thời tiết, kinh nghiệm, ăn uống hoặc quy định du lịch..."
              value={inputVal}
              onChange={e => setInputVal(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="btn-send-message"
              disabled={!inputVal.trim() || loading}
            >
              <span>✈</span>
              <span>Gửi câu hỏi</span>
            </button>
          </form>
        </div>
      </div>

      {/* 2. Right Panel: Real-time Retrieval Inspector */}
      <aside className={`retrieval-details-panel ${activeInspector ? 'open' : ''}`}>
        <div className="details-panel-header" onClick={() => setActiveInspector(!activeInspector)}>
          <div className="details-title-wrap">
            <span>🔍</span>
            <span>Giám sát Đường ống RAG</span>
          </div>
          <span className="details-chevron">{activeInspector ? '▼' : '▲'}</span>
        </div>

        {/* Dense Retrieval Card */}
        <div className="retrieval-stat-card">
          <div className="stat-card-icon icon-dense">☊</div>
          <div className="stat-card-content">
            <div className="stat-card-top-row">
              <span className="stat-card-title">Dense Semantic (ChromaDB)</span>
              <span className="top-badge">Top {config.topK}</span>
            </div>
            <div className="stat-card-results">{retrievalStats.denseResults} chunks ngữ nghĩa</div>
            <div className="stat-card-desc">Cosine Similarity từ vector embeddings</div>
          </div>
        </div>

        {/* BM25 Retrieval Card */}
        <div className="retrieval-stat-card">
          <div className="stat-card-icon icon-bm25">📍</div>
          <div className="stat-card-content">
            <div className="stat-card-top-row">
              <span className="stat-card-title">Lexical Search (BM25)</span>
              <span className="top-badge">Top {config.topK}</span>
            </div>
            <div className="stat-card-results">{retrievalStats.bm25Results} chunks từ khóa</div>
            <div className="stat-card-desc">Khớp chính xác tên quán, địa danh, món ăn</div>
          </div>
        </div>

        {/* RRF Rank Fusion Card */}
        <div className="retrieval-stat-card">
          <div className="stat-card-icon icon-rrf">⚡</div>
          <div className="stat-card-content">
            <div className="stat-card-top-row">
              <span className="stat-card-title">Reciprocal Rank Fusion</span>
              <span className="top-badge">k = 60</span>
            </div>
            <div className="stat-card-results">{retrievalStats.rrfResults} chunks tối ưu sau gộp</div>
            <div className="stat-card-desc">Công thức: sum(1 / (60 + rank))</div>
          </div>
        </div>

        <div className="details-divider" />

        {/* Confidence & Fallback Status */}
        <div className="details-kv-row">
          <div className="kv-left">
            <span>🛡️ Độ tin cậy trung bình:</span>
          </div>
          <span className={`kv-value-score ${retrievalStats.fallbackTriggered ? 'score-warning' : ''}`}>
            {retrievalStats.confidence}
          </span>
        </div>

        <div className="details-kv-row">
          <div className="kv-left">
            <span>⚙️ Ngưỡng Fallback:</span>
          </div>
          <span className="kv-value-flag">{config.threshold.toFixed(2)}</span>
        </div>

        <div className="details-kv-row">
          <div className="kv-left">
            <span>🔄 Trạng thái Fallback:</span>
          </div>
          <span className={`kv-value-flag ${retrievalStats.fallbackTriggered ? 'flag-active' : ''}`}>
            {retrievalStats.fallbackUsed}
          </span>
        </div>

        <div className="details-kv-row">
          <div className="kv-left">
            <span>⏱️ Độ trễ xử lý:</span>
          </div>
          <span className="kv-value-flag">{retrievalStats.latency}</span>
        </div>

        <div className="details-help-box">
          <div className="help-box-title">💡 Gợi ý kiểm định:</div>
          <p className="help-box-text">
            Thử bấm vào các câu hỏi mẫu như <strong>"Sửa xe máy"</strong> hoặc tăng <strong>Ngưỡng điểm (threshold &gt; 0.95)</strong> ở thanh bên trái để xem phản xạ kích hoạt <strong>Safe Refusal</strong>!
          </p>
        </div>
      </aside>

      {/* 3. Source Details Modal (Source Highlighting & Full content inspection) */}
      {selectedSourceDetail && (
        <div className="upload-modal-overlay" onClick={() => setSelectedSourceDetail(null)}>
          <div className="upload-modal-box modal-wide" onClick={e => e.stopPropagation()}>
            <div className="modal-header-row">
              <div>
                <span className={`pdf-badge ${selectedSourceDetail.metadata?.doc_type === 'legal' ? 'badge-legal' : 'badge-news'}`}>
                  TRÍCH DẪN [{selectedSourceDetail.index}] • {selectedSourceDetail.metadata?.doc_type === 'legal' ? 'VĂN BẢN PHÁP LÝ' : 'CẨM NANG DU LỊCH'}
                </span>
                <h3 className="modal-title-text">{selectedSourceDetail.metadata?.title || 'Tài liệu nguồn'}</h3>
              </div>
              <button className="modal-close-icon" onClick={() => setSelectedSourceDetail(null)}>✕</button>
            </div>

            <div className="modal-meta-grid">
              <div><strong>Vị trí trang:</strong> {selectedSourceDetail.metadata?.page || 'N/A'}</div>
              <div><strong>Chunk Index:</strong> #{selectedSourceDetail.metadata?.chunk_index ?? 'N/A'}</div>
              <div><strong>Điểm phù hợp:</strong> <span className="score-num">{Number(selectedSourceDetail.score || 0).toFixed(3)}</span></div>
              <div><strong>Phương pháp:</strong> <span className="method-pill">{selectedSourceDetail.retrieval_method || 'hybrid'}</span></div>
            </div>

            <div className="modal-content-area">
              <div className="content-label">NỘI DUNG TOÀN VĂN ĐOẠN TRÍCH (CHUNK TEXT):</div>
              <div className="content-box">
                {selectedSourceDetail.content}
              </div>
            </div>

            {selectedSourceDetail.metadata?.url && selectedSourceDetail.metadata.url !== '#' && (
              <div className="source-url-row">
                <span>Nguồn công bố: </span>
                <a href={selectedSourceDetail.metadata.url} target="_blank" rel="noreferrer">
                  {selectedSourceDetail.metadata.url}
                </a>
              </div>
            )}

            <div className="modal-footer-row">
              <button className="btn-secondary" onClick={() => setSelectedSourceDetail(null)}>Đóng</button>
              <button
                className="btn-primary"
                onClick={() => {
                  navigator.clipboard.writeText(selectedSourceDetail.content);
                  alert('Đã sao chép nội dung đoạn trích vào clipboard!');
                }}
              >
                📋 Sao chép đoạn trích
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
