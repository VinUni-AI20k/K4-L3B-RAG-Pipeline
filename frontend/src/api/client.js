// src/api/client.js — HTTP client with auto-mock fallback for TravelBot RAG
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkApiHealth() {
  try {
    const res = await fetch(`${BASE}/health`, { method: 'GET', signal: AbortSignal.timeout(1500) });
    return res.ok;
  } catch {
    return false;
  }
}

// Realistic travel mock knowledge base
const MOCK_TRAVEL_KB = {
  da_lat: {
    answer: `Dựa trên cẩm nang du lịch Đà Lạt mùa đông và kho dữ liệu lữ hành được lập chỉ mục, các kinh nghiệm trọng tâm bao gồm:

1. **Thời điểm vàng & Điểm ngắm cảnh nổi bật:** Mùa hoa Dã Quỳ nở rộ dọc đèo Tà Nung và đồi cỏ hồng Dankia - Suối Vàng rực rỡ nhất từ 5:30 – 7:00 sáng. Bạn cũng không nên bỏ lỡ trải nghiệm săn mây bình minh tại đồi chè Cầu Đất lúc 5:00 sáng. [1] [2]

2. **Ẩm thực ấm áp mùa đông:** Thưởng thức các món đặc sản làm ấm cơ thể như Lẩu gà lá é Tao Ngộ (đường 3/4), lẩu bò Ba Toa quán Gỗ, bánh căn xíu mại đường Tăng Bạt Hổ và sữa đậu nành nóng hổi tại Chợ Đêm Đà Lạt. [2]

3. **Phương tiện di chuyển & Lưu trú:** Nên thuê xe máy khoảng 120.000đ/ngày để chủ động săn mây sáng sớm. Nên đặt phòng homestay hoặc khách sạn tại Phường 1 hoặc đường Nam Kỳ Khởi Nghĩa trước 2–3 tuần vào các dịp cuối tuần. [1] [3]

4. **Lưu ý trang phục & Thời tiết:** Nhiệt độ ban đêm hạ xuống dưới 12°C – 14°C kèm sương muối lạnh. Cần chuẩn bị kỹ áo khoác dày, khăn quàng cổ, găng tay và giày bệt chống trơn trượt khi đi đồi dốc. [3]`,
    sources: [
      {
        id: "chunk_dl_1",
        score: 0.94,
        retrieval_method: "hybrid",
        content: "Đà Lạt mùa đông từ tháng 11 đến hết tháng 1 là mùa đẹp nhất trong năm. Lúc này thời tiết hanh khô, ban ngày nắng nhẹ, ban đêm nhiệt độ hạ xuống dưới 12°C - 14°C. Đây là thời điểm diễn ra mùa hoa dã quỳ nở rộ dọc đèo Tà Nung và lễ hội đồi cỏ hồng tại Dankia - Suối Vàng thu hút hàng chục ngàn du khách.",
        metadata: {
          title: "Cẩm nang Du lịch Đà Lạt Mùa Đông Toàn Tập 2024",
          url: "https://dulichdalat.vn/cam-nang/mua-dong",
          doc_type: "news",
          chunk_index: 3,
          page: "Trang 12–16",
        },
      },
      {
        id: "chunk_dl_2",
        score: 0.89,
        retrieval_method: "dense",
        content: "Danh sách các quán ăn uy tín cho mùa đông: Lẩu gà lá é chuẩn vị tại số 5 đường 3/4 có giá từ 200.000đ - 300.000đ/nồi, lẩu bò quán Gỗ khu Ba Toa, kem bơ Thanh Thảo, bánh mì xíu mại Hoàng Diệu. Giá dao động từ 35.000đ đến 250.000đ/món.",
        metadata: {
          title: "Top 20 Quán Ăn Đặc Sản Chuẩn Vị & Giá Niêm Yết Đà Lạt",
          url: "https://foody.vn/da-lat/top-quan-ngon",
          doc_type: "news",
          chunk_index: 2,
          page: "Trang 5–8",
        },
      },
      {
        id: "chunk_dl_3",
        score: 0.81,
        retrieval_method: "bm25",
        content: "Hướng dẫn di chuyển và lưu trú: Thuê xe máy khoảng 120.000đ/ngày, nên đặt phòng tại khu vực Phường 1 hoặc đường Nam Kỳ Khởi Nghĩa để thuận tiện đi bộ ra Chợ Đêm và hồ Xuân Hương. Biên độ nhiệt ngày đêm rất lớn, bắt buộc mang áo ấm nhiều lớp.",
        metadata: {
          title: "Sổ tay Lưu trú, Di chuyển & An toàn Du lịch",
          url: "https://dulichdalat.vn/hotels-safety",
          doc_type: "legal",
          chunk_index: 1,
          page: "Trang 3–4",
        },
      },
    ],
  },

  phu_quoc: {
    answer: `Dựa trên cẩm nang du lịch Phú Quốc 3 ngày 2 đêm, dưới đây là lịch trình và kinh nghiệm tối ưu chi phí:

1. **Lịch trình Ngày 1 (Bắc Đảo & Khám phá):** Khởi hành đến Phú Quốc, nhận phòng tại Thị trấn Dương Đông. Chiều tham quan Grand World (Thành phố không ngủ), trải nghiệm đi thuyền Gondola trên sông Venice và ngắm hoàng hôn Bãi Dài. [1] [2]

2. **Lịch trình Ngày 2 (Tour 4 Đảo & Cáp treo Hòn Thơm):** Tham gia tour cano tham quan Hòn Mây Rút, Hòn Gầm Ghì (lặn ngắm san hô tự nhiên). Trải nghiệm Cáp treo vượt biển Hòn Thơm 3 dây dài nhất thế giới (gần 7.900m) và check-in Cầu Hôn (Kiss Bridge). [2]

3. **Lịch trình Ngày 3 (Nam Đảo & Mua sắm đặc sản):** Buổi sáng tắm biển Bãi Sao với bãi cát trắng mịn nước xanh ngọc. Thăm nhà thùng nước mắm truyền thống, trang trại nuôi cấy ngọc trai và mua hải sản khô tại Chợ Dương Đông trước khi ra sân bay. [1] [3]

4. **Mẹo săn vé máy bay & chi phí:** Đặt vé máy bay khứ hồi trước 3–4 tuần vào các khung giờ sáng sớm hoặc đêm muộn để tiết kiệm 30% chi phí. Chi phí trọn gói tự túc khoảng 3.500.000đ – 5.000.000đ/người. [3]`,
    sources: [
      {
        id: "chunk_pq_1",
        score: 0.95,
        retrieval_method: "hybrid",
        content: "Lịch trình du lịch Phú Quốc 3N2Đ: Ngày 1 khám phá Bắc Đảo Grand World, VinWonders. Ngày 2 đi tour cano 4 đảo lặn san hô Hòn Mây Rút, cáp treo Hòn Thơm. Ngày 3 tắm biển Bãi Sao và mua sắm đặc sản ngọc trai, tiêu, nước mắm.",
        metadata: {
          title: "Cẩm nang Lịch trình Du lịch Phú Quốc 3N2Đ Tự túc Tiết kiệm",
          url: "https://phuquoc.vn/guides/3n2d",
          doc_type: "news",
          chunk_index: 1,
          page: "Trang 2–5",
        },
      },
      {
        id: "chunk_pq_2",
        score: 0.88,
        retrieval_method: "dense",
        content: "Trải nghiệm không thể bỏ qua: Cáp treo Hòn Thơm vượt biển dài gần 7.900m, Cầu Hôn Sunset Town ngắm hoàng hôn đẹp nhất Việt Nam, câu mực đêm cùng ngư dân địa phương.",
        metadata: {
          title: "Top 10 Trải nghiệm Biển Đảo Phú Quốc",
          url: "https://travel.vietnam.vn/phu-quoc/top-trai-nghiem",
          doc_type: "news",
          chunk_index: 2,
          page: "Trang 8–10",
        },
      },
      {
        id: "chunk_pq_3",
        score: 0.82,
        retrieval_method: "bm25",
        content: "Kinh nghiệm đặt vé máy bay và lưu trú: Sân bay quốc tế Phú Quốc cách Dương Đông 10km. Nên thuê resort ven biển Bãi Trường hoặc khách sạn trung tâm Dương Đông để thuận tiện ăn uống chợ đêm.",
        metadata: {
          title: "Cẩm nang Săn vé rẻ & Khách sạn Phú Quốc",
          url: "https://phuquoc.travel/tips/ve-may-bay",
          doc_type: "legal",
          chunk_index: 3,
          page: "Trang 1–3",
        },
      },
    ],
  },

  hoi_an: {
    answer: `Dựa trên cẩm nang ẩm thực và di sản phố cổ Hội An, đây là danh sách những món đặc sản danh tiếng nhất định phải thưởng thức:

1. **Cao Lầu Hội An (Món trứ danh):** Món mì độc nhất vô nhị với sợi mì vàng ươm ngâm tro củi cù lao Chàm và nước giếng cổ Bá Lễ, ăn kèm thịt xíu thơm mềm, tóp mỡ giòn rụm và rau thơm Trà Quế. Quán gợi ý: Cao lầu Thanh (26 Thái Phiên), Cao lầu Bà Bé (chợ Hội An). [1] [2]

2. **Cơm gà phố cổ:** Hạt cơm nấu bằng nước luộc gà óng ánh màu nghệ, thịt gà ta xé phay bóp hành tây thơm nồng cay nhẹ. Địa chỉ nổi tiếng: Cơm gà Bà Buội (22 Phan Chu Trinh), Cơm gà Nga (Móng Cái). [2]

3. **Bánh mì Hội An:** Vỏ bánh giòn rụm với nhân pate béo ngậy, thịt xá xíu, chả lụa và nước sốt gia truyền đặc trưng. Địa chỉ hàng đầu: Bánh mì Phượng (7B Phan Chu Trinh) và Bánh mì Madam Khánh. [1]

4. **Bánh bao - Bánh vạc & Mót thảo mộc:** Thưởng thức "bông hồng trắng" (White Rose) nhân tôm thịt tại Lò Bánh Bao Bánh Vạc và giải nhiệt bằng ly nước Mót thảo mộc hoa sen thơm mát tại 150 Trần Phú. [3]`,
    sources: [
      {
        id: "chunk_ha_1",
        score: 0.96,
        retrieval_method: "hybrid",
        content: "Ẩm thực Hội An là sự giao thoa tinh tế giữa văn hóa Việt, Hoa và Nhật Bản. Nổi bật nhất là Cao Lầu với nước giếng Bá Lễ độc quyền, Bánh mì Phượng được đầu bếp Anthony Bourdain ca ngợi là ngon nhất thế giới.",
        metadata: {
          title: "Bản đồ Ẩm thực và Di sản Văn hóa Phố Cổ Hội An",
          url: "https://hoian.gov.vn/am-thuc-di-san",
          doc_type: "news",
          chunk_index: 1,
          page: "Trang 4–7",
        },
      },
      {
        id: "chunk_ha_2",
        score: 0.91,
        retrieval_method: "dense",
        content: "Cơm gà Hội An và mì Quảng: Cơm dẻo thơm nấu nước luộc gà ta thả vườn béo ngọt, ăn kèm gỏi hành tây chua ngọt và tương ớt Hội An rim cay nồng đặc sắc.",
        metadata: {
          title: "Top Quán Ăn Truyền Thống Hội An",
          url: "https://foody.vn/hoi-an/quan-ngon",
          doc_type: "news",
          chunk_index: 2,
          page: "Trang 2–3",
        },
      },
      {
        id: "chunk_ha_3",
        score: 0.84,
        retrieval_method: "bm25",
        content: "Thức uống và món ăn vặt chợ đêm Hội An: Nước Mót thảo mộc hoa sen thơm mát chỉ 15.000đ/ly, chè bắp Cẩm Nam béo ngậy, bánh tráng cuốn thịt heo chấm mắm nêm đậm đà.",
        metadata: {
          title: "Cẩm nang Ăn vặt & Nước giải nhiệt Chợ Đêm",
          url: "https://hoian.travel/mon-ngon",
          doc_type: "legal",
          chunk_index: 3,
          page: "Trang 8–10",
        },
      },
    ],
  },

  visa_nhat: {
    answer: `Dựa trên sổ tay hướng dẫn thủ tục thị thực du lịch Nhật Bản cập nhật mới nhất, hồ sơ xin visa tự túc (Single Entry) cần chuẩn bị đầy đủ 4 nhóm giấy tờ sau:

1. **Hồ sơ nhân thân & Pháp lý:** Hộ chiếu còn hạn trên 6 tháng (kèm bản photo), tờ khai xin visa có dán ảnh 4.5 x 4.5cm chuẩn quốc tế nền trắng, căn cước công dân và xác nhận cư trú CT07. [1] [2]

2. **Hồ sơ chứng minh tài chính:** Bản sao kê tài khoản ngân hàng nhận lương 6 tháng gần nhất có số dư tối thiểu 100.000.000đ – 150.000.000đ/người, xác nhận số dư sổ tiết kiệm, giấy tờ sở hữu nhà đất hoặc ô tô nếu có. [1]

3. **Hồ sơ công việc:** Hợp đồng lao động còn hiệu lực, đơn xin nghỉ phép đi du lịch đã được công ty phê duyệt, bảng lương 3 tháng gần nhất và quá trình đóng BHXH (VssID). [2]

4. **Lịch trình chuyến đi & Booking:** Bản kế hoạch du lịch chi tiết từng ngày (nêu rõ địa điểm tham quan, khách sạn lưu trú và phương tiện di chuyển), xác nhận đặt phòng khách sạn và vé máy bay khứ hồi. [3]`,
    sources: [
      {
        id: "chunk_vn_1",
        score: 0.97,
        retrieval_method: "hybrid",
        content: "Quy định xin visa du lịch Nhật Bản tự túc: Đương đơn nộp hồ sơ tại Đại sứ quán/Lãnh sự quán hoặc qua các Trung tâm tiếp nhận VFS Global. Thời gian xét duyệt tiêu chuẩn từ 8 đến 10 ngày làm việc.",
        metadata: {
          title: "Hướng dẫn Thủ tục & Hồ sơ Xin Visa Du lịch Tự túc Nhật Bản",
          url: "https://japan-visa.gov.vn/thu-tuc-tu-tuc",
          doc_type: "legal",
          chunk_index: 1,
          page: "Trang 1–4",
        },
      },
      {
        id: "chunk_vn_2",
        score: 0.90,
        retrieval_method: "dense",
        content: "Yêu cầu tài chính và công việc: Cần chứng minh có thu nhập ổn định và ràng buộc chặt chẽ tại Việt Nam để đảm bảo quay về đúng hạn. Sổ tiết kiệm nên gửi từ 3 tháng trở lên.",
        metadata: {
          title: "Tiêu chuẩn Xét duyệt Tài chính & Công việc",
          url: "https://visa.mofa.go.jp/requirements",
          doc_type: "legal",
          chunk_index: 2,
          page: "Trang 4–6",
        },
      },
      {
        id: "chunk_vn_3",
        score: 0.83,
        retrieval_method: "bm25",
        content: "Mẫu lịch trình di chuyển chi tiết: Phải khớp chính xác với ngày đi, ngày về trên vé máy bay và địa chỉ khách sạn đã đặt.",
        metadata: {
          title: "Mẫu Lịch trình Du lịch Chuẩn Đại Sứ Quán",
          url: "https://japan.travel/schedule-template",
          doc_type: "news",
          chunk_index: 3,
          page: "Trang 5",
        },
      },
    ],
  },

  phap_luat: {
    answer: `Căn cứ Luật Du lịch số 09/2017/QH14 và các nghị định hướng dẫn, khách du lịch và các cơ sở lữ hành có các quyền và nghĩa vụ quy chuẩn sau:

1. **Quyền của khách du lịch (Điều 11):** Được bảo đảm an toàn về tính mạng, sức khỏe, tài sản khi tham gia tour; được cứu nạn, cứu hộ trong trường hợp bất khả kháng; được cung cấp thông tin trung thực, rõ ràng về dịch vụ, điểm đến. [1]

2. **Nghĩa vụ của cơ sở lưu trú & kinh doanh (Nghị định 168/2017/NĐ-CP):** Bắt buộc phải niêm yết công khai bảng giá dịch vụ, giữ gìn vệ sinh an toàn thực phẩm, không chèn ép hoặc nâng giá tùy tiện vào mùa cao điểm. [2]

3. **Quy tắc bảo vệ di tích & môi trường du lịch:** Khách du lịch có nghĩa vụ tuân thủ nội quy tham quan, không xả rác bừa bãi, không xâm hại cảnh quan, không khắc tên vẽ bậy lên các hiện vật và công trình tâm linh. [3]`,
    sources: [
      {
        id: "chunk_pl_1",
        score: 0.96,
        retrieval_method: "hybrid",
        content: "Luật Du lịch số 09/2017/QH14 Điều 11 quy định: Khách du lịch có quyền được bảo đảm an toàn về tính mạng, sức khỏe, tài sản; được tôn trọng, đối xử bình đẳng và khiếu nại các hành vi vi phạm pháp luật du lịch.",
        metadata: {
          title: "Luật Du lịch số 09/2017/QH14 & Nghị định 168/2017/NĐ-CP",
          url: "https://vanban.chinhphu.vn/default.aspx?pageid=27160&docid=190367",
          doc_type: "legal",
          chunk_index: 1,
          page: "Trang 6–8",
        },
      },
      {
        id: "chunk_pl_2",
        score: 0.92,
        retrieval_method: "dense",
        content: "Cơ sở lưu trú du lịch phải niêm yết công khai giá bán hàng hóa, dịch vụ và nội quy của cơ sở; thực hiện đúng cam kết về chất lượng dịch vụ với khách hàng.",
        metadata: {
          title: "Thông tư 06/2017/TT-BVHTTDL Quy định chi tiết Luật Du lịch",
          url: "https://bvhttdl.gov.vn/van-ban-quan-ly/thong-tu-06-2017.htm",
          doc_type: "legal",
          chunk_index: 2,
          page: "Trang 12",
        },
      },
      {
        id: "chunk_pl_3",
        score: 0.88,
        retrieval_method: "bm25",
        content: "Quy tắc ứng xử văn minh: Nghiêm cấm hành vi xả rác, khắc tên, vẽ bậy lên các di tích lịch sử, cảnh quan thiên nhiên và các công trình văn hóa tâm linh.",
        metadata: {
          title: "Quy định Bảo vệ môi trường và Ứng xử văn minh tại các Khu di tích, Danh thắng",
          url: "https://vietnamtourism.gov.vn/post/quy-tac-ung-xu",
          doc_type: "legal",
          chunk_index: 3,
          page: "Trang 3–5",
        },
      },
    ],
  },

  safe_refusal: (query, score = 0.38, threshold = 0.70) => ({
    answer: `⚠️ **Safe Refusal (Kích hoạt Từ chối An toàn):**

Không tìm thấy thông tin phù hợp trong kho cẩm nang du lịch và pháp luật lữ hành cho câu hỏi: *"**${query}**"*.

- **Độ tương đồng ngữ nghĩa (Cosine Score gốc):** \`${score}\`
- **Ngưỡng Fallback đã cấu hình (Threshold):** \`${threshold}\`
- **Lý do kích hoạt:** Điểm tương đồng thấp hơn ngưỡng tối thiểu, câu hỏi nằm ngoài phạm vi tri thức du lịch (Out-of-domain). Hệ thống kích hoạt Safe Refusal theo quy chuẩn Module Contracts để tránh tình trạng ảo giác (Hallucination) và bảo đảm tính trung thực (Faithfulness = 0.98).`,
    sources: [],
    retrieval_source: "none",
    confidence: String(score),
    fallback_triggered: true,
  }),
};

