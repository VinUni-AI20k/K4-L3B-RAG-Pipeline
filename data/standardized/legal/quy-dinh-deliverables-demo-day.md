---
id: doc_legal_demo_day_deliverables
source: quy-dinh-deliverables-demo-day.docx
title: "Quy định 10 Deliverables và Hướng dẫn Nộp bài Demo Day"
doc_type: legal
document_type: policy
url: "https://phoenix.note.transformerlabs.ai/technical-book/chapter-09"
source_url: "https://phoenix.note.transformerlabs.ai/technical-book/chapter-09"
source_name: "Ban Tổ Chức AI20K Technical Guidebook"
collected_at: "2026-09-22T07:50:00Z"
language: vi
---

# Quy định 10 Deliverables và Hướng dẫn Nộp bài Demo Day
**Nguồn:** Ban Tổ Chức AI20K Technical Guidebook (https://phoenix.note.transformerlabs.ai/technical-book/chapter-09)


# QUY ĐỊNH 10 DELIVERABLES VÀ HƯỚNG DẪN NỘP BÀI DEMO DAY

Ban Tổ Chức AI20K — Technical Guidebook Chương 9 (Nộp bài Demo Day)

## 1. Yêu cầu chung về Deliverables

Ban Tổ Chức (BTC) AI20K yêu cầu mỗi đội nộp đầy đủ 10 deliverables cho sự kiện Demo Day. Hoàn thành đủ 10/10 deliverables là điều kiện tiên quyết để đạt điểm tối đa ở tiêu chí 'Hoàn thành deliverables'. Mọi sản phẩm phải nằm trong repository được hệ thống tự động sinh trong GitHub Organization của khóa học; repo tự tạo bên ngoài org sẽ không được chấm.

## 2. Chi tiết 10 Deliverables bắt buộc của BTC

* 1. Source Code (GitHub Repository): Push toàn bộ mã nguồn lên GitHub. Repo có cấu trúc rõ ràng, có .gitignore chuẩn, không commit file nhạy cảm (.env/secrets) hay file dữ liệu nặng (>10MB). Đảm bảo code chạy được sau khi cấu hình biến môi trường.
* 2. README.md: Tài liệu giới thiệu dự án hoàn chỉnh gồm: Tên dự án, mô tả giải pháp, ảnh chụp màn hình/GIF demo, hướng dẫn cài đặt môi trường, cách chạy, cấu trúc thư mục, tech stack và danh sách thành viên nhóm.
* 3. Architecture Diagram: Sơ đồ kiến trúc thể hiện rõ các tầng hệ thống: Frontend, Backend API, AI Agent (LangGraph), Vector Store / Database, và kết nối dịch vụ bên ngoài. Đặt tại docs/architecture.md hoặc file ảnh/PDF.
* 4. AI Logs: Minh chứng hoạt động của AI Agent và quá trình reasoning. Cấu hình logging qua LangSmith (3 biến môi trường) hoặc lưu vết logs hệ thống chứng minh các bước suy luận.
* 5. Live URL: Đường dẫn website truy cập thực tế qua internet. Deploy frontend lên Vercel/Netlify và backend lên Render/Cloud. Đảm bảo URL duy trì hoạt động tối thiểu đến hết Demo Day + 7 ngày.
* 6. Video Demo: Video quay màn hình thời lượng 3-5 phút giới thiệu nhóm, trình diễn use case chính của AI Agent, giải thích luồng xử lý kiến trúc và minh họa tình huống xử lý biên (edge cases). Upload YouTube (unlisted).
* 7. Pitch Deck: Bộ slide thuyết trình chuẩn 10 slide phục vụ báo cáo trước hội đồng giám khảo tại Demo Day. Mỗi slide trình bày gọn trong khoảng 1 phút.
* 8. Development Journal: Nhật ký phát triển (docs/journal.md) ghi nhận các quyết định kỹ thuật quan trọng, các khó khăn gặp phải trong quá trình build và cách đội ngũ giải quyết, kèm bài học rút ra.
* 9. Worklog: Lịch sử commit đều đặn chứng minh quá trình làm việc liên tục của từng thành viên trong suốt kỳ đào tạo (docs/worklog.md hoặc trích xuất git log).
* 10. Evaluation Evidence: Bằng chứng đánh giá định lượng chất lượng của AI Agent (docs/evaluation.md). Sử dụng bộ chỉ số đánh giá chuyên sâu (như RAGAS: Faithfulness, Answer Relevance, Context Precision/Recall) kèm kết quả kiểm thử thực nghiệm.

## 3. Cấu trúc thư mục chuẩn trong GitHub Repository

Mỗi deliverable phải được sắp xếp chính xác theo cây thư mục sau:
project-root/
├── README.md               # Deliverable #2
├── docs/
│   ├── architecture.md     # Deliverable #3 (hoặc file ảnh/PDF)
│   ├── video-demo.md       # Deliverable #6 (link YouTube)
│   ├── pitch-deck.pdf      # Deliverable #7
│   ├── journal.md          # Deliverable #8
│   ├── worklog.md          # Deliverable #9
│   └── evaluation.md       # Deliverable #10
├── src/                    # Deliverable #1 (Source Code)
├── tests/                  # Bộ kiểm thử cho Evaluation Evidence
├── .github/workflows/      # CI/CD tự động hóa kiểm tra mã nguồn
├── Dockerfile              # Docker container phục vụ triển khai
└── docker-compose.yml