# Task 4 — Chia đoạn, embedding và ChromaDB

Task 4 đọc 8 Markdown từ Task 3. Metadata YAML ở đầu file được tách khỏi nội
dung embedding; giữ tiêu đề, file nguồn, URL, ngôn ngữ và thông tin OCR để trích dẫn.

**Trạng thái hiện tại:** đã tạo embedding và index thành công 498 đoạn từ 8
Markdown vào ChromaDB. `reports/task4_index.json` có `status: indexed`.
Đã kiểm tra collection thật có 498 bản ghi, cosine distance và truy vấn mẫu
trả về các đoạn của Luật Du lịch cùng Nghị định 168/2017/NĐ-CP.

## Chia đoạn

- Chiến lược `separator_window_per_page`: cửa sổ tối đa 500 ký tự, gối nhau
  50 ký tự trước khi bỏ khoảng trắng ở hai đầu. Ưu tiên kết thúc ở đoạn văn,
  dòng, câu rồi khoảng trắng; từ dài vẫn được chia để không vượt giới hạn.
- Chọn 500/50 để cân bằng lượng ngữ cảnh, số đoạn và chi phí CPU trên bộ dữ liệu
  nhỏ. Đây là cấu hình ban đầu, chưa tối ưu bằng golden dataset.
- PDF được chia riêng từng trang. Metadata `page` luôn chỉ đúng trang gốc;
  không có đoạn nối từ hai trang. Task 5 có thể tìm nhiều đoạn để ghép ngữ cảnh.
- ID cố định: `legal/ten_file.md::chunk-0`, `news/article_01.md::chunk-0`, ...
- Corpus gồm 498 đoạn với dữ liệu hiện tại; lưu `data/index/chunks.jsonl` để
  Task 6 dùng đúng nội dung và ID như dense search.

## Embedding và lưu trữ

Theo lựa chọn của người dùng: `sentence_transformers`, `BAAI/bge-m3`, vector
1024 chiều, chuẩn hóa vector. Revision được ghim trong code/.env.example.
Model chạy local và không cần API key. Task 5 đã import `embed_texts()` và
`get_collection()` từ Task 4 nên sẽ dùng chung cấu hình.

ChromaDB mặc định lưu ở `chroma_db/`; có thể đổi qua `CHROMA_DB_PATH` trong
`.env`. Collection `rag_documents` dùng distance `cosine`.
Collection giữ dấu nhận diện provider/model/revision/dimension; cấu hình khác
bị từ chối để tránh trộn vector không tương thích. Nếu đổi model thì chọn
collection mới và tạo lại toàn bộ embedding tương ứng.

`upsert` cập nhật cùng ID khi chạy lại. Sau khi ghi thành công, những đoạn cũ
của tài liệu đã thay đổi được dọn khỏi collection. Chạy toàn bộ pipeline cũng
dọn các đoạn thuộc pipeline này của tài liệu đã bị loại khỏi corpus. Corpus
rỗng bị từ chối, không dùng để xóa dữ liệu.

Embedding cache mặc định nằm trong `.cache/task4-embeddings/`; có thể đổi qua
`EMBEDDING_CACHE_DIR`. Cache gắn với nội dung, provider, model, revision và
dimension. Khi bị gián đoạn có thể chạy lại, các batch đã hoàn thành không phải
tính lại. Các thư mục model, vector DB và dữ liệu index phát sinh đã được Git
bỏ qua; bản gốc và Markdown vẫn giữ nguyên.

## Chạy trên máy hiện tại

Môi trường riêng `.cache/task4-venv` dùng Python 3.10 và PyTorch CPU. Do ổ C
thiếu dung lượng, ChromaDB và dependency được cài ở
`D:/AI thuc chien/rag-model-cache/pydeps`; file `sitecustomize.py` trong
venv (Git bỏ qua) thêm đường dẫn này sau các thư viện hệ thống để giữ phiên bản
`tokenizers` tương thích với Transformers. Trên máy có đủ dung lượng, cài các
dependency từ `pyproject.toml` vào venv như bình thường.

```powershell
$env:HF_HUB_OFFLINE = "1"  # model đã tải đủ trên máy này
.\.cache\task4-venv\Scripts\python.exe -m src.task4_chunking_indexing
```

Chỉ tạo corpus để kiểm tra, không tải model hoặc ghi database:

```powershell
python -m src.task4_chunking_indexing --prepare
```

Lệnh `--prepare` chỉ cần `python-dotenv` và `PyYAML`. Trên môi trường mới,
cài `chromadb>=1,<2`, `sentence-transformers>=5,<7`, `python-dotenv`, `PyYAML`
để chạy toàn bộ Task 4. Có thể dùng `.venv` chính sau khi cài xong dự án.

Mặc định model tải vào `.cache/huggingface/`; những lần sau ưu tiên cache.
Máy hiện tại thiếu dung lượng ổ C, nên `.env` đặt `EMBEDDING_MODEL_CACHE`,
`EMBEDDING_CACHE_DIR` và `CHROMA_DB_PATH` dưới
`D:/AI thuc chien/rag-model-cache`. Model BGE-M3 đã tải đủ và kiểm tra SHA-256.
`.env` được đọc tự động nhưng không ghi đè biến môi trường của shell.
`EMBEDDING_BATCH_SIZE` mặc định 8; lần index thành công dùng batch 4 để giảm RAM.

## Kiểm tra

```powershell
.\.cache\task4-venv\Scripts\python.exe -m unittest tests.test_task4_indexing tests.test_task4_chroma -v
```

9 kiểm thử đạt, gồm kiểm thử logic offline và tích hợp Chroma thật bằng vector
nhỏ. Chúng kiểm tra metadata, giới hạn độ dài, ID, mốc trang, cache, upsert
không trùng, dọn đuôi tài liệu cũ, vector lỗi và collection không tương thích.
`reports/task4_index.json` chỉ được tạo/cập nhật sau một lần index thành công.

Bộ contract cho Task 4–10 hiện đã được triển khai và đạt kiểm thử offline.
Chất lượng tìm kiếm vẫn phụ thuộc lỗi OCR ở Task 3; Task 4 không tự sửa văn bản.

Nguồn tham khảo: [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3),
[Chroma collection configuration](https://docs.trychroma.com/docs/collections/configure).
