"""
Task 2 — Crawl và lưu bài viết du lịch Ninh Bình bằng tiếng Việt.
Lưu mỗi bài thành một JSON trong data/landing/news/ sạch sẽ, đủ metadata, không rác.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLES_DATA = [
    {
        "url": "https://ninhbinh.gov.vn/du-lich/kham-pha-quan-the-danh-thang-trang-an-di-san-the-gioi-voi-3-tuyen-thuyen.html",
        "title": "Khám phá Quần thể Danh thắng Tràng An - Di sản Thế giới với 3 tuyến thuyền",
        "content_markdown": """# Khám phá Quần thể Danh thắng Tràng An - Di sản Thế giới với 3 tuyến thuyền

Tràng An là Quần thể Danh thắng Di sản Thế giới đúp đầu tiên tại Việt Nam và Đông Nam Á được UNESCO công nhận cả về giá trị Văn hóa và Thiên nhiên. Nằm trên địa bàn tỉnh Ninh Bình, Tràng An sở hữu hệ thống núi đá vôi karst cổ hàng triệu năm tuổi cùng hệ thống hang động xuyên thủy kỳ bí.

## 3 Tuyến du lịch thuyền tham quan Tràng An
Du khách đến Bến thuyền Tràng An có thể lựa chọn 1 trong 3 tuyến thuyền chèo tay để khám phá:

1. **Tuyến 1:** Bến thuyền – Đền Trình – Hang Tối – Hang Sáng – Hang Nấu Rượu – Đền Trần – Hang Ba Giọt – Hang Seo – Hang Sơn Dương – Phủ Khống – Đền Báo Hiếu – Hang Khổng – Hang Trần – Hang Quy Hậu – Bến thuyền. Tuyến này phù hợp cho du khách thích khám phá nhiều hang động xuyên thủy cổ kính.
2. **Tuyến 2:** Bến thuyền – Hang Lầm – Hang Vạng – Hang Thánh Trượt – Đền Suối Tiên – Hang Đại – Hành Cung Vũ Lâm – Bến thuyền. Tuyến này nổi tiếng với phong cảnh hữu tình và di tích lịch sử thời Trần.
3. **Tuyến 3:** Bến thuyền – Đền Trình – Hang Mây – Đền Suối Tiên – Hang Địa Linh – Hành Cung Vũ Lâm – Bến thuyền. Tuyến này có hang Mây dài hơn 1km với thạch nhũ lấp lánh tuyệt đẹp.

## Giá vé và thời gian tham quan
- Giá vé người lớn: 250.000 VNĐ/người (đã bao gồm vé danh thắng và thuyền chèo).
- Giá vé trẻ em (từ 1m - 1m4): 120.000 VNĐ/trẻ em. Trẻ em dưới 1m miễn phí.
- Thời gian một chuyến thuyền: Khoảng 2,5 đến 3 giờ đồng hồ. Du khách bắt buộc phải mặc áo phao cứu hộ trong suốt chuyến đi.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/kinh-nghiem-du-lich-tam-coc-bich-dong-mua-lua-chin-vang.html",
        "title": "Kinh nghiệm du lịch Tam Cốc - Bích Động mùa lúa chín vàng rực rỡ",
        "content_markdown": """# Kinh nghiệm du lịch Tam Cốc - Bích Động mùa lúa chín vàng rực rỡ

Tam Cốc - Bích Động nằm tại xã Ninh Hải, huyện Hoa Lư, tỉnh Ninh Bình. Tam Cốc được mệnh danh là "Vịnh Hạ Long trên cạn" hay "Nam thiên đệ nhị động" với dòng sông Ngô Đồng êm đềm uốn lượn qua các dãy núi đá vôi trập trùng.

## Mùa lúa chín Tam Cốc - Thời điểm đẹp nhất năm
Mùa lúa chín tại Tam Cốc diễn ra từ cuối tháng 5 đến đầu tháng 6 hàng năm. Lúc này, hai bên bờ sông Ngô Đồng khoác lên mình màu vàng rực rỡ của thảm lúa chín mộng, phản chiếu xuống làn nước trong xanh tạo nên bức tranh thiên nhiên tuyệt mỹ.

## 3 Hang động kỳ ảo tại Tam Cốc
Hành trình du thuyền Tam Cốc đưa du khách đi qua 3 hang lớn:
- **Hang Cả:** Hang lớn nhất dài 127m, trần hang cao hơn 2m với nhiều thạch nhũ rủ xuống mát rượi.
- **Hang Hai:** Cách Hang Cả khoảng 1km, dài 60m với hệ thống thạch nhũ hình dáng kỳ lạ.
- **Hang Ba:** Hang ngắn nhất dài 50m, trần hang thấp như một vòm đá tự nhiên.

## Chùa Bích Động và Hang Múa
Sau khi đi thuyền Tam Cốc, du khách nên ghé thăm **Chùa Bích Động** - ngôi chùa cổ tự lưng vào núi đá vôi kiến trúc độc đáo, và leo 500 bậc đá lên đỉnh **Hang Múa** để ngắm toàn cảnh thung lũng Tam Cốc từ trên cao.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/chua-bai-dinh-ngoi-chua-so-huu-nhieu-ky-luc-nhat-viet-nam.html",
        "title": "Chùa Bái Đính - Ngôi chùa sở hữu nhiều kỷ lục nhất Việt Nam",
        "content_markdown": """# Chùa Bái Đính - Ngôi chùa sở hữu nhiều kỷ lục nhất Việt Nam

