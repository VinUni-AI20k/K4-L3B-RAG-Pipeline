"""Create reproducible HUTECH 2026 source snapshots from official pages."""

from pathlib import Path

from fpdf import FPDF


ROOT = Path(__file__).resolve().parents[1]
LEGAL_DIR = ROOT / "data" / "landing" / "legal"
STANDARDIZED_DIR = ROOT / "data" / "standardized" / "legal"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
DATE = "2026-09-25"

SOURCES = [
    {
        "slug": "hutech_2026_phuong_thuc_tuyen_sinh",
        "title": "Phương thức tuyển sinh đại học HUTECH 2026",
        "url": "https://www.hutech.edu.vn/tuyensinh/daihoc",
        "content": (
            "Trang tuyển sinh đại học chính quy của HUTECH giới thiệu các phương thức "
            "tuyển sinh năm 2026 gồm: xét kết quả kỳ thi tốt nghiệp THPT 2026; xét kết "
            "quả kỳ thi đánh giá đầu vào đại học trên máy tính V-SAT 2026; xét kết quả "
            "kỳ thi đánh giá năng lực 2026 của Đại học Quốc gia TP.HCM; xét tuyển thẳng "
            "hoặc ưu tiên xét tuyển theo quy định và các chứng chỉ quốc tế SAT, ACT, "
            "A level, IB; và xét tuyển học bạ THPT. Thí sinh cần đối chiếu điều kiện "
            "và thời gian đăng ký trên thông báo chính thức của HUTECH."
        ),
    },
    {
        "slug": "hutech_2026_chuong_trinh_dao_tao",
        "title": "Chương trình và tổ hợp xét tuyển HUTECH 2026",
        "url": "https://www.hutech.edu.vn/tuyensinh",
        "content": (
            "Trang thông tin tuyển sinh HUTECH 2026 công bố danh mục chương trình đào "
            "tạo, mã xét tuyển, thời gian đào tạo và tổ hợp xét tuyển. Một số nhóm ngành "
            "được giới thiệu gồm kinh doanh và quản lý, công nghệ thông tin và trí tuệ "
            "nhân tạo, truyền thông - thiết kế - nghệ thuật, kỹ thuật - công nghệ, luật "
            "- ngôn ngữ - khoa học xã hội, y và khoa học sức khỏe. Các tổ hợp được sử "
            "dụng tùy ngành, có thể gồm A00, A01, D01, D09, D10, D14, D15 và các tổ hợp "
            "khác được ghi trên trang ngành tương ứng."
        ),
    },
    {
        "slug": "hutech_2026_hoc_bong",
        "title": "Chính sách học bổng tuyển sinh HUTECH 2026",
        "url": "https://www.hutech.edu.vn/tuyensinh/tin-tuyen-sinh/14630823-hutech-cong-bo-chinh-sach-hoc-bong-tuyen-sinh-khoa-2026",
        "content": (
            "HUTECH công bố học bổng tuyển sinh năm 2026 với các mức hỗ trợ 25%, 50% "
            "và 100% học phí toàn khóa cho thí sinh có thành tích học tập tốt ở bậc THPT. "
            "Tiêu chí học bạ có thể dựa trên tổng điểm trung bình ba môn lớp 11, ba môn "
            "học kỳ 1 lớp 12 hoặc ba môn cả năm lớp 12. Trang cũng nêu các nhóm học bổng "
            "Tài năng Tân sinh viên, Tiếp sức và Giáo dục với điều kiện riêng. Thời hạn "
            "đăng ký học bổng cần được kiểm tra lại trên thông báo chính thức."
        ),
    },
]


def write_pdf(item: dict) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", str(FONT))
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(0, 8, item["title"])
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, f"Official source: HUTECH website\nCollected: {DATE}")
    pdf.set_x(pdf.l_margin)
    pdf.ln(4)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, item["content"])
    pdf.output(str(LEGAL_DIR / f"{item['slug']}.pdf"))


def write_markdown(item: dict) -> None:
    content = (
        f"# {item['title']}\n\n"
        f"**Source:** {item['url']}\n\n"
        f"**Collected:** {DATE}\n\n"
        f"---\n\n{item['content']}\n"
    )
    (STANDARDIZED_DIR / f"{item['slug']}.md").write_text(content, encoding="utf-8")


def main() -> None:
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    STANDARDIZED_DIR.mkdir(parents=True, exist_ok=True)
    for item in SOURCES:
        write_pdf(item)
        write_markdown(item)
        print(f"Created {item['slug']}")


if __name__ == "__main__":
    main()
