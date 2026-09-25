Người 1 — Dữ liệu và nội dung: Task 1–3
Mục tiêu: cung cấp dữ liệu sạch, có nguồn rõ ràng và bộ câu hỏi chuẩn để kiểm tra chatbot.
Công việc cụ thể

1. Thu thập tài liệu (Việt)
   - Đưa ít nhất 3 PDF/DOCX về quy chế, đề án hoặc hướng dẫn tuyển sinh vào data/landing/legal/.
   - Thu thập ít nhất 5 bài viết/trang hướng dẫn liên quan vào data/landing/news/.
   - Ưu tiên nguồn chính thức; kiểm tra năm áp dụng.
   - Lập danh mục gồm: tên file, tiêu đề, URL gốc, loại tài liệu, năm áp dụng và ngày thu thập.
2. Hoàn thiện Task 1–2
   - Task 1: xử lý việc thu thập tài liệu chính sách. Với PDF đã tải thủ công, bảo đảm chúng được các bước sau đọc được.
   - Task 2: thu thập bài viết, loại bỏ menu, quảng cáo và nội dung không liên quan.
   - Mỗi JSON bài viết phải có url, title, date_crawled, content_markdown.
3. Hoàn thiện Task 3 — chuyển đổi Markdown
   - Chuyển PDF/DOCX và nội dung bài viết sang Markdown.
   - Giữ tiêu đề, mục, điều khoản, danh sách và bảng biểu.
   - Kiểm tra lỗi mất dấu, thiếu trang, sai thứ tự đọc hoặc bảng bị vỡ.
   - Nếu PDF là bản scan, kiểm tra khả năng trích xuất và bổ sung OCR khi cần.
   - Giữ thông tin nguồn để các bước sau tạo citation.
4. Xây golden dataset
   - Soạn ít nhất 15 câu hỏi dựa trên nội dung thực sự có trong corpus.
   - Mỗi câu có: mã câu hỏi, câu hỏi, đáp án tham chiếu, nguồn, đoạn bằng chứng và năm áp dụng.
   - Có cả câu tra cứu trực tiếp và câu cần tổng hợp nhiều đoạn.
   - Chuẩn bị thêm các câu ngoài chủ đề hoặc thiếu thông tin để kiểm tra fallback.
     Bàn giao

- Bộ tài liệu gốc và Markdown đã kiểm tra.
- Danh mục nguồn.
- Golden dataset tối thiểu 15 câu.
- Danh sách lỗi dữ liệu hoặc nội dung còn chưa rõ.
  Tiêu chí hoàn thành: đọc được toàn bộ tài liệu, đủ số lượng, không mất nội dung quan trọng, truy ngược được về nguồn.
  Phối hợp: bàn giao sớm một tài liệu sạch cho Người 2; gửi golden dataset cho Người 4; hỗ trợ Người 3 kiểm tra câu trả lời.
  Người 2 — Lập chỉ mục và tìm kiếm: Task 4–7
  Mục tiêu: từ dữ liệu sạch, tìm ra những đoạn phù hợp với câu hỏi.
  Công việc cụ thể

1. Task 4 — Chunking (Đông)
   - Đọc dữ liệu do Người 1 bàn giao.
   - Chia đoạn theo tiêu đề, mục và nội dung.
   - Hạn chế tách điều kiện khỏi ngoại lệ hoặc bảng khỏi tiêu đề cột.
   - Tạo ID duy nhất, ổn định cho từng chunk.
   - Mỗi chunk có source, title, doc_type, url, chunk_index; giữ năm áp dụng nếu có.
2. Task 4 — Embedding và ChromaDB
   - Triển khai embed_texts() dùng chung cho tài liệu và câu hỏi.
   - Thống nhất embedding model và dimension.
   - Lưu vector, nội dung và metadata vào ChromaDB.
   - Bảo đảm chạy index lại không tạo dữ liệu trùng.
3. Task 5 — Dense search
   - Triển khai semantic_search(query, top_k=10).
   - Trả đúng schema SearchResult.
   - Giữ cosine score gốc để Người 3 sử dụng cho fallback.
   - Kiểm tra cách chuyển đổi nếu vector database trả distance thay vì similarity.
