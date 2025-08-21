from pathlib import Path
from fontTools.ttLib import TTFont
from fontmod.FontEnumerator import _get_ttfont_name


def _get_test_font_path() -> Path:
    paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/system/fonts/NotoSans-Regular.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return Path(path)
    raise FileNotFoundError("No test font found")


def test_get_ttfont_name():
    path = _get_test_font_path()
    if path.suffix.lower() in (".ttc", ".otc"):
        font = TTFont(path, fontNumber=0)
    else:
        font = TTFont(path)
    name = _get_ttfont_name(font)
    assert(name is not None)
