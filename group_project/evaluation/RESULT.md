# RAG evaluation results — Du lịch Ninh Bình

## Run information

- Time (UTC): 2026-09-25T10:33:24.476581+00:00
- Questions: 15; top_k: 5
- Corpus: 3 tài liệu legal + 5 bài news; 15 câu kiểm tra lấy từ 5 bài news.
- Phép đo: retrieval theo đúng file nguồn được ghi trong expected_context.
- Dense-only và hybrid dùng cùng câu hỏi, top_k, corpus, embedding; hybrid thêm BM25 và RRF.

## Overall scores

| Metric | Dense-only | Hybrid + RRF | Delta (hybrid - dense) |
|---|---:|---:|---:|
| Hit@5 | 1.0000 | 1.0000 | +0.0000 |
| MRR@5 | 0.9333 | 0.9222 | -0.0111 |
| Avg latency (s) | 1.8450 | 0.1480 | -1.6970 |

## A/B comparison

Hit@5 = tỷ lệ câu có ít nhất một chunk từ đúng file nguồn trong top 5. MRR@5 = trung bình nghịch đảo vị trí đầu tiên của đúng file nguồn.
Điểm cao hơn của Hit@5 và MRR@5 là tốt hơn; thời gian thấp hơn là tốt hơn.
Kết quả từng câu và danh sách ID được lưu ở ab_results.json.
Đây là số đo retrieval theo file nguồn, không phải điểm Ragas hoặc đánh giá faithfulness của câu trả lời.

## Worst performers

- Theo bài viết Thưởng ngoạn cảnh sắc thiên nhiên tuyệt đẹp của Ninh Bình, Bích Động có nghĩa là gì? — nguồn chuẩn news/article_05.md; dense rank 1, hybrid rank 3.
- Ba hang động ở Tam Cốc được bài viết nêu tên là gì? — nguồn chuẩn news/article_01.md; dense rank 2, hybrid rank 2.
- Lúa ở Tam Cốc bắt đầu chín rộ vào tháng nào? — nguồn chuẩn news/article_01.md; dense rank 1, hybrid rank 1.

## Recommendations

1. Xem từng câu bị miss trong ab_results.json, sửa nội dung corpus hoặc chunking dựa trên bằng chứng trước khi tăng top_k.
2. Kiểm tra citation đến đúng chunk; test contract và kết quả theo file nguồn không đủ chứng minh mỗi lời đáp đều có dẫn chứng đúng.
3. Kiểm chứng nguồn gốc ba PDF; bổ sung câu hỏi pháp lý có reference được đối chiếu trước khi đánh giá toàn corpus.
4. Nếu bài lab yêu cầu Ragas, chạy thêm phép đo Ragas thật; không gắn nhãn Ragas cho các số đo trong báo cáo này.
