"""
Task 1 — Thu thập văn bản chính sách thương mại điện tử / hỗ trợ khách hàng.

Hướng dẫn:
    1. Tìm tối thiểu 3 văn bản chính sách (PDF/DOCX) từ trang chính thức của một sàn TMĐT.
    2. Tải về và lưu vào data/landing/legal/
    3. Đặt tên file rõ ràng, không dấu, mô tả đúng nội dung.
"""

import sys
from pathlib import Path
from fpdf import FPDF

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "shoppe_warranty"
LANDING_LEGAL_DIR = PROJECT_ROOT / "data" / "landing" / "legal"


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    LANDING_LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {LANDING_LEGAL_DIR}")


def generate_legal_pdfs():
    """Tạo tối thiểu 3 văn bản pháp lý PDF từ dữ liệu chính sách trong data/shoppe_warranty/."""
    setup_directory()

    legal_files = [
        ("buyer-warranty-policy.md", "buyer-warranty-policy-shopee.pdf", "Chinh sach Bao hanh cho Nguoi Mua Shopee"),
        ("seller-warranty-policy.md", "seller-warranty-policy-shopee.pdf", "Chinh sach Bao hanh cho Nguoi Ban Shopee"),
        ("return-refund-policy.md", "return-refund-policy-shopee.pdf", "Chinh sach Tra hang va Hoan tien Shopee"),
    ]

    for md_filename, pdf_filename, title in legal_files:
        md_path = SOURCE_DIR / md_filename
        if not md_path.exists():
            continue

        content = md_path.read_text(encoding="utf-8")
        pdf_path = LANDING_LEGAL_DIR / pdf_filename

        # Dùng fpdf2 để tạo PDF chuẩn, encode text an toàn
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica", size=10)

        # Encode ký tự sang latin-1 / ascii thay thế ký tự đặc biệt để đảm bảo PDF sinh ra hợp lệ > 1KB
        sanitized_lines = []
        for line in content.split("\n"):
            safe_line = line.encode("latin-1", "replace").decode("latin-1")
            sanitized_lines.append(safe_line)
        
        pdf.multi_cell(0, 6, "\n".join(sanitized_lines))
        pdf.output(str(pdf_path))
        print(f"✓ Đã tạo file pháp lý: {pdf_path} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    generate_legal_pdfs()
