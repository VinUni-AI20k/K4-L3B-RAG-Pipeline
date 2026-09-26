# Individual Contribution Report

## Thông tin

- Họ và tên: Ngô Thế Khanh
- Mã học viên: 2A20262503
- Nhóm: K4-L3B-RAG-Pipeline
- Vai trò: Member & Retrieval Engineer

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4: Chunking & Indexing | Cài đặt logic chunking văn bản với overlap, tích hợp embedding model `all-MiniLM-L6-v2` và lưu trữ vào ChromaDB | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| Task 5: Semantic Search | Viết hàm dense search truy vấn ChromaDB trả về `SearchResult` theo đúng contract | `src/task5_semantic_search.py` | Done |
| Task 6: Lexical Search | Xây dựng BM25Okapi search trên tập chunks để tối ưu truy vấn từ khóa | `src/task6_lexical_search.py` | Done |
| Task 7: Reranking & RRF | Cài đặt thuật toán Reciprocal Rank Fusion (RRF) kết hợp danh sách xếp hạng từ Dense và BM25 | `src/task7_reranking.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng hằng số $k=60$ trong công thức RRF: $Score = \sum \frac{1}{k + rank}$.  
   **Lý do/evidence:** Hằng số $k=60$ là tiêu chuẩn được kiểm chứng trong nhiều nghiên cứu về thông tin truy hồi, tránh việc một kết quả top 1 ở một kênh lấn át hoàn toàn kênh còn lại.  
   **Trade-off:** Điểm số RRF không nằm trên thang đo tuyệt đối [0, 1] nên không thể so trực tiếp với cosine threshold (phải dùng cosine score gốc cho fallback).

2. **Quyết định:** Chạy semantic search và lexical search lấy `top_k * 2` trước khi đưa vào RRF.  
   **Lý do/evidence:** Mở rộng không gian ứng viên giúp thuật toán fusion có đủ chunk giao thoa để tìm ra thứ hạng tối ưu nhất.  
   **Trade-off:** Tăng nhẹ thời gian tính toán xếp hạng nhưng đảm bảo không bỏ sót văn bản liên quan.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: Thử nghiệm truy vấn cụm từ chuyên biệt như "Điều 11 quyền của khách du lịch" và "hang Múa".
- Kết quả trước/sau: Dense-only thường bị trôi thứ hạng của Điều 11 xuống top 4; khi kết hợp BM25 + RRF, chunk chứa Điều 11 vươn lên vị trí top 1.
- Lỗi đã phát hiện và cách xử lý: Lỗi không đồng nhất schema giữa dense và bm25 results; đã chuẩn hóa chặt chẽ theo dataclass `SearchResult`.

## Điều còn hạn chế

- Một hạn chế cụ thể: Chưa tích hợp Cross-Encoder Reranker học sâu (như BGE-Reranker-large) do giới hạn tài nguyên máy tính cá nhân.
- Hướng cải tiến: Triển khai Jina Reranker API hoặc self-host một model cross-encoder gọn nhẹ để tăng độ chính xác top 3.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Ngô Thế Khanh
