from functools import lru_cache
import itertools
import logging
from dataclasses import dataclass
from pathlib import Path

from fontmod.context import FontContext
from fontmod.info import FontInfo


@dataclass(frozen=True)
class _Entry:
    fontname: str
    filename: str


_font2file = {
    "Segoe UI": "segoeui.ttf",
    "Segoe UI Bold": "segoeuib.ttf",
    "Segoe UI Italic": "segoeuii.ttf",
    "Segoe UI Bold Italic": "segoeuiz.ttf",
    "Arial": "arial.ttf",
    "Arial Bold": "arialbd.ttf",
    "Arial Italic": "ariali.ttf",
    "Arial Bold Italic": "arialbi.ttf",
    "Calibri": "calibri.ttf",
    "Calibri Bold": "calibrib.ttf",
    "Calibri Italic": "calibrii.ttf",
    "Calibri Bold Italic": "calibriz.ttf",
    "Verdana": "verdana.ttf",
    "Verdana Bold": "verdanab.ttf",
    "Verdana Italic": "verdanai.ttf",
    "Verdana Bold Italic": "verdanaz.ttf",
    "Georgia": "georgia.ttf",
    "Georgia Bold": "georgiab.ttf",
    "Georgia Italic": "georgiai.ttf",
    "Georgia Bold Italic": "georgiaz.ttf",
    "Times New Roman": "times.ttf",
    "Times New Roman Bold": "timesbd.ttf",
    "Times New Roman Italic": "timesi.ttf",
    "Times New Roman Bold Italic": "timesbi.ttf",
    "Cambria": "cambria.ttc",
    "Cambria Bold": "cambriab.ttf",
    "Cambria Italic": "cambriai.ttf",
    "Cambria Bold Italic": "cambriaz.ttf",
    "Cambria Math": "cambria.ttc",
    "Noto Sans Regular": "NotoSans-Regular.ttf",
    "Noto Sans Arabic Regular": "NotoSansArabic-Regular.ttf",
    "Noto Naskh Arabic Regular": "NotoNaskhArabic-Regular.ttf",
    "Scheherazade": "Scheherazade-Regular.ttf",
    "Dubai Regular": "DUBAI-REGULAR.TTF",
    "Noto Sans Hebrew Regular": "NotoSansHebrew-Regular.ttf",
    "Noto Serif Hebrew Regular": "NotoSerifHebrew-Regular.ttf",
    "Frank Ruehl CLM Medium": "FrankRuehlCLM-Medium.otf",
    "David Libre Regular": "DavidLibre-Regular.ttf",
    "Nirmala": "Nirmala.ttc",
    "Leelawadee UI": "LeelawUI.ttf",
    "Leelawadee UI Bold": "LeelaUIb.ttf",
    "Noto Sans Lao Regular": "NotoSansLao-Regular.ttf",
    "Microsoft Himalaya": "himalaya.ttf",
    "Myanmar Text": "mmrtext.ttf",
    "Myanmar Text Bold": "mmrtextb.ttf",
    "Noto Serif Armenian Regular": "NotoSerifArmenian-Regular.ttf",
    "Noto Sans Armenian Regular": "NotoSansArmenian-Regular.ttf",
    "Noto Serif Georgian Regular": "NotoSerifGeorgian-Regular.ttf",
    "Noto Sans Georgian Regular": "NotoSansGeorgian-Regular.ttf",
    "Malgun Gothic": "malgun.ttf",
    "Malgun Gothic Bold": "malgunbd.ttf",
    "YuGothB": "YuGothB.ttc",
    "YuGothR": "YuGothR.ttc",
    "Segoe UI Symbol": "seguisym.ttf",
    "Segoe UI Emoji": "seguiemj.ttf",
    "Segoe UI Historic": "seguihis.ttf",
    "Symbol": "symbol.ttf",
    "msyh": "msyh.ttc",
    "msyhbd": "msyhbd.ttc",
    "simsun": "simsun.ttc",
    "msjh": "msjh.ttc",
    "msjhbd": "msjhbd.ttc",
    "mingliub": "mingliub.ttc",
}


_font_dirs = [Path("C:/Windows/Fonts")]


def _font_files(paths: list[Path]):
    return itertools.chain.from_iterable(path.rglob("*") for path in paths)


@lru_cache(maxsize=1024)
def _load_font(fontname: str):
    if not fontname:
        return None

    try:
        filename = _font2file[fontname]
    except KeyError:
        return None

    paths = (path for path in _font_files(_font_dirs) if filename == path.name)
    return next(paths, None)

def _load_family(base: str, bold: bool = False, italic: bool = False):
    if not base:
        return None

    font = None

    if bold and italic:
        font = _load_font(f"{base} Bold Italic")

    elif bold:
        font = _load_font(f"{base} Bold")

    elif italic:
        font = _load_font(f"{base} Italic")

    return font or _load_font(base)


def _load_families(names: list[str], bold: bool = False, italic: bool = False):
    if not names:
        return None

    for name in names:
        font = _load_family(name, bold, italic)
        if font:
            return font

    return None


def load_system_boxes_font(ctx: FontContext):
    if ctx.boxes is not None:
        return ctx.boxes

    path = _load_families(["Segoe UI Symbol"], False, False)
    if path is None:
        return None

    try:
        ctx.boxes = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for boxes")
        return ctx.boxes
    except Exception:
        logging.warning(f"Failed to load font {path} for boxes")
        return None