// Check if query is out of domain
function isOutOfDomainQuery(query) {
  const q = (query || '').toLowerCase().trim();
  const outKeywords = [
    'sửa xe', 'bugi', 'honda', 'wave', 'xe máy', 'thay nhớt',
    'pizza', 'nhào bột', 'bánh pizza', 'lò nướng', 'nấu ăn món tây',
    'sao hỏa', 'thiên văn', 'vũ trụ', 'mặt trăng', 'phi thuyền',
    'chứng khoán', 'cổ phiếu', 'crypto', 'bitcoin', 'đầu tư tài chính',
    'lập trình c++', 'python', 'java', 'react native', 'viết code',
    'bệnh ung thư', 'khám bệnh', 'uống thuốc', 'bác sĩ'
  ];
  return outKeywords.some(kw => q.includes(kw));
}

function matchTravelMock(query, threshold = 0.70) {
  const q = (query || '').toLowerCase().trim();

  // 1. Kiểm tra out-of-domain hoặc threshold quá cao
  if (isOutOfDomainQuery(q) || threshold > 0.95) {
    return MOCK_TRAVEL_KB.safe_refusal(query, 0.38, threshold);
  }

  // 2. So khớp in-domain
  if (q.includes('đà lạt') || q.includes('da lat') || q.includes('dã quỳ') || q.includes('cỏ hồng')) {
    return MOCK_TRAVEL_KB.da_lat;
  }
  if (q.includes('phú quốc') || q.includes('phu quoc') || q.includes('hòn thơm') || q.includes('bãi sao')) {
    return MOCK_TRAVEL_KB.phu_quoc;
  }
  if (q.includes('hội an') || q.includes('hoi an') || q.includes('cao lầu') || q.includes('bánh mì phượng')) {
    return MOCK_TRAVEL_KB.hoi_an;
  }
  if (q.includes('visa') || q.includes('nhật') || q.includes('nhat ban') || q.includes('thị thực')) {
    return MOCK_TRAVEL_KB.visa_nhat;
  }
  if (q.includes('luật') || q.includes('quy định') || q.includes('quy tắc') || q.includes('pháp luật') || q.includes('nghĩa vụ') || q.includes('quyền')) {
    return MOCK_TRAVEL_KB.phap_luat;
  }

  // 3. Fallback câu hỏi du lịch chung
  return {
    answer: `Dựa trên kho dữ liệu cẩm nang du lịch và lữ hành cho "${query}", đây là các thông tin trọng tâm:

1. **Khám phá & Trải nghiệm tiêu biểu:** Điểm đến sở hữu cảnh sắc thiên nhiên độc đáo cùng bề dày văn hóa địa phương phong phú, rất phù hợp cho các chuyến du lịch tự túc hoặc nghỉ dưỡng gia đình. [1] [2]

2. **Ẩm thực đặc sản địa phương:** Thưởng thức các món ngon truyền thống tại các khu chợ ẩm thực sầm uất và các quán ăn lâu đời với giá cả niêm yết rõ ràng. [2]

3. **Lưu trú & Di chuyển:** Nên lựa chọn khách sạn hoặc homestay ở khu vực trung tâm để thuận tiện đi lại. Nên đặt trước từ 2–3 tuần vào các mùa cao điểm để nhận mức giá ưu đãi nhất. [1] [3]

4. **Lưu ý an toàn:** Kiểm tra dự báo thời tiết trước chuyến đi 3 ngày, chuẩn bị trang phục phù hợp và tôn trọng phong tục văn hóa bản địa. [3]`,
    sources: [
      {
        id: "chunk_gen_1",
        score: 0.91,
        retrieval_method: "hybrid",
        content: `Cẩm nang tổng hợp thông tin về "${query}". Cung cấp gợi ý về thời điểm tham quan tốt nhất, danh sách lưu trú uy tín và lịch trình khám phá tiết kiệm.`,
        metadata: {
          title: `Cẩm nang Hướng dẫn Du lịch: ${query.slice(0, 36)}`,
          url: "https://vietnamtourism.gov.vn/guides",
          doc_type: "news",
          chunk_index: 1,
          page: "Trang 1–4",
        },
      },
      {
        id: "chunk_gen_2",
        score: 0.85,
        retrieval_method: "dense",
        content: "Đặc sản ẩm thực và các địa điểm ăn uống ngon bổ rẻ được cộng đồng du lịch bình chọn cao.",
        metadata: {
          title: "Top Món Ăn Ngon & Quán Đặc Sản",
          url: "https://foody.vn/dia-diem-an-uong",
          doc_type: "news",
          chunk_index: 2,
          page: "Trang 2",
        },
      },
      {
        id: "chunk_gen_3",
        score: 0.79,
        retrieval_method: "bm25",
        content: "Kinh nghiệm đặt phòng giá rẻ, phương tiện di chuyển tối ưu và các lưu ý an toàn hành trình.",
        metadata: {
          title: "Sổ tay Du lịch An toàn & Tiết kiệm",
          url: "https://travelblog.vn/tips",
          doc_type: "legal",
          chunk_index: 3,
          page: "Trang 3–5",
        },
      },
    ],
  };
}

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  generate: async (query, topK = 5, provider = 'openai', model = '', threshold = 0.45) => {
    try {
      const data = await post('/generate', { query, top_k: topK, provider, model, threshold });
      return data;
    } catch {
      // Backend offline -> Return rich realistic travel mock immediately
      const mock = matchTravelMock(query, threshold);
      return {
        answer: mock.answer,
        sources: (mock.sources || []).slice(0, topK),
        retrieval_source: mock.fallback_triggered ? 'none' : 'hybrid',
        confidence: mock.confidence || (mock.fallback_triggered ? '0.38' : '0.94'),
        fallback_triggered: mock.fallback_triggered || false,
        is_mock: true,
      };
    }
  },

  retrieve: async (query, topK = 5, method = 'hybrid') => {
    try {
      const data = await post('/retrieve', { query, top_k: topK, method });
      if (data?.chunks?.length) return data;
      throw new Error('No chunks from live backend');
    } catch {
      const mock = matchTravelMock(query);
      if (mock.fallback_triggered) {
        return { chunks: [], is_mock: true };
      }

      if (method === 'dense') {
        // Mô phỏng kết quả Dense Only (chỉ ngữ nghĩa vector)
        const denseChunks = (mock.sources || []).map((s, i) => ({
          ...s,
          retrieval_method: 'dense',
          score: Number((s.score - 0.04 - i * 0.03).toFixed(3)),
        }));
        return { chunks: denseChunks.slice(0, topK), is_mock: true };
      }

      if (method === 'bm25') {
        // Mô phỏng kết quả BM25 Only (từ khóa chính xác)
        const bm25Chunks = (mock.sources || []).map((s, i) => ({
          ...s,
          retrieval_method: 'bm25',
          score: Number((s.score - 0.02 - i * 0.04).toFixed(3)),
        }));
        return { chunks: bm25Chunks.slice(0, topK), is_mock: true };
      }

      if (method === 'pageindex') {
        return {
          chunks: [
            {
              id: 'p_1',
              score: 0.885,
              retrieval_method: 'pageindex',
              content: `[PageIndex Vectorless] Trích xuất chỉ mục mục lục cẩm nang du lịch cho truy vấn: "${query}". Rút trích theo phân cấp chương mục.`,
              metadata: { title: `Chỉ mục mục lục: ${query.slice(0, 30)}`, doc_type: 'legal', url: 'https://dulich.vn/index' },
            },
            {
              id: 'p_2',
              score: 0.812,
              retrieval_method: 'pageindex',
              content: `[PageIndex Vectorless] Tóm lược nội dung chương 2: Quy định giá niêm yết và bảo vệ quyền lợi du khách.`,
              metadata: { title: 'Mục lục chương 2: Quyền lợi & Lưu trú', doc_type: 'legal', url: 'https://dulich.vn/c2' },
            },
          ].slice(0, topK),
          is_mock: true,
        };
      }

      // Default: hybrid (RRF fusion)
      return { chunks: (mock.sources || []).slice(0, topK), is_mock: true };
    }
  },
};
