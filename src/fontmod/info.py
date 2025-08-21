from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont, TTLibError


@dataclass(frozen=True)
class FontInfo:
    name: str
    path: Path
    unicode2gid: dict[int, int]
    is_bold: bool
    is_italic: bool
    is_serif: bool

    def contains(self, cp: int) -> bool:
        return cp in self.unicode2gid

    def get_gid(self, cp: int) -> int | None:
        try:
            return self.unicode2gid[cp]
        except KeyError:
            return None

    @classmethod
    def load(cls, path: str | Path) -> "FontInfo":
        info = _load_font_info(path)
        assert info is not None
        return info


def _font_flags(font: TTFont) -> tuple[bool, bool, bool]:
    if "OS/2" not in font:
        return False, False, False
    os2 = font["OS/2"]
    is_bold = os2.usWeightClass >= 500  # type: ignore
    is_italic = os2.fsSelection & 0x1  # type: ignore
    is_serif = os2.fsSelection & 0x2  # type: ignore
    return is_serif, is_italic, is_bold


def _font_name(font: TTFont) -> str | None:
    if "name" not in font:
        return None
    name = font["name"]
    # 优先常见组合 (platformID=3, platEncID=1)，回退到 Unicode(0,3) 或任意可用项
    candidate = name.getName(4, 3, 1) or name.getName(4, 0, 3) or name.getName(4, 0, 4)  # type: ignore
    if candidate is None:
        # 兜底：扫描所有 name 记录，取第一个可转为 Unicode 的
        for rec in name.names:  # type: ignore
            try:
                return rec.toUnicode()
            except Exception:
                continue
        return None
    return candidate.toUnicode()


def _unicode2gid_map(tt: TTFont) -> dict[int, int]:
    cmap = tt.getBestCmap()  # unicode -> glyph
    gmap = tt.getReverseGlyphMap()  # glyph -> gid
    return {unicode: gmap[glyph] for unicode, glyph in cmap.items() if glyph in gmap}


@lru_cache(maxsize=1024)
def _load_font_info(path: str | Path) -> FontInfo | None:
    path = Path(path)
    u2g: dict[int, int] = {}
    try:
        if path.suffix.lower() in {".ttc", ".otc"}:
            # 字体集合：遍历每个 face
            with TTFont(path, fontNumber=0) as tt:  # 先打开以读取 numFonts
                name = _font_name(tt)
                assert name is not None
                numFonts = tt.reader.numFonts  # type: ignore
                serif, italic, bold = _font_flags(tt)
            for idx in range(numFonts):
                with TTFont(path, fontNumber=idx, lazy=True) as tt:
                    u2g.update(_unicode2gid_map(tt))
        else:
            with TTFont(path, lazy=True) as tt:
                name = _font_name(tt)
                assert name is not None
                serif, italic, bold = _font_flags(tt)
                u2g = _unicode2gid_map(tt)
    except TTLibError:
        return None
    except Exception:
        return None
    return FontInfo(
        name=name,
        path=path,
        unicode2gid=u2g,
        is_serif=serif,
        is_italic=italic,
        is_bold=bold,
    )
