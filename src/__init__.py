"""Day 8 — RAG Pipeline: tra cứu kiến thức migration lên AWS."""

import sys


def _force_utf8_stdio() -> None:
    """Cho phép print tiếng Việt trên console Windows.

    Console Windows mặc định dùng cp1252, nên mọi print có dấu sẽ raise
    UnicodeEncodeError và làm dừng pipeline giữa đường. Chuyển stdout/stderr sang
    UTF-8 ngay khi import package để các task chạy được bằng `python -m src.taskN`.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


_force_utf8_stdio()
