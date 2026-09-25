from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parent.parent / "app.py"


def test_app_renders_household_tax_portal():
    """Màn hình ban đầu hiển thị luồng hỏi đáp thuế và các điều khiển cần thiết."""
    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert app.title[0].value == "Thuế & Kê khai Hộ Kinh Doanh"
    assert app.slider[0].label == "Số nguồn tham khảo"
    assert app.chat_input[0].placeholder == "Nhập câu hỏi về thuế và kê khai..."
    assert len(app.button) == 3
