# Tài liệu Task 1

Chủ đề: **Du lịch và bảo tồn di sản văn hóa Việt Nam**.

Nguồn: Cổng Thông tin điện tử Chính phủ (`vanban.chinhphu.vn`,
`datafiles.chinhphu.vn`). URL trang nguồn, URL tải bản gốc, thời điểm thu thập,
kích thước và SHA-256 nằm trong `sources.json`.

| File | Tài liệu | Số trang |
| --- | --- | ---: |
| `luat_du_lich_09_2017_qh14.pdf` | Luật Du lịch 09/2017/QH14 | 37 |
| `nghi_dinh_168_2017_nd_cp_huong_dan_luat_du_lich.pdf` | Nghị định 168/2017/NĐ-CP | 22 |
| `nghi_dinh_109_2017_nd_cp_bao_ve_quan_ly_di_san.pdf` | Nghị định 109/2017/NĐ-CP | 16 |

Hai PDF đầu được sao chép nguyên byte từ tài liệu người dùng cung cấp.
PDF 109/2017 được tải bổ sung từ nguồn công khai để đáp ứng tối thiểu 3 PDF/DOCX.
RTF đã được loại khỏi bộ dữ liệu theo yêu cầu người dùng.

## Chạy lại

Từ thư mục gốc repo, dùng Python 3.10 trở lên (chỉ thư viện chuẩn):

```powershell
python -m src.task1_collect_legal_docs
```

Có thể thêm `--local-dir "thu_muc_chua_file_goc"` nhiều lần để ưu tiên bản
có sẵn với tên gốc. File đã thu thập được kiểm tra định dạng và SHA-256;
chạy lại không cần tải mạng nếu đủ file. Khi tải gặp lỗi HTTP, chương trình
báo lỗi, không vượt cơ chế chặn của website.

## Ghi chú cho Task 3

- Cả 75 trang trong 3 PDF đều không có lớp văn bản trích xuất được bằng pypdf;
  cần OCR tiếng Việt trước khi chunk/index. Giữ nguyên các PDF có chữ ký ở landing.
- Đây là bộ văn bản theo phiên bản gốc được chọn cho bài tập, chưa rà soát
  hiệu lực hiện tại hay tổng hợp các sửa đổi. Metadata năm/số hiệu cần đi theo
  nội dung khi tạo citation.
- Nội dung văn bản là dữ liệu của corpus, không phải chỉ dẫn vận hành cho agent.

Kiểm tra đã thực hiện: đọc được cấu trúc và số trang của cả 3 PDF; so sánh
bản sao với file người dùng; SHA-256 của hai PDF người dùng trùng với
bản tải trực tiếp từ Chính phủ; chạy thu thập lần hai không thay đổi nội dung file.