4. Task 6 — BM25
   - Triển khai lexical_search(query, top_k=10).
   - Dùng cùng bộ chunks và cùng ID với Dense.
   - Kiểm tra các câu có từ khóa, mã ngành, tên phương thức hoặc chứng chỉ nếu corpus có.
5. Task 7 — RRF
   - Triển khai rerank_rrf(ranked_lists, top_k=5, k=60).
   - Gộp theo ID, không trả trùng chunk.
   - Dùng công thức sum(1 / (k + rank)), thứ hạng bắt đầu từ 1.
   - Chỉ thực hiện việc gộp thứ hạng; Người 3 chịu trách nhiệm gọi trong pipeline.
     Bàn giao

- Pipeline chunk → embedding → index chạy được.
- Ba hàm Dense, BM25 và RRF đúng contract.
- Hướng dẫn tạo lại index.
- Một số câu hỏi mẫu kèm kết quả retrieval để kiểm tra.
  Tiêu chí hoàn thành: kết quả không trùng ID, không vượt top_k, giữ metadata nguồn; index lại không trùng dữ liệu.
  Phối hợp: thống nhất đầu vào với Người 1; bàn giao hàm tìm kiếm cho Người 3; hỗ trợ Người 4 chạy cấu hình Dense-only. (Duyên)
  Người 3 — Retrieval, fallback và generation: Task 8–10
  Mục tiêu: tạo câu trả lời có căn cứ, có citation và xử lý được trường hợp thiếu bằng chứng. Đồng thời chịu trách nhiệm tích hợp kỹ thuật.
  Công việc cụ thể

1. Task 8 — PageIndex fallback
   - Triển khai pageindex_search(query, top_k=5).
   - Trả SearchResult với retrieval_method="pageindex".
   - Xử lý lỗi hoặc timeout của provider.
   - Khi fallback lỗi, pipeline trả kết quả hybrid còn dùng được hoặc thông báo thiếu bằng chứng theo contract.
2. Task 9 — Ghép retrieval pipeline
   - Triển khai retrieve(...).
   - Gọi Dense và BM25 từ Người 2.
   - Gọi RRF đúng một lần.
   - Dùng cosine score gốc của Dense để quyết định fallback.
   - Hiệu chỉnh threshold bằng bộ câu hỏi trong và ngoài chủ đề.
   - Ghi lại threshold đã chọn và căn cứ lựa chọn.
3. Task 10 — Chuẩn bị context
   - Triển khai reorder_for_llm() và format_context().
   - Giữ ID khi sắp xếp lại các đoạn.
   - Đưa tiêu đề, nguồn và năm áp dụng vào context khi có.
   - Gắn nhãn nguồn để đối chiếu citation.
4. Task 10 — Sinh câu trả lời
   - Triển khai generate_with_citation(query, top_k=5).
   - Đọc cấu hình provider và API key từ môi trường.
   - Yêu cầu LLM trả lời theo bằng chứng được cung cấp.
   - Không tự thêm điều kiện, điểm số hoặc thời hạn.
   - Không đủ bằng chứng thì thông báo rõ; thiếu năm cần thiết thì yêu cầu làm rõ.
   - Trả đúng GenerationResult: answer, sources, retrieval_source.
5. Tích hợp
   - Ghép module của các thành viên.
   - Giải quyết lỗi interface và cấu hình.
   - Kiểm tra luồng dữ liệu → retrieval → generation → UI.
   - Chạy các test của repo trước khi chốt bản nộp.
     Bàn giao

- Task 8–10 hoạt động.
- Hàm generate_with_citation() để Người 4 gọi.
- Cấu hình mẫu không chứa key thật.
- Kết quả kiểm tra fallback, citation và xử lý lỗi.
  Tiêu chí hoàn thành: citation khớp sources, không dùng điểm RRF làm ngưỡng fallback, lỗi provider không làm UI sập.
  Phối hợp: gửi sớm một GenerationResult giả lập cho Người 4; phối hợp Người 2 kiểm tra score; nhờ Người 1 xác minh nội dung trả lời.
  Người 4 — Giao diện, đánh giá và báo cáo (Na)
  Mục tiêu: tạo chatbot dùng được và chứng minh chất lượng bằng kết quả đánh giá.
  Công việc cụ thể

