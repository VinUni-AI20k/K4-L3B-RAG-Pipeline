# TravelBot RAG Frontend

Giao diện trực quan hiện đại cho hệ thống RAG Pipeline (TravelBot).

## 🚀 Hướng dẫn chạy trên máy khác (Cross-platform)

### Yêu cầu tiên quyết:
- **Node.js** >= 18.x (khuyến nghị Node 20 LTS)
- **npm** (đi kèm Node.js)

### Bước 1: Cài đặt dependencies
Tại thư mục `frontend`:
```bash
npm install
```

### Bước 2: Chạy Development Server
```bash
npm run dev
```
Trình duyệt sẽ mở tại: **`http://localhost:5173`**

---

## 🔌 Kết nối với Backend (Tùy chọn)

Giao diện có sẵn cơ chế **Mock / Demo Fallback Mode** thông minh:
- Nếu Backend chưa bật: UI vẫn hoạt động mượt mà, đầy đủ các tính năng (Chat có trích dẫn [1][2], Safe Refusal khi hỏi ngoài phạm vi du lịch, Debug chunks, So sánh A/B và Đánh giá 4 Metrics).
- Nếu muốn kết nối Pipeline Python thật:
  ```bash
  # Tại thư mục gốc của repo:
  uvicorn backend.api:app --reload --port 8000
  ```
  UI sẽ tự động nhận diện và chuyển sang trạng thái **🟢 Online (Connected)**.

---

## 🛠️ Build Production
Để kiểm tra hoặc build triển khai:
```bash
npm run build
npm run preview
```