def load_system_emoji_font(ctx: FontContext):
    if ctx.emoji is not None:
        return ctx.emoji

    path = _load_families(["Segoe UI Emoji"], False, False)
    if path is None:
        return None

    try:
        ctx.emoji = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for emoji")
        return ctx.emoji
    except Exception:
        logging.warning(f"Failed to load font {path} for emoji")
        return None


def load_system_math_font(ctx: FontContext):
    if ctx.math is not None:
        return ctx.math

    path = _load_families(["Cambria Math", "Cambria"], False, False)
    if path is None:
        return None

    try:
        ctx.math = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for math")
        return ctx.math
    except Exception:
        logging.warning(f"Failed to load font {path} for math")
        return None


def load_system_music_font(ctx: FontContext):
    if ctx.music is not None:
        return ctx.music

    path = _load_families(["Segoe UI Symbol"], False, False)
    if path is None:
        return None

    try:
        ctx.music = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for music")
        return ctx.music
    except Exception:
        logging.warning(f"Failed to load font {path} for music")
        return None


def load_system_symbol1_font(ctx: FontContext):
    if ctx.symbol1 is not None:
        return ctx.symbol1

    path = _load_families(["Segoe UI Symbol", "Symbol"], False, False)
    if path is None:
        return None

    try:
        ctx.symbol1 = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for symbol1")
        return ctx.symbol1
    except Exception:
        logging.warning(f"Failed to load font {path} for symbol1")
        return None


def load_system_symbol2_font(ctx: FontContext):
    if ctx.symbol2 is not None:
        return ctx.symbol2

    path = _load_families(["Segoe UI Historic", "Segoe UI Symbol"], False, False)
    if path is None:
        return None

    try:
        ctx.symbol2 = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for symbol2")
        return ctx.symbol2
    except Exception:
        logging.warning(f"Failed to load font {path} for symbol2")
        return None


def load_system_text_font(
    ctx: FontContext, script: str, serif: bool, bold: bool, italic: bool
):
    try:
        return ctx.fallback[script]
    except KeyError:
        pass

    match script:
        case "Zyyy" | "Zinh" | "Zzzz":
            return None
        case "Latn" | "Grek" | "Cyrl":
            sans = ["Segoe UI", "Arial", "Calibri", "Verdana"]
            ser = ["Times New Roman", "Georgia", "Cambria"]
            path = _load_families(ser if serif else sans, bold, italic)
        case "Arab":
            if serif:
                ser = ["Noto Naskh Arabic Regular", "Scheherazade"]
                path = _load_families(ser if serif else sans, bold, italic)
            sans = ["Noto Sans Arabic Regular", "Dubai Regular"]
            path = _load_families(ser if serif else sans, bold, italic)
        case "Hebr":
            if serif:
                ser = [
                    "Noto Serif Hebrew Regular",
                    "Frank Ruehl CLM Medium",
                    "David Libre Regular",
                ]
                path = _load_families(ser if serif else sans, bold, italic)
            sans = ["Noto Sans Hebrew Regular"]
            path = _load_families(ser if serif else sans, bold, italic)
        case "Deva":
            path = _load_families(["Nirmala"], bold, italic)
        case "Thai":
            path = _load_families(["Leelawadee UI"], bold, italic)
        case "Laoo":
            path = _load_families(["Noto Sans Lao Regular"], bold, italic)
        case "Tibt":
            path = _load_families(["Microsoft Himalaya"], bold, italic)
        case "Mymr":
            path = _load_families(["Myanmar Text"], bold, italic)
        case "Armn":
            if serif:
                ser = ["Noto Serif Armenian Regular"]
                path = _load_families(ser if serif else sans, bold, italic)
            sans = ["Noto Sans Armenian Regular"]
            path = _load_families(ser if serif else sans, bold, italic)
        case "Geor":
            if serif:
                ser = ["Noto Serif Georgian Regular"]
                path = _load_families(ser if serif else sans, bold, italic)
            sans = ["Noto Sans Georgian Regular"]
            path = _load_families(ser if serif else sans, bold, italic)
        case "Hang":
            path = _load_families(["Malgun Gothic"], bold, italic)
        case "Hira" | "Kata":
            if bold:
                path = _load_families(["YuGothB"], bold, italic)
            path = _load_families(["YuGothR"], bold, italic)
        case "Bopo":
            if not serif:
                if bold:
                    path = _load_families(["msjhbd"], bold, italic)
                path = _load_families(["msjh"], bold, italic)
            path = _load_families(["mingliub"], bold, italic)
        case "Hani":
            if not serif:
                if bold:
                    path = _load_families(["msyhbd"], bold, italic)
                path = _load_families(["msyh"], bold, italic)
            path = _load_families(["simsun"], bold, italic)
        case (
            "Khmr"
            | "Mong"
            | "Copt"
            | "Taml"
            | "Telu"
            | "Knda"
            | "Mlym"
            | "Sinh"
            | "Gujr"
            | "Guru"
            | "Beng"
            | "Orya"
            | "Syrc"
            | "Thaa"
        ):
            path = _load_families(["Noto Sans Regular", "Segoe UI"], bold, italic)

        case _:
            return None

    if path is None:
        return None

    try:
        font_info = FontInfo.load(path)
        ctx.fallback[script] = font_info
        logging.info(f"🎉 Loaded path {path.name} for script {script}")
        return font_info
    except Exception as e:
        logging.warning(f"Failed to load font {path} for script {script}: {e=}")
        return None