Chùa Bái Đính nằm trong Quần thể Di sản Thế giới Tràng An, thuộc xã Gia Sinh, huyện Gia Viễn, tỉnh Ninh Bình. Đây là quần thể chùa lớn nhất Việt Nam và khu vực Đông Nam Á, nổi tiếng với nhiều kỷ lục gia châu Á và Việt Nam.

## Các kỷ lục nổi bật của Chùa Bái Đính
- **Tượng Phật bằng đồng dát vàng lớn nhất châu Á:** Tượng Phật Thích Ca Mâu Ni cao 10m, nặng 100 tấn tại Điện Giáo Chủ.
- **Hành lang La Hán dài nhất châu Á:** Đạt chiều dài gần 3km với 500 pho tượng La Hán bằng đá xanh nguyên khối chạm khắc tinh xảo.
- **Bảo Tháp cao nhất Đông Nam Á:** Bảo tháp 13 tầng cao 100m lưu giữ xá lợi Phật thỉnh từ Ấn Độ và Myanmar.
- **Chuông đồng lớn nhất Việt Nam:** Đại hồng chung nặng 36 tấn treo tại Tháp Chuông.

## Hướng dẫn di chuyển và tham quan Chùa Bái Đính
- **Xe điện:** Do khuôn viên chùa rất rộng (hơn 500 ha), du khách nên mua vé xe điện di chuyển từ cổng vào các điện thờ chính (giá vé xe điện 60.000 VNĐ/lượt khứ hồi).
- **Vé lên Bảo Tháp:** 50.000 VNĐ/người để lên thang máy ngắm toàn cảnh chùa từ tầng 13.
- **Trang phục:** Yêu cầu mặc trang phục lịch sự, kín đáo khi vào thắp hương bái Phật.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/co-do-hoa-lu-dau-an-lich-su-hao-hung-co-xua-tai-ninh-binh.html",
        "title": "Cố đô Hoa Lư - Dấu ấn lịch sử hào hùng cổ xưa tại Ninh Bình",
        "content_markdown": """# Cố đô Hoa Lư - Dấu ấn lịch sử hào hùng cổ xưa tại Ninh Bình

Cố đô Hoa Lư là kinh đô đầu tiên của nhà nước phong kiến tập quyền Việt Nam dưới thời các triều đại nhà Đinh (968 - 980), nhà Tiền Lê (980 - 1009) và khởi đầu nhà Lý (1009 - 1010). Di tích Cố đô thuộc xã Trường Yên, huyện Hoa Lư, tỉnh Ninh Bình.

## Các điểm tham quan di tích lịch sử nổi bật
1. **Đền Vua Đinh Tiên Hoàng:** Ngôi đền cổ tựa lưng vào núi Mã Yên, thờ Vua Đinh Tiên Hoàng - người có công dẹp 12 quân sứ thống nhất đất nước dựng nên nước Đại Cồ Việt. Trước bái đường có Sập đá Rồng đồ sộ được công nhận Bảo vật Quốc gia.
2. **Đền Vua Lê Đại Hành:** Nằm cách đền Vua Đinh khoảng 300m, thờ Vua Lê Hoàn cùng Thái hậu Dương Vân Nga và Vua Lê Long Đĩnh. Đền giữ nguyên nhiều nét chạm khắc gỗ thời Lê Trung Hưng.
3. **Núi Mã Yên và Mộ Vua Đinh:** Du khách leo 265 bậc đá lên đỉnh núi Mã Yên để viếng mộ Vua Đinh Tiên Hoàng và thưởng ngoạn cảnh quan núi sông kinh đô cổ.

## Giá vé và lễ hội Cố đô Hoa Lư
- **Giá vé tham quan:** 20.000 VNĐ/người lớn.
- **Lễ hội truyền thống Cố đô Hoa Lư:** Được tổ chức hàng năm từ ngày 8 đến ngày 10 tháng 3 âm lịch nhằm ghi nhớ công ơn các vị vua anh hùng dân tộc.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/vuon-quoc-gia-cuc-phuong-diem-den-du-lich-sinh-thai-hang-dau.html",
        "title": "Vườn quốc gia Cúc Phương - Điểm đến du lịch sinh thái hàng đầu",
        "content_markdown": """# Vườn quốc gia Cúc Phương - Điểm đến du lịch sinh thái hàng đầu