1. Giao diện Streamlit — app.py
   - Tạo ô nhập câu hỏi và hiển thị hội thoại.
   - Gọi generate_with_citation() của Người 3.
   - Hiển thị câu trả lời, nguồn, retrieval method và score.
   - Cho người dùng xem đoạn nội dung được trích dẫn.
   - Hiển thị trạng thái đang xử lý và thông báo lỗi dễ hiểu.
   - Nêu rõ năm tuyển sinh/phạm vi tài liệu chatbot hỗ trợ.
2. Chuẩn bị chương trình đánh giá
   - Nhận golden dataset từ Người 1.
   - Chạy từng câu hỏi qua pipeline.
   - Lưu câu trả lời, chunks truy xuất, nguồn và cấu hình chạy.
   - Phối hợp Người 1 kiểm tra chất lượng đáp án tham chiếu.
3. Đo bốn metric
   - Faithfulness.
   - Answer relevance.
   - Context recall.
   - Context precision.
4. So sánh A/B
   - A: Dense-only.
   - B: Dense + BM25 + RRF.
   - Giữ nguyên corpus, câu hỏi, LLM, prompt, top_k và chính sách fallback.
   - Không dùng toàn bộ bộ đánh giá cuối để chỉnh threshold.
   - Báo cáo kết quả thực tế và giải thích những câu cải thiện hoặc kém đi.
5. Báo cáo và demo
   - Hoàn thiện group_project/evaluation/RESULT.md.
   - Ghi cấu hình, kết quả metric, bảng A/B, lỗi tiêu biểu và giới hạn.
   - Cập nhật README với cách cài đặt, index và chạy chatbot.
   - Chuẩn bị demo: câu có đáp án, câu cần tổng hợp, câu thiếu bằng chứng.
     Bàn giao

- app.py chạy được.
- Chương trình và dữ liệu kết quả đánh giá.
- Bảng A/B và RESULT.md hoàn chỉnh.
- Hướng dẫn chạy và kịch bản demo.
  Tiêu chí hoàn thành: người khác chạy được theo README; các con số trong báo cáo có kết quả chạy làm bằng chứng.
  Phối hợp: làm UI với dữ liệu giả lập trước; Người 1 kiểm tra nội dung; Người 2–3 cung cấp hai chế độ retrieval.
  Quy trình bàn giao chung
  Mốc Việc cần hoàn thành Người chịu trách nhiệm chính

1. Chốt đầu vào Năm tuyển sinh, schema, embedding model, provider LLM, phạm vi file mỗi người sửa Cả nhóm; Người 3 tổng hợp
2. Có dữ liệu mẫu Một tài liệu sạch kèm metadata nguồn Người 1
3. Chạy một câu xuyên suốt Index → tìm kiếm → trả lời → hiển thị citation Người 2, 3, 4
4. Hoàn thiện dữ liệu và chức năng Đủ tài liệu, hybrid, fallback, golden dataset, UI Cả nhóm
5. Chốt cấu hình để đánh giá Cố định corpus, prompt và các cấu hình A/B Người 3 và 4
6. Kiểm tra và nộp Test, kết quả A/B, báo cáo, README, demo Người 3 tích hợp; mỗi người kiểm tra phần mình

Không chờ người trước làm xong toàn bộ mới bắt đầu. Người 1 giao dữ liệu mẫu sớm; Người 2–3 triển khai theo contract; Người 4 dùng kết quả giả lập để làm giao diện và khung đánh giá.
Quy tắc làm việc nhóm

- Mỗi người làm trên một branch riêng; Người 3 quản lý tích hợp.
- Hạn chế cùng sửa một file. Thay đổi schema phải thông báo cả nhóm.
- Khi bàn giao, gửi đủ: commit, cách chạy, đầu vào/đầu ra và lỗi còn tồn tại.
- Mỗi thành viên tự kiểm tra module của mình và viết báo cáo cá nhân.
- Không commit .env hoặc API key.
- Hoàn thành các yêu cầu chính trước khi làm bonus như memory, query expansion hoặc deploy.
