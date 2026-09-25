# Individual contribution report — Bùi Quốc Việt

---

## Thông tin

- **Họ và tên:** Bùi Quốc Việt
- **Mã học viên:** 2A202602884
- **Nhóm:** Nhóm K4-L3B-nhomtoi (RAG Pipeline tuyển sinh NEU 2026)
- **Repository/branch:** `vietbui000/K4-L3B-RAG-Pipeline` (branch: `buiquocviet`)

---

## Phần việc đã thực hiện

| Module/deliverable                        | Việc tôi trực tiếp làm                                                                                                                                  | File/commit/PR                                                                                                                  | Trạng thái |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| **Task 1 — Legal Docs Collection**        | Thu thập và lập danh mục 3 tệp PDF tuyển sinh NEU 2026 (Chính quy 11 trang, Liên thông CĐ 7 trang, Liên thông ĐH 4 trang), tạo manifest kiểm kê SHA-256 | `src/task1_collect_legal_docs.py`, `data/landing/legal/`, `data/legal_inventory.json`                                           | Done       |
| **Task 2 — Web News Crawling**            | Crawl và làm sạch 5 bài viết hướng dẫn tuyển sinh từ `fit.neu.edu.vn`, loại bỏ menu, quảng cáo, trích xuất Markdown chuẩn                               | `src/task2_crawl_news.py`, `data/landing/news/`, `data/landing/raw_html/`                                                       | Done       |
| **Task 3 — Markdown Conversion & OCR**    | Chuyển đổi PDF/DOCX và bài viết web sang định dạng Markdown chuẩn hóa, triển khai Tesseract OCR cho PDF scan, xử lý bảng biểu chỉ tiêu                  | `src/task3_convert_markdown.py`, `data/standardized/legal/`, `data/standardized/news/`, `data/ocr/`                             | Done       |
| **Golden Dataset & Fallback Calibration** | Xây dựng bộ 20 câu hỏi đánh giá (Golden Dataset) có bằng chứng trích dẫn thực tế và 6 kịch bản kiểm thử hiệu chỉnh Fallback                             | `src/build_golden_dataset.py`, `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/fallback_dataset.json` | Done       |
| **Data Handoff Documentation**            | Viết hướng dẫn bàn giao chi tiết cho Người 2 (Chunking), Người 3 (Pipeline) và Người 4 (Evaluation)                                                     | `docs/DATA_HANDOFF.md`                                                                                                          | Done       |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng Tesseract OCR kết hợp bộ đệm (cache) theo mã băm SHA-256 của file PDF và rà soát thủ công các trang chứa bảng biểu chỉ tiêu quan trọng (trang 1, 4–7 của Đề án 2026).  
   **Lý do/evidence:** Cả 3 file PDF tuyển sinh do nhà trường công bố đều là bản scan. Nếu dùng bộ trích xuất text thông thường sẽ bị mất chữ hoặc làm vỡ cấu trúc bảng chỉ tiêu (tổng 8.780 sinh viên). Việc cache SHA-256 giúp tiết kiệm thời gian OCR khi chạy lại pipeline.  
   **Trade-off:** Đòi hỏi bước rà soát thủ công đối chiếu ảnh PDF cho các trang quan trọng, nhưng đổi lại đảm bảo 100% độ chính xác của bảng ngành, tổ hợp xét tuyển và chỉ tiêu.

2. **Quyết định:** Thiết kế chuẩn hóa Schema JSON Document và Metadata nhất quán (`admission_year`, `audience`, `source`, `url`, `doc_type`).  
   **Lý do/evidence:** Giúp module Chunking (Người 2) và Generation (Người 3) phân biệt chính xác đối tượng áp dụng (Đại học chính quy vs. Liên thông) và trích dẫn URL/nguồn chính xác theo yêu cầu hợp đồng module (`docs/MODULE_CONTRACTS.md`).  
   **Trade-off:** Làm tăng nhẹ dung lượng file metadata, nhưng giúp ngăn chặn triệt để việc chatbot lấy thông tin hệ liên thông trả lời cho thí sinh THPT.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  `pytest tests/test_data_pipeline.py tests/test_acceptance.py -k "not evaluation_report"`
- **Kết quả trước/sau nếu có:**
  - _Trước:_ Dữ liệu thô gồm PDF scan không thể đọc text và HTML bài viết chứa nhiều thẻ rác menu/footer.
  - _Sau:_ 8 file Markdown và 8 file JSON Document chuẩn hóa đạt **100% Passed (14/14 tests)**; 20 câu hỏi golden dataset có đầy đủ bằng chứng đối chiếu.
- **Lỗi đã phát hiện và cách xử lý:**
  - _Lỗi:_ Thứ tự dòng chữ trong PDF scan bị đảo lộn giữa 2 cột làm vỡ nghĩa của câu.
  - _Cách xử lý:_ Viết thuật toán sắp xếp bbox (tọa độ chữ) theo chiều dọc cột trước khi ghép dòng và thực hiện rà soát trang 4–7.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:**  
  Hai file PDF liên thông đại học và cao đẳng mới chỉ chạy OCR tự động, chưa rà soát đối chiếu từng ô bảng thủ công 100% như PDF chính quy.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:**  
  Phát triển công cụ UI tự động hỗ trợ rà soát và sửa lỗi OCR cho toàn bộ 22 trang scan của cả 3 file PDF.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Bùi Quốc Việt