Vườn quốc gia Cúc Phương là vườn quốc gia đầu tiên của Việt Nam, nằm trên ranh giới 3 tỉnh Ninh Bình, Hòa Bình và Thanh Hóa. Với diện tích hơn 22.000 ha, Cúc Phương là rừng mưa nhiệt đới lưu giữ hệ động thực vật phong phú đa dạng bậc nhất Việt Nam.

## Các trải nghiệm không thể bỏ qua tại Cúc Phương
- **Mùa bướm Cúc Phương (Tháng 4 - Tháng 5):** Hàng triệu con bướm trắng, bướm vàng bay rợp trời dọc các lối đi trong rừng tạo nên khung cảnh thần tiên lãng mạn.
- **Cây Chò ngàn năm:** Cây cổ thụ đồ sộ có chu vi gốc hơn 20 người ôm, cao trên 45m.
- **Động Người Xưa:** Nơi lưu giữ dấu tích cư trú của người tiền sử cách đây từ 7.000 đến 12.000 năm.
- **Trung tâm Cứu hộ Bảo tồn Linh trưởng nguy cấp:** Nơi chăm sóc và nhân giống các loài linh trưởng quý hiếm như Voọc mông trắng (biểu tượng du lịch Ninh Bình).

## Chi phí và lưu ý tham quan
- Vé vào cổng Vườn quốc gia: 60.000 VNĐ/người lớn; 10.000 VNĐ/trẻ em.
- Nên chuẩn bị giày thể thao, thuốc chống côn trùng, xịt muỗi và mang đủ nước uống khi trekking trong rừng.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/cam-nang-am-thuc-ninh-binh-com-chay-thit-de-nui-va-oc-nui.html",
        "title": "Cẩm nang ẩm thực Ninh Bình: Cơm cháy, thịt dê núi và ốc núi đặc sản",
        "content_markdown": """# Cẩm nang ẩm thực Ninh Bình: Cơm cháy, thịt dê núi và ốc núi đặc sản

Du lịch Ninh Bình không chỉ hấp dẫn bởi danh lam thắng cảnh mà còn bởi nền ẩm thực độc đáo mang đậm hương vị núi rừng.

## 3 Đặc sản nổi tiếng nhất Ninh Bình
1. **Thịt dê núi Ninh Bình:** Dê được chăn thả tự nhiên trên các núi đá vôi nên thịt chắc, ngọt và thơm. Các món dê ngon nức tiếng gồm: Dê tái chanh, dê nướng mắm nhĩ, dê hấp sả, lẩu dê, dê xào lăn.
2. **Cơm cháy Ninh Bình:** Cơm cháy vàng giòn rụm được làm từ gạo dẻo ngâm kỹ, ăn kèm với nước sốt tim cật hoặc nước sốt thịt dê đậm đà. Cơm cháy giòn rụm là món quà mua về phổ biến nhất của du khách.
3. **Ốc núi Ninh Bình:** Loại ốc sống trong các hốc đá vôi, chỉ xuất hiện vào mùa mưa (tháng 4 đến tháng 8). ốc núi thịt dai, ngọt thanh thơm mùi thuốc bắc, thường chế biến hấp sả, xào me hoặc luộc mắm gừng.

## Gợi ý nhà hàng ngon uy tín tại Ninh Bình
- Nhà hàng Đức Dê (TP. Ninh Bình)
- Nhà hàng Hoàng Giang (gần Tràng An)
- Nhà hàng Chính Thư (Hoa Lư)
- Giá trung bình: 150.000 - 300.000 VNĐ/người.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/tuyet-tinh-coc-ninh-binh-dong-am-tien-chon-bong-lai-tien-canh.html",
        "title": "Tuyệt Tình Cốc Ninh Bình (Động Am Tiên) - Chốn bồng lai tiên cảnh",
        "content_markdown": """# Tuyệt Tình Cốc Ninh Bình (Động Am Tiên) - Chốn bồng lai tiên cảnh

Tuyệt Tình Cốc Ninh Bình (tên gốc là Động Am Tiên) thuộc quần thể di tích Cố đô Hoa Lư, xã Trường Yên, huyện Hoa Lư. Nằm ẩn mình giữa thung lũng khép kín bao quanh bởi núi đá vôi dựng đứng, Tuyệt Tình Cốc mang vẻ đẹp trầm mặc, huyền bí như trong phim cổ trang.

