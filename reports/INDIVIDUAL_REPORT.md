# Báo cáo đóng góp cá nhân — Người 4

## Thông tin

- Họ và tên: Na
- Mã học viên: ................................
- Nhóm: K4-L3B-RAG-Pipeline
- Vai trò: Người 4 — Giao diện, đánh giá và báo cáo
- Repository/branch: `K4-L3B-RAG-Pipeline`

## Phần việc đã thực hiện

| Module/deliverable | Việc trực tiếp thực hiện | File/bằng chứng | Trạng thái |
|---|---|---|---|
| Streamlit UI | Xây dựng giao diện chat, nhập câu hỏi, hiển thị hội thoại và trạng thái xử lý | `app.py` | Done |
| Generation integration | Kết nối `generate_with_citation(query, top_k)` vào UI | `app.py` | Done |
| Citation display | Hiển thị title, source, URL, retrieval method, score và nội dung chunk | `app.py` | Done |
| Error handling | Hiển thị lỗi dễ hiểu khi thiếu index, API key hoặc provider lỗi | `app.py` | Done |
| Scope communication | Nêu rõ phạm vi tài liệu tuyển sinh NEU 2026 trên sidebar và header | `app.py` | Done |
| Evaluation runner | Chạy golden dataset theo hai cấu hình Dense-only và Hybrid | `src/task11_evaluation.py` | Done |
| Metric calculation | Lưu faithfulness, answer relevance, context recall và context precision | `src/task11_evaluation.py` | Done |
| Raw evaluation evidence | Lưu câu hỏi, đáp án tham chiếu, chunks, metadata, score và cấu hình chạy | `group_project/evaluation/runs/` | Done |
| Group report | Hoàn thiện cấu hình, cách chạy, A/B, giới hạn và demo | `reports/RESULT.md` | Done |
| Evaluation report | Bổ sung Overall scores, A/B comparison, Worst performers và Recommendations | `group_project/evaluation/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

### 1. Giữ UI theo generation contract

UI gọi đúng `generate_with_citation(query, top_k)` và dùng trực tiếp ba trường `answer`, `sources`, `retrieval_source`. Cách này giúp giao diện không tự suy diễn nguồn và luôn hiển thị citation từ pipeline.

**Trade-off:** UI phụ thuộc vào index, retrieval pipeline và provider LLM đã được cấu hình; đổi lại schema giữa các module nhất quán và dễ kiểm thử.

### 2. Tách evaluation khỏi giao diện

Phần đánh giá được triển khai riêng trong `src/task11_evaluation.py`. Nhánh A dùng `use_reranking=False`, nhánh B dùng `use_reranking=True`; cả hai giữ nguyên corpus, câu hỏi, `top_k=5` và threshold `0.35`.

**Trade-off:** Cần chạy thêm một command riêng để tạo kết quả JSON, nhưng kết quả có thể tái lập, kiểm tra và không phụ thuộc thao tác trên UI.

## Kiểm thử và kết quả

Đã thực hiện:

```powershell
python -m py_compile app.py
python -m compileall -q app.py src
pytest -q tests/test_acceptance.py
```

Kết quả acceptance test hiện tại: **5 passed**.

Golden dataset đã được kiểm tra có **20 câu hỏi**. Evaluation runner hỗ trợ chạy:

```powershell
python -m src.task4_chunking_indexing
python -m src.task11_evaluation --mode both
```

Kết quả sau khi chạy được lưu tại:

- `group_project/evaluation/runs/dense_run.json`
- `group_project/evaluation/runs/hybrid_run.json`

## Metric và cách diễn giải

Runner lưu bốn metric cho từng câu hỏi:

- **Faithfulness:** mức độ đáp án tham chiếu có bằng chứng trong context truy xuất.
- **Answer relevance:** mức độ context liên quan đến đáp án kỳ vọng.
- **Context recall:** mức độ context bao phủ bằng chứng tham chiếu.
- **Context precision:** mức độ context truy xuất tập trung vào bằng chứng cần thiết.

Phiên bản hiện tại dùng token-overlap proxy xác định để kiểm tra hồi quy offline. Proxy này không được coi là điểm RAGAS chính thức; muốn đánh giá semantic cần chạy evaluator RAGAS với model và cấu hình cố định.

## Lỗi đã phát hiện và cách xử lý

| Lỗi/tình huống | Cách xử lý |
|---|---|
| Thiếu API key hoặc LLM provider lỗi | UI hiển thị thông báo thân thiện và không làm app crash |
| Chưa có ChromaDB index | Ghi rõ cần chạy indexing trước khi đánh giá |
| Câu hỏi ngoài phạm vi hoặc thiếu bằng chứng | Generation pipeline dùng safe refusal |
| Retrieval không tìm thấy kết quả | Hiển thị câu trả lời không thể xác minh từ nguồn hiện có |
| Kết quả A/B chưa chạy | Không điền số liệu giả vào report; hướng dẫn lệnh tái lập |

## Hạn chế

1. Chưa thể công bố điểm RAGAS chính thức nếu chưa cố định evaluator model và API key.
2. Token-overlap proxy chưa đánh giá đầy đủ tính đúng nghĩa của câu trả lời tiếng Việt.
3. Chất lượng UI phụ thuộc dữ liệu và metadata được cung cấp từ retrieval/generation.
4. Các câu hỏi khác năm tuyển sinh cần được tách phạm vi rõ ràng trước khi trả lời.

## Kế hoạch cải thiện

- Chạy evaluation sau khi index đầy đủ và lưu hai file JSON kết quả vào `group_project/evaluation/runs/`.
- Bổ sung RAGAS semantic evaluation với model evaluator cố định.
- Rà soát ba nhóm câu hỏi: có đáp án trực tiếp, cần tổng hợp nhiều nguồn và thiếu bằng chứng.
- Dùng kết quả worst performers để điều chỉnh chunking hoặc metadata, không chỉnh threshold trên toàn bộ evaluation set.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh các phần việc đã thực hiện trong project và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Na
