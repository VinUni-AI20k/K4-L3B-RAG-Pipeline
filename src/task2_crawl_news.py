"""
Task 2 — Crawl bài viết/thông báo.

Chủ đề: thuế và nghĩa vụ kê khai của hộ kinh doanh cá thể.

9 bài viết (>=5 yêu cầu), **toàn bộ từ nguồn nhà nước**: chinhphu.vn
(xaydungchinhsach, baochinhphu) và VietnamPlus (Thông tấn xã Việt Nam).
Các blog nhà cung cấp phần mềm (einvoice/misa/meinvoice/easybooks) đã bị
loại bỏ để tăng độ tin cậy của corpus.

Phủ các mảng: bỏ thuế khoán và lệ phí môn bài, ngưỡng doanh thu hiện hành
(Nghị định 141/2026/NĐ-CP nâng từ 500 triệu lên 01 tỷ đồng), tỷ lệ/thuế
suất theo hoạt động kinh doanh, hồ sơ và thời hạn kê khai, hoá đơn điện tử,
xử phạt vi phạm hành chính về quản lý thuế.

Ghi chú: thuvienphapluat.vn bị chặn bởi Cloudflare JS challenge (403/307).
Theo hướng dẫn của task này ("nếu website chặn crawler, hãy chọn nguồn công
khai khác; không vượt WAF"), dùng nguồn .gov.vn tương đương thay thế.

Cài browser trước khi chạy:
    python -m playwright install chromium
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # Cai cach 2026: bo ap dung thue khoan (Thong tan xa Viet Nam).
    "https://www.vietnamplus.vn/bo-ap-dung-thue-khoan-ho-kinh-doanh-buoc-vao-cuoc-choi-moi-post1042297.vnp",
    # Tong quan noi dung moi ND68/2026 + TT18/2026.
    "https://xaydungchinhsach.chinhphu.vn/noi-dung-moi-cua-nghi-dinh-68-2026-nd-cp-va-thong-tu-18-2026-tt-btc-nguoi-nop-thue-can-luu-y-119260312140920747.htm",
    # TOAN VAN Nghi dinh 141/2026/ND-CP: sua "500 trieu dong" thanh "01 ty dong"
    # tai Dieu 3, Dieu 4 ND68/2026. Ban PDF ky so tren vanban.chinhphu.vn la anh
    # scan khong co lop text, nen day la nguon van ban day du duy nhat doc duoc.
    "https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-so-141-2026-nd-cp-nang-nguong-doanh-thu-khong-phai-chiu-thue-len-1-ty-dong-119260504154326455.htm",
    # Huong dan trien khai ND141/2026.
    "https://xaydungchinhsach.chinhphu.vn/huong-dan-trien-khai-nghi-dinh-so-141-2026-nd-cp-ve-chinh-sach-thue-doi-voi-ho-kinh-doanh-doanh-nghiep-119260502203430701.htm",
    # Nang nguong chiu thue len 1 ty dong/nam, ap dung tu 01/01/2026.
    "https://baochinhphu.vn/chinh-thuc-nang-nguong-chiu-thue-voi-ho-kinh-doanh-len-01-ty-dong-nam-ap-dung-tu-1-1-2026-102260429185517215.htm",
    # Thue suat / ty le theo tung hoat dong kinh doanh cua ho kinh doanh.
    "https://xaydungchinhsach.chinhphu.vn/thue-suat-doi-voi-cac-hoat-dong-kinh-doanhcua-ho-kinh-doanh-119260407103211289.htm",
    # Luu y khi ke khai thue theo ky (ho so, thoi han).
    "https://xaydungchinhsach.chinhphu.vn/luu-y-chinh-trong-ky-khai-thue-quy-i-2026-119260312174235595.htm",
    # Muc phat tien trong xu phat vi pham hanh chinh ve quan ly thue.
    "https://xaydungchinhsach.chinhphu.vn/muc-phat-tien-trong-xu-phat-vi-pham-hanh-chinh-ve-quan-ly-thue-119260331093932736.htm",
    # Diem moi ND254/2026 + TT91/2026 ve hoa don dien tu, chung tu dien tu.
    "https://xaydungchinhsach.chinhphu.vn/nhung-diem-moi-cua-nghi-dinh-254-2026-nd-cp-va-thong-tu-91-2026-tt-btc-ve-hoa-don-dien-tu-chung-tu-dien-tu-119260717143502375.htm",
]


async def crawl_article(url: str) -> dict:
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not result.success or (result.status_code or 200) >= 400:
            raise ValueError(f"Crawl failed for {url}: {result.error_message}")
        title = (result.metadata or {}).get("title") or url
        markdown = str(result.markdown) if result.markdown else ""
        if not markdown.strip():
            raise ValueError(f"Empty markdown for {url}")
        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
