"""Build source-grounded evaluation cases; fail if any selected evidence changed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "group_project/evaluation"


def build() -> None:
    documents = {}
    for path in (ROOT / "data/standardized").glob("*/*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        documents[document["id"]] = document
    cases = []

    def add(question, answer, references, category="direct"):
        evidence = []
        for source_id, needle in references:
            doc = documents[source_id]
            blocks = doc["content"].split("\n\n")
            matches = [block for block in blocks if needle in block]
            if len(matches) != 1:
                raise ValueError(f"Evidence must match exactly one paragraph: {source_id}: {needle}")
            quote = matches[0]
            prefix = doc["content"][:doc["content"].index(quote)]
            pages = [line for line in prefix.splitlines() if line.startswith("## Trang ")]
            evidence.append({"source_id": source_id, "url": doc["metadata"]["url"],
                "source": doc["metadata"]["source"], "quote": quote,
                "locator": pages[-1] if pages else f"paragraph {blocks.index(quote) + 1}"})
        cases.append({"id": f"NEU2026-{len(cases)+1:02d}", "question": question,
            "expected_answer": answer, "expected_context": "\n\n".join(e["quote"] for e in evidence),
            "admission_year": 2026, "audience": "dai_hoc_chinh_quy", "category": category,
            "evidence": evidence, "split": "evaluation"})

    n1, n2, n3, n4, n5 = [f"neu2026_news_{i:02d}" for i in range(1, 6)]
    legal = "neu2026_undergraduate"
    add("Cổng đăng ký hồ sơ xét tuyển trực tuyến của NEU năm 2026 ở đâu?",
        "Cổng đăng ký là https://xtkh.neu.edu.vn.", [(n1, "đã chính thức vận hành")])
    add("Theo hướng dẫn NEU 2026, thí sinh Nhóm 5 có nộp lệ phí trên cổng NEU không?",
        "Nhóm 5 chỉ xét điểm ba môn thi tốt nghiệp THPT bỏ qua bước nộp lệ phí trên cổng NEU. Điều này không đồng nghĩa được miễn lệ phí trên hệ thống Bộ GDĐT.",
        [(n1, "**Thí sinh xét tuyển Nhóm 5**"), (n2, "| Nộp lệ phí xét tuyển trực tuyến |")], "multi_source")
    add("NEU hướng dẫn dùng trình duyệt nào và chế độ nào để đăng ký hồ sơ năm 2026?",
        "Chrome ở chế độ ẩn danh; trên máy tính mở bằng Ctrl + Shift + N.", [(n1, "**Thiết bị khuyến nghị:**")])
    add("Khi đăng ký hồ sơ NEU 2026, nên chuẩn bị email thế nào?",
        "Khuyến khích Gmail; chuẩn bị một email chính và một dự phòng để nhận thông tin xử lý hồ sơ.", [(n1, "**Chuẩn bị Email:**")])
    add("Theo thông báo ngày 26/6/2026, NEU kiểm tra và xác thực hồ sơ trước ngày nào?",
        "Trước ngày 01/7/2026.", [(n2, "Đại học tiến hành kiểm tra")])
    add("Theo thông báo 1558, thời gian đăng ký nguyện vọng trên hệ thống Bộ GDĐT năm 2026 là khi nào?",
        "Từ 02/7 đến 17h00 ngày 14/7/2026.", [(n2, "| Đăng ký nguyện vọng trên hệ thống Bộ GDĐT |")], "table")
    add("Thí sinh xét tuyển thẳng vào NEU năm 2026 có cần đăng ký nguyện vọng trên hệ thống Bộ GDĐT không?",
        "Có. Tất cả phương thức, kể cả xét tuyển thẳng, đều phải đăng ký; nguyện vọng trên hệ thống Bộ là căn cứ xét tuyển chính thức.", [(n2, "kể cả xét tuyển thẳng")])
    add("Có được thay đổi thứ tự nguyện vọng so với hồ sơ đã đăng ký tại NEU năm 2026 không?",
        "Có thể thêm, bớt hoặc thay đổi thứ tự nguyện vọng trên hệ thống Bộ GDĐT so với hệ thống NEU.", [(n2, "Thí sinh có thể thêm, bớt")])
    add("Theo thông báo 1558, hạn xác nhận nhập học trên hệ thống Bộ và nhập học tại NEU năm 2026 khác nhau thế nào?",
        "Xác nhận trên hệ thống Bộ trước 17h00 ngày 21/8/2026; nhập học trên hệ thống NEU trước 17h00 ngày 23/8/2026.", [(n2, "| Xác nhận nhập học trên hệ thống Bộ GDĐT |")], "table")
    add("Hướng dẫn công cụ quy đổi điểm NEU 2026 cho nhập những kỳ thi và chứng chỉ nào?",
        "SAT, ACT, HSA, V-ACT, TSA, IELTS, TOEFL iBT hoặc TOEIC; chỉ nhập các mục có điểm.", [(n3, "thí sinh nhập các điểm đang có")])
    add("Các tổ hợp A00, A01, D01 và D07 trên công cụ NEU 2026 gồm môn nào?",
        "A00: Toán, Lý, Hóa; A01: Toán, Lý, Anh; D01: Toán, Văn, Anh; D07: Toán, Hóa, Anh.", [(n3, "Hệ thống tự tính điểm bốn tổ hợp")])
    add("Công cụ NEU dự báo ngành có khả năng trúng tuyển năm 2026 có bảo đảm tôi trúng tuyển không?",
        "Không. Danh sách chỉ để tham khảo khi sắp xếp nguyện vọng, không phải cam kết trúng tuyển.", [(n3, "không phải cam kết trúng tuyển")])
    add("Cần nhập thông tin gì để tra cứu hồ sơ NEU 2026?",
        "Mã hồ sơ và số báo danh hoặc CCCD khớp với dữ liệu đã đăng ký tại https://ai.neu.edu.vn/tuyen-sinh/tools/ho-so.", [(n4, "thí sinh nhập **Mã hồ sơ**")])
    add("Nếu công cụ NEU 2026 báo không tra cứu được hồ sơ thì làm gì?",
        "Kiểm tra lại mã hồ sơ, số báo danh/CCCD hoặc liên hệ hotline tuyển sinh để được hỗ trợ.", [(n4, "Khi gặp thông báo này")])
    add("Theo thông báo 1613 ngày 03/7/2026, ngưỡng đầu vào NEU và điều kiện Toán cho lĩnh vực Pháp luật là gì?",
        "Ngưỡng 22,0/30 cho A00, A01, D01, D07, đã gồm ưu tiên nếu có, áp dụng với phương thức dùng điểm THPT và kết hợp điểm THPT với chứng chỉ tiếng Anh quốc tế. Ngành/chương trình thuộc lĩnh vực Pháp luật cần Toán tối thiểu 6 điểm.",
        [(n5, "| A00: Toán, Vật lý, Hoá học |"), (n5, "Mức điểm này áp dụng"), (n5, "Bên cạnh bảng quy đổi")], "table")
    add("Vì sao hai bài NEU 2026 ghi hạn hồ sơ là 20/6 và 25/6?",
        "Bài hướng dẫn ngày 28/5 ghi đến 17h00 ngày 20/6; bài thông báo ngày 26/6 ghi đã nhận hồ sơ đến 17h00 ngày 25/6. Cần nêu rõ hai thời điểm công bố và đối chiếu thông báo mới hơn; các đoạn này không giải thích nguyên nhân thay đổi.",
        [(n1, "**Thời gian đăng ký hồ sơ:**"), (n2, "Đại học tiến hành kiểm tra")], "temporal_conflict")
    add("Theo tài liệu thông tin tuyển sinh NEU ngày 06/3/2026, mã tuyển sinh là gì?",
        "Mã tuyển sinh là NEU.", [(legal, "2. Mã tuyển sinh: NEU.")])
    add("Theo bảng chứng chỉ trong tài liệu NEU ngày 06/3/2026, IELTS 6.5 quy đổi bao nhiêu điểm?",
        "IELTS 6.5 quy đổi 9.0 điểm trong bảng quy đổi chứng chỉ tiếng Anh; đây không phải toàn bộ điểm xét tuyển.", [(legal, "| 6.5 | 79 - 93 |")], "table")
    add("Theo tài liệu NEU ngày 06/3/2026, xét tuyển kết hợp có nhận chứng chỉ quốc tế thi Home edition không?",
        "Không xét tuyển đối với tất cả chứng chỉ quốc tế có hình thức thi Home edition.", [(legal, "*Lưu ý:* phương thức xét tuyển kết hợp")])
    add("Theo tài liệu NEU ngày 06/3/2026, tổng chỉ tiêu và chỉ tiêu chính quy, liên thông là bao nhiêu?",
        "Tổng 9.000, gồm đại học chính quy 8.780 và liên thông đại học chính quy 220.", [(legal, "### 4.2. Chỉ tiêu tuyển sinh:")])

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "golden_dataset.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fallback = [
        {"id": "CAL-01", "question": "Làm thế nào sửa xe máy không nổ?", "kind": "out_of_domain", "expected_behavior": "Từ chối do ngoài phạm vi tuyển sinh NEU."},
        {"id": "CAL-02", "question": "Điểm chuẩn NEU năm 2030 là bao nhiêu?", "kind": "missing_evidence", "expected_behavior": "Nói corpus 2026 không có thông tin năm 2030; không suy đoán."},
        {"id": "CAL-03", "question": "Tôi đã trúng tuyển NEU chưa?", "kind": "personal_data_unavailable", "expected_behavior": "Không tự tra cứu hoặc kết luận; hướng dẫn cổng tra cứu chính thức."},
        {"id": "CAL-04", "question": "Tôi đã tốt nghiệp cao đẳng, có áp dụng mọi điều kiện của học sinh THPT không?", "kind": "audience_disambiguation", "expected_behavior": "Phân biệt tuyển sinh liên thông cao đẳng với tuyển sinh chính quy; hỏi rõ hình thức dự tuyển."},
        {"id": "CAL-05", "question": "Cho biết điều kiện tuyển sinh NEU", "kind": "underspecified", "expected_behavior": "Hỏi rõ năm, phương thức, đối tượng hoặc nêu rõ phạm vi 2026 trước khi trả lời."},
        {"id": "CAL-06", "question": "Thông tin liên hệ tư vấn tuyển sinh NEU năm 2026?", "kind": "in_domain", "expected_behavior": "Tìm được nguồn, trả lời hotline 0888.128.558 trong giờ hành chính, có citation."},
    ]
    for case in fallback:
        case["split"] = "calibration"
    (OUTPUT / "fallback_dataset.json").write_text(json.dumps(fallback, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(cases)} grounded evaluation cases and {len(fallback)} calibration cases")


if __name__ == "__main__":
    build()
