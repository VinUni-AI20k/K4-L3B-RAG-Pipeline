from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parent.parent / "app.py"


def test_app_renders_household_tax_portal():
    """Màn hình ban đầu hiển thị luồng hỏi đáp thuế và các điều khiển cần thiết."""
    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert app.title[0].value == "Thuế & Kê khai Hộ Kinh Doanh"
    assert app.slider[0].label == "Số nguồn tham khảo"
    assert app.chat_input[0].placeholder == "Hãy nhập câu hỏi của bạn..."
    assert len(app.button) == 6


def test_app_renders_government_rag_portal_sections():
    """Portal làm rõ nguồn chính thức, danh mục tri thức và năng lực RAG."""
    app = AppTest.from_file(str(APP_PATH)).run()

    rendered_copy = " ".join(element.value for element in app.markdown)

    assert not app.exception
    assert "Trợ lý Tra cứu Thông tin Chính thức" in rendered_copy
    assert "Thủ tục hành chính" in rendered_copy
    assert "Tra cứu chính xác theo tài liệu gốc" in rendered_copy
    assert "Nguồn chính thức" in rendered_copy
    assert app.chat_input[0].placeholder == "Hãy nhập câu hỏi của bạn..."
    assert len(app.button) == 6


def test_hero_guides_people_to_the_real_chat_input():
    """Hero không được giả làm ô nhập; người dùng phải thấy nơi nhập thật."""
    app = AppTest.from_file(str(APP_PATH)).run()

    rendered_copy = " ".join(element.value for element in app.markdown)

    assert "Nhập câu hỏi tại thanh tra cứu ở cuối trang" in rendered_copy
    assert app.chat_input[0].placeholder == "Hãy nhập câu hỏi của bạn..."


def test_app_uses_compact_initial_portal_layout():
    """Màn hình ban đầu ưu tiên tra cứu, không giữ khoảng trống landing page lớn."""
    app = AppTest.from_file(str(APP_PATH)).run()

    theme = app.markdown[0].value

    assert "min-height:420px" not in theme
    assert "min-height:220px" in theme
    assert "min-height:104px" in theme


def test_hero_copy_stays_inside_navy_panel():
    """Nội dung hero không tràn sang vùng màu be ở desktop."""
    app = AppTest.from_file(str(APP_PATH)).run()

    theme = app.markdown[0].value

    assert "box-sizing:border-box" in theme
    assert "width:58%" in theme
