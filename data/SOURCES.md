# Hồ sơ nguồn dữ liệu Du lịch Việt Nam

Ngày xác minh: 25/09/2026. Phạm vi demo: Huế – Đà Nẵng – Hội An.

## Văn bản chính sách và quy định

| Văn bản | Cơ quan | Ban hành | Hiệu lực | Tình trạng/phiên bản | Nguồn xác minh |
|---|---|---:|---:|---|---|
| Luật Du lịch 09/2017/QH14 | Quốc hội | 19/06/2017 | 01/01/2018 | Còn hiệu lực; lưu bản Công báo có thể tìm kiếm nội dung | [Cổng TTĐT Chính phủ](https://vanban.chinhphu.vn/default.aspx?docid=190290&pageid=27160) |
| Nghị định 168/2017/NĐ-CP | Chính phủ | 31/12/2017 | 01/01/2018 | Còn hiệu lực; khi áp dụng điều cụ thể cần đối chiếu văn bản sửa đổi | [Cổng TTĐT Chính phủ](https://vanban.chinhphu.vn/?docid=193059&pageid=27160) |
| Nghị định 45/2019/NĐ-CP | Chính phủ | 21/05/2019 | 01/08/2019 | Hết hiệu lực một phần; phải đọc cùng Nghị định 129/2021/NĐ-CP và 348/2025/NĐ-CP | [Cổng TTĐT Chính phủ](https://chinhphu.vn/default.aspx?docid=197075&pageid=27160) |
| Nghị định 348/2025/NĐ-CP | Chính phủ | 30/12/2025 | 15/02/2026 | Còn hiệu lực; là bản sửa đổi mới thu thập cho Nghị định 45/2019/NĐ-CP | [Cổng TTĐT Chính phủ](https://vanban.chinhphu.vn/?docid=216361&pageid=27160) |

Các PDF trong `data/landing/legal/` được tải từ hệ thống Công báo điện tử của Chính phủ. Metadata máy đọc được và URL tải trực tiếp nằm trong `data/landing/legal/legal_sources.json`.

Lưu ý sử dụng: không trả lời mức phạt hiện hành chỉ từ Nghị định 45/2019/NĐ-CP mà không đối chiếu Nghị định 348/2025/NĐ-CP hoặc văn bản hợp nhất mới nhất.

## Bài viết và page du lịch

| Nội dung | Đơn vị xuất bản | URL |
|---|---|---|
| Điểm đến nổi bật tại Huế | Cổng thông tin du lịch thành phố Huế | [Nguồn](https://visithue.vn/Top-10-dia-diem-%E2%80%9Cchup-anh-dep-khong-muon-ve%E2%80%9D-ngay-tai-Hue.html/?pid=MTkyMTR8Y3NkbGRs0) |
| Danh thắng Ngũ Hành Sơn | Cổng thông tin du lịch thành phố Đà Nẵng | [Nguồn](https://danangfantasticity.com/cn/danh-thang-ngu-hanh-son) |
| Trải nghiệm văn hóa tại Hội An | Cục Du lịch Quốc gia Việt Nam | [Nguồn](https://www.vietnam.travel/things-to-do/7-things-to-do-hoi-an) |
| Ẩm thực đặc trưng tại Huế | Cổng thông tin du lịch thành phố Huế | [Nguồn](https://visithue.vn/10-mon-an-ngon-phai-thu-it-nhat-mot-lan-khi-den-Hue.html/?pid=MTkzNjB8Y3NkbGRs0) |
| Trải nghiệm và di chuyển tại miền Trung | Cục Du lịch Quốc gia Việt Nam | [Nguồn](https://www.vietnam.travel/things-to-do/top-things-do-central-vietnam) |

Thông tin giá, giờ mở cửa hoặc lịch hoạt động chỉ phản ánh thời điểm `date_crawled` trong từng JSON, không được trình bày như dữ liệu thời gian thực.

## Quy trình tái tạo

```powershell
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
python -m src.task3_convert_markdown
```

Task 1 xác minh PDF bằng kích thước và PDF signature, đồng thời ghi manifest. Task 2 giữ URL, title, publisher, thời điểm crawl và nội dung đã làm sạch. Task 3 thêm front matter để Cường có thể ánh xạ `source`, `title`, `doc_type` và `url` vào metadata chunk.