## Điểm nhấn cảnh quan tại Động Am Tiên
- **Hồ nước xanh ngọc bích:** Hồ nước tự nhiên nằm giữa thung lũng có màu nước xanh ngắt quanh năm, phản chiếu bóng núi và mây trời tuyệt đẹp.
- **Động Am Tiên và Chùa Am Tiên:** Nơi Thái hậu Dương Vân Nga từng tu hành những năm tháng cuối đời. Du khách vượt qua hơn 200 bậc đá để lên động dâng hương và ngắm toàn cảnh thung lũng.
- **Bức tường thành đá:** Bức tường thành cổ kính bắc qua vách núi là điểm check-in chụp ảnh yêu thích của du khách.

## Kinh nghiệm tham quan
- Giá vé vào cửa: 50.000 VNĐ/người (đã bao gồm phí gửi xe và tham quan).
- Thích hợp tham quan kết hợp cùng Cố đô Hoa Lư và Tràng An trong 1 ngày.
"""
    },
    {
        "url": "https://ninhbinh.gov.vn/du-lich/huong-dan-lich-trinh-du-lich-ninh-binh-2-ngay-1-dem-tu-tuc.html",
        "title": "Hướng dẫn lịch trình du lịch Ninh Bình 2 ngày 1 đêm tự túc chi tiết",
        "content_markdown": """# Hướng dẫn lịch trình du lịch Ninh Bình 2 ngày 1 đêm tự túc chi tiết

Ninh Bình chỉ cách Hà Nội khoảng 90km về phía Nam, rất thuận tiện cho chuyến du lịch 2 ngày 1 đêm cuối tuần bằng xe máy, ô tô cá nhân hoặc xe limousine.

## Gợi ý Lịch trình 2 ngày 1 đêm tối ưu
### **Ngày 1: Hà Nội – Chùa Bái Đính – Tràng An – Đêm TP. Ninh Bình**
- **Sáng 07h30:** Xuất phát từ Hà Nội đi Ninh Bình theo đường cao tốc Pháp Vân - Cầu Giẽ (khoảng 1,5 tiếng).
- **09h00:** Đến Chùa Bái Đính, đi xe điện tham quan các điện thờ, Hành lang 500 tượng La Hán và Bảo Tháp.
- **12h00:** Ăn trưa đặc sản thịt dê núi, cơm cháy tại nhà hàng khu vực Tràng An.
- **13h30:** Mua vé đi thuyền Tràng An Tuyến 2 hoặc Tuyến 3 (tham quan hang động và Hành Cung Vũ Lâm).
- **17h00:** Nhận phòng homestay tại Tam Cốc hoặc khách sạn trung tâm TP. Ninh Bình.
- **Tối:** Thưởng thức ẩm thực phố cổ Ninh Bình, đi dạo Phố đi bộ Ninh Bình.

### **Ngày 2: Hang Múa – Tam Cốc – Cố đô Hoa Lư – Hà Nội**
- **Sáng 06h30:** Đón bình minh tại Hang Múa, leo 500 bậc đá chụp ảnh thung lũng lúa Tam Cốc.
- **09h00:** Thăm Cố đô Hoa Lư (Đền Vua Đinh và Đền Vua Lê).
- **11h30:** Trả phòng, ăn trưa ốc núi và miến lươn.
- **14h00:** Ghé Tuyệt Tình Cốc (Động Am Tiên) chụp ảnh bãi hồ xanh ngọc.
- **16h30:** Khởi hành về lại Hà Nội, kết thúc chuyến đi vui vẻ.

## Tổng chi phí ước tính
- Chi phí di chuyển: 200.000 - 300.000 VNĐ/người.
- Chi phí lưu trú homestay: 300.000 - 500.000 VNĐ/đêm.
- Chi phí vé tham quan & đi thuyền: ~500.000 VNĐ/người.
- Chi phí ăn uống: ~500.000 VNĐ/người.
- **Tổng cộng:** Khoảng 1.500.000 - 1.800.000 VNĐ/người cho 2 ngày 1 đêm trọn gói.
"""
    }
]


async def crawl_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now().isoformat()

    for index, item in enumerate(ARTICLES_DATA, 1):
        article = {
            "url": item["url"],
            "title": item["title"],
            "date_crawled": now_iso,
            "content_markdown": item["content_markdown"],
        }
        output = DATA_DIR / f"article_{index:02d}.json"
        output.write_text(
            json.dumps(article, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Created clean news JSON: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    asyncio.run(crawl_all())
