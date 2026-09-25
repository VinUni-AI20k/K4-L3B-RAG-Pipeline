# Individual contribution report

---

## Thông tin

- Họ và tên: Phan Hoàng Vũ
- Mã học viên: 2A202602450
- Nhóm: Soul
- Repository/branch: `main` (Vai trò: Machine Learning Engineer)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 — Chunking & Indexing | Code hàm load markdown, cắt 472 chunk (recursive 500/50), gọi Gemini embedding và upsert vào ChromaDB có kèm retry rate limit | `src/task4_chunking_indexing.py` (commit `b15a48d`) | Done |
| Task 5 — Semantic Search | Code hàm search vector trên ChromaDB, đổi cosine distance sang similarity score và fix lỗi thiếu field url do Chroma trả về | `src/task5_semantic_search.py` (commit `f0ea805`) | Done |
| Task 6 — Lexical Search (BM25) | Cài đặt BM25Okapi, viết thêm class SmoothBM25Okapi xử lý corpus nhỏ để pass test và cache lại index tránh build lại nhiều lần | `src/task6_lexical_search.py` (commit `6a3e38f`) | Done |
| Task 7 — RRF Reranking | Cài đặt thuật toán Reciprocal Rank Fusion kết hợp thứ hạng từ Dense và BM25 theo công thức chuẩn $1/(60+rank)$ | `src/task7_reranking.py` (commit `382459f`) | Done |
| Testing & Debug | Chạy pass toàn bộ test contract cho cả 4 task và kiểm tra thực tế trên tập data 472 chunk của trường | `tests/test_contracts.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng Gemini embedding (`gemini-embedding-001`) chia batch 50 kèm cơ chế bắt lỗi 429 để tự động ngủ (sleep) rồi retry lại thay vì gọi ồ ạt.  
   **Lý do/evidence:** Lúc đầu tính dùng OpenAI nhưng kiểm tra key thì thấy báo hết quota (credit exhausted). Chuyển qua Gemini thì chạy 472 chunk liên tục lại bị dính rate limit 429 của gói Free tier. Nếu không viết đoạn retry và giãn cách 1s giữa các batch thì script chạy giữa chừng sẽ văng lỗi và ChromaDB bị thiếu dữ liệu.  
   **Trade-off:** Quá trình index ban đầu chạy mất tầm hơn 1 phút do phải đợi retry vài batch, nhưng bù lại thì index chạy hết 100% không bị chết giữa chừng.

2. **Quyết định:** Kế thừa `BM25Okapi` tạo ra `SmoothBM25Okapi` để ép gán giá trị sàn (floor) cho IDF khi giá trị này bé hơn hoặc bằng 0.  
   **Lý do/evidence:** Khi chạy test case của môn trong file `test_contracts.py`, do test chỉ truyền vào có 2 document mẫu, công thức IDF nguyên bản của BM25Okapi bị chia ra số âm hoặc bằng 0 khiến score của tất cả document đều bằng 0 và bị hàm search lọc sạch làm rỗng kết quả (bị văng lỗi `IndexError`). Đặt sàn `eps = 0.25` giúp hàm pass được bài test của thầy mà vẫn giữ được độ chính xác khi tìm trên tập văn bản lớn.  
   **Trade-off:** Phải can thiệp vào hàm `_calc_idf` của thư viện ngoài một chút thay vì gọi thẳng hàm mặc định.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - Chạy unit test hợp đồng:
    ```bash
    pytest tests/test_contracts.py -k "chunk or semantic or lexical or rrf" -v
    ```
  - Chạy thử query thực tế trên dữ liệu trường:
    ```python
    "học bổng khuyến khích học tập"
    "Quy định điều kiện xét học bổng khuyến khích học tập ĐHQGHN"
    ```
- Kết quả trước/sau nếu có:
  - **Trước:** Các file task 4, 5, 6, 7 đều chưa code, chạy test toàn bị `NotImplementedError` và ChromaDB chưa có dữ liệu nào (count = 0).
  - **Sau:** 
    + 4/4 bài test contract của Task 4, 5, 6, 7 đều **PASSED 100%**.
    + ChromaDB nạp đủ 472 chunks (kiểm tra `col.count()` ra đúng 472).
    + Tìm kiếm thử ra đúng văn bản mong muốn: Semantic search đạt score ~0.85, BM25 bắt đúng các từ khóa chính xác, và RRF kết hợp đưa chunk số 50 và 16 của quy định học bổng lên đầu bảng với điểm cao nhất (`0.03252`).
- Lỗi đã phát hiện và cách xử lý:
  - Lúc đầu chạy cài thư viện thì bị văng lỗi cú pháp TOML do file `pyproject.toml` dòng 29 bị dính chữ `K4-L3B-RAG-Pipeline` ở đuôi, tôi đã mở file sửa lại cho chuẩn.
  - Khi lấy dữ liệu từ ChromaDB ra để validate contract ở Task 5, ChromaDB tự ý xóa mất key `"url"` nếu giá trị của nó là `None`, làm hàm `validate_document` báo lỗi `metadata.url must be a string or None`. Tôi đã xử lý bằng cách check nếu thiếu key `"url"` trong metadata trả về thì tự động bù lại `"url": None`.
  - Trên máy Windows lúc in kết quả ra terminal hay bị lỗi encoding `cp1252 / charmap` do text tiếng Việt có dấu, tôi đã thêm đoạn `sys.stdout.reconfigure(encoding="utf-8")` vào các khối chạy thử nghiệm để console in mượt mà.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Phần tách từ của BM25 hiện tại mới dùng hàm `.split()` theo dấu cách đơn giản, đối với tiếng Việt có nhiều từ ghép 2 hoặc 3 tiếng thì cách tách này đôi khi chưa phản ánh hết được ngữ nghĩa của từ khóa.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung thư viện tách từ tiếng Việt (như `pyvi` hoặc `underthesea`) vào trước khi đưa vào BM25, và thử cài thêm một model cross-encoder reranker (như BGE-Reranker) để làm thí nghiệm so sánh đối đầu với thuật toán RRF xem cái nào tìm bài chuẩn hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phan Hoàng Vũ
