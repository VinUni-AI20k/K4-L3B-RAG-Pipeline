# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-26 |
| Framework and version | Ragas 0.4.3 |
| Evaluator model | `cx/gpt-5.6-luna` qua OpenAI-compatible 9Router |
| Generator model | `cx/gpt-5.6-luna` qua OpenAI-compatible 9Router |
| Embedding model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers) |
| Corpus version/commit | `984ad82` |
| Golden dataset size | 15 |
| `top_k` | 5 |
| Fallback threshold and calibration | Production `0.45`; A/B đặt `-1.0` để tắt PageIndex và cô lập biến retrieval |

## Configurations

- **Config A — dense-only:** cosine dense retrieval, lấy top 5, `use_reranking=False`.
- **Config B — hybrid + RRF:** dense top 10 và BM25 top 10, hợp nhất một lần bằng RRF (`k=60`), lấy top 5.

Hai config dùng cùng 15 câu hỏi, corpus, embedding, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy. Answer relevance dùng `strictness=1`; các metric còn lại dùng cấu hình mặc định của Ragas 0.4.3.

## Fallback calibration

Ngưỡng production `0.45` được chọn sau khi đo bằng đúng embedding/corpus hiện tại: 18 câu in-domain trong golden dataset có cosine tốt nhất từ `0.6327` đến `0.8627` (mean `0.7477`), còn ba câu thử ngoài domain về tên lửa, Python và cổ phiếu có cosine tốt nhất từ `0.2745` đến `0.3592`. Local fallback còn yêu cầu từ khóa thuộc miền du lịch/pháp lý; không có kết quả phù hợp thì Task 10 trả safe refusal.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | 0.8267 | 0.8667 | +0.0400 |
| Answer relevance | 0.6174 | 0.6894 | +0.0720 |
| Context recall | 0.7333 | 0.8667 | +0.1333 |
| Context precision | 0.6278 | 0.7856 | +0.1578 |
| **Average** | **0.7013** | **0.8021** | **+0.1008** |

## A/B comparison

- Cấu hình tốt hơn theo trung bình bốn metric: **B — hybrid + RRF** (`Delta B−A = +0.1008`).
- Evidence: thay đổi lớn nhất thuộc **Context precision** (`+0.1578`); số liệu chi tiết từng câu nằm trong `evaluation_details.json`.
- Trade-off về latency/cost: dense-only trung bình 4.49s/câu; hybrid + RRF trung bình 3.51s/câu. Hybrid chạy thêm BM25 và RRF; chi phí tiền không đo riêng vì 9Router dùng quota của provider.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Mức ký quỹ kinh doanh dịch vụ lữ hành đối với khách du lịch ra nước ngoài được quy định là bao nhiêu theo Nghị định 168/2017/NĐ-CP? | A | 0.4000 | 0.0000 | 0.0000 | 0.0000 | retrieval | Các chunk truy hồi không chứa đủ bằng chứng tham chiếu để trả lời. |
| 2 | Phố đi bộ Hồ Gươm ở Hà Nội mở cửa vào thời gian nào trong tuần? | A | 1.0000 | 0.0000 | 0.0000 | 0.0000 | retrieval | Các chunk truy hồi không chứa đủ bằng chứng tham chiếu để trả lời. |
| 3 | Chợ hoa Quảng Bá ở Hà Nội hoạt động đông vui nhất vào khoảng thời gian nào? | A | 1.0000 | 0.0000 | 0.0000 | 0.0000 | retrieval | Các chunk truy hồi không chứa đủ bằng chứng tham chiếu để trả lời. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | Yêu cầu generator trả lời trực tiếp, ngắn gọn trước phần giải thích. | Answer relevance là điểm yếu nhất. | Câu trả lời bám sát câu hỏi hơn. | Chạy lại answer relevance trên cùng output constraints. |
| 2 | Kiểm tra thủ công ba ca thấp nhất và bổ sung regression cases. | Ba ca trong bảng Worst performers có điểm trung bình thấp nhất. | Ngăn lỗi tương tự tái diễn. | Thêm test rồi chạy lại hai config. |
| 3 | Chạy evaluation lặp lại ít nhất ba lần khi có thêm quota. | Generator và LLM judge có tính bất định. | Ước lượng độ biến thiên của metric. | Báo cáo mean và standard deviation qua ba lần chạy. |

## Bonus experiments

- **UI citation/source highlighting (+2):** React UI nhận citation `[n]`, cuộn/highlight source card tương ứng và mở chi tiết chunk/metadata trong `frontend/src/tabs/TabChat.jsx` và `frontend/src/components/SourceCards.jsx`.
- Không tuyên bố HyDE/query expansion, reranker nâng cao hoặc conversation memory vì chưa có code kèm A/B/demo kiểm chứng.

## Reproducibility

```powershell
.\.venv\Scripts\python.exe -m group_project.evaluation.run_evaluation --skip-index --limit 15
.\.venv\Scripts\python.exe -m pytest -q
```

`evaluation_inputs.json` lưu input/output và latency; `evaluation_details.json` lưu bốn metric từng câu. Hai file không chứa API key.
