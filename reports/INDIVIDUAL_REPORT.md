# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên:Tô Anh Đức
- Mã học viên:2A202602639
- Nhóm:K4-L3B
- Repository/branch:K4-L3B-RAG-Pipeline / tainangtre

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4-9 / indexing và retrieval | Hoàn thiện chunking, ChromaDB, semantic search, BM25, RRF, PageIndex fallback và calibration threshold | `src/task4_chunking_indexing.py`, `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Golden dataset và UI | Tạo 15 golden cases; chuyển UI sang real retrieval; thêm live pipeline, embedding comparison và golden analysis | `group_project/evaluation/golden_dataset.json`, `app.py`, `src/embedding_comparison.py` | Done |
| Kiểm thử pipeline | Kiểm tra ChromaDB 329 chunks, real query, contract tests và Streamlit AppTest | `tests/test_contracts.py`, `tests/test_acceptance.py` | Partial |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Dùng ChromaDB persistent với collection `rag_documents`, embedding MiniLM và ID chunk ổn định.
   **Lý do/evidence:** Chạy index tạo 329 chunks; contract tests xác nhận metadata, ID và search result.
   **Trade-off:** Model local dễ chạy lại nhưng cần cache model khi chạy lần đầu.

2. **Quyết định:** Dùng hybrid retrieval với BM25 + RRF và threshold dense score 0.6 cho fallback.
   **Lý do/evidence:** Hybrid tăng context recall từ 0.600 lên 0.733 trên 15 golden cases; dense in-domain cao hơn rõ rệt so với query ngoài domain.
   **Trade-off:** Phải chạy thêm BM25/RRF; BGE-M3 chưa tải hoàn chỉnh nên UI dùng TF-IDF fallback để so sánh.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest -q`, contract tests, query semantic/BM25/hybrid thật, Streamlit AppTest và audit 15 golden cases.
- Kết quả trước/sau nếu có: `19 passed, 1 failed`; lỗi còn lại là evaluation report trước khi tạo file đúng path. Hybrid đạt context recall `0.733`, precision `0.356`.
- Lỗi đã phát hiện và cách xử lý: threshold `0.3` quá thấp nên điều chỉnh mặc định thành `0.6`; BGE-M3 chưa đủ cache nên UI báo rõ và dùng TF-IDF fallback.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Faithfulness và answer relevance chưa được đo bằng evaluator LLM; full acceptance còn phụ thuộc report evaluation và BGE-M3 chưa sẵn sàng.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: chạy evaluator cho 4 metrics và tối ưu chunking theo section/table cho tài liệu tuyển sinh dài.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày:25/9/2026
- Tên thành viên:Tô Anh Đức
