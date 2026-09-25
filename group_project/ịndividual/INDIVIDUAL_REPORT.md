# Báo cáo cá nhân

**Họ và tên:** Lê Văn Sang  
**Mã học viên:** 2A202602391  
**Nhóm:** K4-L3B-RAG-Pipeline  
**Vai trò:** Team Lead & Data Collection  

## 1. Công việc đã thực hiện
- Thu thập và làm sạch dữ liệu văn bản pháp luật: Luật Du lịch 2017 (Luật số 09/2017/QH14), Quyết định 718/QĐ-BVHTTDL ban hành Bộ quy tắc ứng xử văn minh du lịch, Kế hoạch 75/KH-UBND phát triển du lịch biển Ninh Bình 2026-2030.
- Crawl và chuẩn hóa dữ liệu 10 bài viết về danh lam thắng cảnh và ẩm thực Ninh Bình (Tam Cốc - Bích Động, Tràng An, Vườn quốc gia Cúc Phương, Đầm Vân Long, Hang Múa, Nem chua Yên Mạc, Cơm cháy...).
- Chuẩn hóa toàn bộ dữ liệu landing sang Markdown sạch có cấu trúc header metadata đồng bộ.
- Phối hợp cùng các thành viên xây dựng và kiểm thử pipeline RAG hoàn chỉnh (convert → chunk → index → dense + BM25 → RRF → fallback → generation có citation).

## 2. Kỹ năng đạt được
- Hiểu sâu và áp dụng thành thạo kỹ thuật chunking văn bản pháp luật và bài viết chuyên đề có overlap.
- Nắm vững kiến thức và kỹ thuật phối hợp Hybrid Search (Dense Vector + Lexical BM25) bằng thuật toán Reciprocal Rank Fusion (RRF).
- Thiết lập quy trình đánh giá chất lượng RAG qua 4 chỉ số cốt lõi (Faithfulness, Relevance, Context Recall, Context Precision).

## 3. Khó khăn và giải pháp
- **Khó khăn:** Quá trình trích xuất văn bản từ các file PDF scan ảnh gặp trở ngại do thiếu thư viện OCR hoặc lỗi font chữ tiếng Việt.
- **Giải pháp:** Bổ sung văn bản chuẩn hóa đầy đủ theo đúng cấu trúc chương điều khoản quy phạm pháp luật và lưu trữ dưới dạng Markdown UTF-8 kèm metadata chuẩn.

## 4. Đề xuất cải tiến
- Tích hợp thêm Knowledge Graph để giải quyết các câu hỏi yêu cầu suy luận phức tạp giữa các quy định pháp luật và danh mục dịch vụ địa phương.
- Phát triển thêm tính năng multi-turn conversation memory cho chatbot hỗ trợ hỏi tiếp nối.
