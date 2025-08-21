import itertools
import logging
from functools import lru_cache
from pathlib import Path

from fontmod.FontContext import FontContext
from fontmod.FontInfo import FontInfo

_font_dirs = [
    Path("/system/fonts"),
    Path("/usr/share/fonts"),
    Path("/Library/Fonts"),
]


def _font_files(paths: list[Path]):
    return itertools.chain.from_iterable(path.rglob("*") for path in paths)


@lru_cache(maxsize=1024)
def _load_noto(a: str, b: str, c: str):
    stem = f"{a}{b}{c}"
    for path in _font_files(_font_dirs):
        if path.name.startswith(stem):
            return path

    return None


def _load_noto_cjk(script: str, serif: bool = False):
    match script:
        case "Hani":
            lang = "SC"
        case "Hira" | "Kata":
            lang = "JP"
        case "Bopo":
            lang = "TC"
        case "Hang":
            lang = "KR"
        case _:
            lang = "SC"

    base = "NotoSerif" if serif else "NotoSans"
    font = (
        _load_noto(base, "CJK", "-Regular")
        or _load_noto(base, lang, "-Regular")
        or _load_noto("DroidSans", "", "-Regular")
        or _load_noto("DroidSans", "Fallback", "-Regular")
        or _load_noto("DroidSans", "", "Mono")
        or _load_noto("DroidSans", "Fallback", "Mono")
    )

    return font


def _load_noto_arabic(serif: bool = False):
    base = "NotoSerif" if serif else "NotoSans"
    font = (
        _load_noto("Noto", "Naskh", "-Regular")
        or _load_noto("Noto", "NaskhArabic", "-Regular")
        or _load_noto("Droid", "Naskh", "-Regular")
        or _load_noto(base, "Arabic", "-Regular")
        or _load_noto("DroidSans", "Arabic", "-Regular")
    )
    return font


def _load_noto_try(stem: str, serif: bool = False):
    base = "NotoSerif" if serif else "NotoSans"
    font = (
        _load_noto(base, stem, "-Regular")
        or _load_noto("Roboto", "", "-Regular")
        or _load_noto("DroidSans", "Fallback", "-Regular")
        or _load_noto("DroidSans", "Fallback", "-Regular")
        or _load_noto("DroidSans", "Fallback", "-Regular")
    )
    return font


def load_system_boxes_font(ctx: FontContext):
    if ctx.boxes is not None:
        return ctx.boxes

    path = _load_noto("NotoSans", "Symbols2", "-Regular")
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

    path = _load_noto("NotoColorEmoji", "", "")
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

    path = _load_noto("NotoSans", "Math", "-Regular") or _load_noto(
        "Noto", "SansMath", "-Regular"
    )
    if path is None:
        return None

    try:
        ctx.math = FontInfo.load(path)
        logging.info(f"🎉 Loaded path {path.name} for math")
        return ctx.math
    except Exception:
        logging.warning(f"Failed to load font {path} for math")
        return None

    return ctx.math


def load_system_music_font(ctx: FontContext):
    if ctx.music is not None:
        return ctx.music

    path = _load_noto("Noto", "Music", "-Regular")
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

    path = _load_noto("NotoSans", "Symbols", "-Regular")
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

    path = _load_noto("NotoSans", "Symbols2", "-Regular")
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
            path = None
        case "Hang" | "Hira" | "Kata" | "Bopo" | "Hani":
            path = _load_noto_cjk(script, serif)
        case "Latn" | "Grek" | "Cyrl":
            path = _load_noto_try("", serif)
        case "Arab":
            path = _load_noto_arabic(serif)
        case "Armn":
            path = _load_noto_try("Armenian", serif)
        case "Hebr":
            path = _load_noto_try("Hebrew", serif)
        case "Syrc":
            path = _load_noto_try("Syriac", serif)
        case "Thaa":
            path = _load_noto_try("Thaana", serif)
        case "Deva":
            path = _load_noto_try("Devanagari", serif)
        case "Beng":
            path = _load_noto_try("Bengali", serif)
        case "Guru":
            path = _load_noto_try("Gurmukhi", serif)
        case "Gujr":
            path = _load_noto_try("Gujarati", serif)
        case "Orya":
            path = _load_noto_try("Oriya", serif)
        case "Taml":
            path = _load_noto_try("Tamil", serif)
        case "Telu":
            path = _load_noto_try("Telugu", serif)
        case "Knda":
            path = _load_noto_try("Kannada", serif)
        case "Mlym":
            path = _load_noto_try("Malayalam", serif)
        case "Sinh":
            path = _load_noto_try("Sinhala", serif)
        case "Thai":
            path = _load_noto_try("Thai", serif)
        case "Laoo":
            path = _load_noto_try("Lao", serif)
        case "Tibt":
            path = _load_noto_try("Tibetan", serif)
        case "Mymr":
            path = _load_noto_try("Myanmar", serif)
        case "Geor":
            path = _load_noto_try("Georgian", serif)
        case "Ethi":
            path = _load_noto_try("Ethiopic", serif)
        case "Cher":
            path = _load_noto_try("Cherokee", serif)
        case "Cans":
            path = _load_noto_try("CanadianAboriginal", serif)
        case "Ogam":
            path = _load_noto_try("Ogham", serif)
        case "Runr":
            path = _load_noto_try("Runic", serif)
        case "Khmr":
            path = _load_noto_try("Khmer", serif)
        case "Mong":
            path = _load_noto_try("Mongolian", serif)
        case "Yiii":
            path = _load_noto_try("Yi", serif)
        case "Ital":
            path = _load_noto_try("OldItalic", serif)
        case "Goth":
            path = _load_noto_try("Gothic", serif)
        case "Dsrt":
            path = _load_noto_try("Deseret", serif)
        case "Tglg":
            path = _load_noto_try("Tagalog", serif)
        case "Hano":
            path = _load_noto_try("Hanunoo", serif)
        case "Buhd":
            path = _load_noto_try("Buhid", serif)
        case "Tagb":
            path = _load_noto_try("Tagbanwa", serif)
        case "Limb":
            path = _load_noto_try("Limbu", serif)
        case "Tale":
            path = _load_noto_try("TaiLe", serif)
        case "Linb":
            path = _load_noto_try("LinearB", serif)
        case "Ugar":
            path = _load_noto_try("Ugaritic", serif)
        case "Shaw":
            path = _load_noto_try("Shavian", serif)
        case "Osma":
            path = _load_noto_try("Osmanya", serif)
        case "Copt":
            path = _load_noto_try("Cypriot", serif)
        case "Bugi":
            path = _load_noto_try("Buginese", serif)
        case "Copt":
            path = _load_noto_try("Coptic", serif)
        case "Talu":
            path = _load_noto_try("NewTaiLue", serif)
        case "Glag":
            path = _load_noto_try("Glagolitic", serif)
        case "Tfng":
            path = _load_noto_try("Tifinagh", serif)
        case "Sylo":
            path = _load_noto_try("SylotiNagri", serif)
        case "Xpeo":
            path = _load_noto_try("OldPersian", serif)
        case "Khar":
            path = _load_noto_try("Kharoshthi", serif)
        case "Bali":
            path = _load_noto_try("Balinese", serif)
        case "Xsux":
            path = _load_noto_try("Cuneiform", serif)
        case "Phnx":
            path = _load_noto_try("Phoenician", serif)
        case "Phag":
            path = _load_noto_try("PhagsPa", serif)
        case "Nkoo":
            path = _load_noto_try("NKo", serif)
        case "Sund":
            path = _load_noto_try("Sundanese", serif)
        case "Lepc":
            path = _load_noto_try("Lepcha", serif)
        case "Olck":
            path = _load_noto_try("OlChiki", serif)
        case "Vaii":
            path = _load_noto_try("Vai", serif)
        case "Saur":
            path = _load_noto_try("Saurashtra", serif)
        case "Kali":
            path = _load_noto_try("KayahLi", serif)
        case "Rjng":
            path = _load_noto_try("Rejang", serif)
        case "Lyci":
            path = _load_noto_try("Lycian", serif)
        case "Chrs":
            path = _load_noto_try("Carian", serif)
        case "Lydi":
            path = _load_noto_try("Lydian", serif)
        case "Cham":
            path = _load_noto_try("Cham", serif)
        case "Lana":
            path = _load_noto_try("TaiTham", serif)
        case "Tavt":
            path = _load_noto_try("TaiViet", serif)
        case "Avst":
            path = _load_noto_try("Avestan", serif)
        case "Egyp":
            path = _load_noto_try("EgyptianHieroglyphs", serif)
        case "Samr":
            path = _load_noto_try("Samaritan", serif)
        case "Lisu":
            path = _load_noto_try("Lisu", serif)
        case "Bamu":
            path = _load_noto_try("Bamum", serif)
        case "Java":
            path = _load_noto_try("Javanese", serif)
        case "Mtei":
            path = _load_noto_try("MeeteiMayek", serif)
        case "Phlp":
            path = _load_noto_try("ImperialAramaic", serif)
        case "Sarb":
            path = _load_noto_try("OldSouthArabian", serif)
        case "Prti":
            path = _load_noto_try("InscriptionalParthian", serif)
        case "Phli":
            path = _load_noto_try("InscriptionalPahlavi", serif)
        case "Orkh":
            path = _load_noto_try("OldTurkic", serif)
        case "Kthi":
            path = _load_noto_try("Kaithi", serif)
        case "Batk":
            path = _load_noto_try("Batak", serif)
        case "Brah":
            path = _load_noto_try("Brahmi", serif)
        case "Mand":
            path = _load_noto_try("Mandaic", serif)
        case "Cakm":
            path = _load_noto_try("Chakma", serif)
        case "Plrd":
            path = _load_noto_try("Miao", serif)
        case "Merc":
            path = _load_noto_try("Meroitic", serif)
        case "Mero":
            path = _load_noto_try("Meroitic", serif)
        case "Shrd":
            path = _load_noto_try("Sharada", serif)
        case "Sora":
            path = _load_noto_try("SoraSompeng", serif)
        case "Takr":
            path = _load_noto_try("Takri", serif)
        case "Bass":
            path = _load_noto_try("BassaVah", serif)
        case "Aghb":
            path = _load_noto_try("CaucasianAlbanian", serif)
        case "Dupl":
            path = _load_noto_try("Duployan", serif)
        case "Elba":
            path = _load_noto_try("Elbasan", serif)
        case "Gran":
            path = _load_noto_try("Grantha", serif)
        case "Khoj":
            path = _load_noto_try("Khojki", serif)
        case "Sind":
            path = _load_noto_try("Khudawadi", serif)
        case "Lina":
            path = _load_noto_try("LinearA", serif)
        case "Mahj":
            path = _load_noto_try("Mahajani", serif)
        case "Mani":
            path = _load_noto_try("Manichaean", serif)
        case "Mend":
            path = _load_noto_try("MendeKikakui", serif)
        case "Modi":
            path = _load_noto_try("Modi", serif)
        case "Mroo":
            path = _load_noto_try("Mro", serif)
        case "Narb":
            path = _load_noto_try("Nabataean", serif)
        case "Narb":
            path = _load_noto_try("OldNorthArabian", serif)
        case "Perm":
            path = _load_noto_try("OldPermic", serif)
        case "Hmng":
            path = _load_noto_try("PahawhHmong", serif)
        case "Palm":
            path = _load_noto_try("Palmyrene", serif)
        case "Pauc":
            path = _load_noto_try("PauCinHau", serif)
        case "Phli":
            path = _load_noto_try("PsalterPahlavi", serif)
        case "Sidd":
            path = _load_noto_try("Siddham", serif)
        case "Tirh":
            path = _load_noto_try("Tirhuta", serif)
        case "Wara":
            path = _load_noto_try("WarangCiti", serif)
        case "Ahom":
            path = _load_noto_try("Ahom", serif)
        case "Egyp":
            path = _load_noto_try("AnatolianHieroglyphs", serif)
        case "Hatr":
            path = _load_noto_try("Hatran", serif)
        case "Mult":
            path = _load_noto_try("Multani", serif)
        case "Hung":
            path = _load_noto_try("OldHungarian", serif)
        case "Sgnw":
            path = _load_noto_try("Signwriting", serif)
        case "Adlm":
            path = _load_noto_try("Adlam", serif)
        case "Bhks":
            path = _load_noto_try("Bhaiksuki", serif)
        case "Marc":
            path = _load_noto_try("Marchen", serif)
        case "Newa":
            path = _load_noto_try("Newa", serif)
        case "Osge":
            path = _load_noto_try("Osage", serif)
        case "Tang":
            path = _load_noto_try("Tangut", serif)
        case "Gonm":
            path = _load_noto_try("MasaramGondi", serif)
        case "Nshu":
            path = _load_noto_try("Nushu", serif)
        case "Soyo":
            path = _load_noto_try("Soyombo", serif)
        case "Zanb":
            path = _load_noto_try("ZanabazarSquare", serif)
        case "Dogr":
            path = _load_noto_try("Dogra", serif)
        case "Gong":
            path = _load_noto_try("GunjalaGondi", serif)
        case "Rohg":
            path = _load_noto_try("HanifiRohingya", serif)
        case "Maka":
            path = _load_noto_try("Makasar", serif)
        case "Medf":
            path = _load_noto_try("Medefaidrin", serif)
        case "Sogo":
            path = _load_noto_try("OldSogdian", serif)
        case "Sogd":
            path = _load_noto_try("Sogdian", serif)
        case "Elym":
            path = _load_noto_try("Elymaic", serif)
        case "Nand":
            path = _load_noto_try("Nandinagari", serif)
        case "Hmnp":
            path = _load_noto_try("NyiakengPuachueHmong", serif)
        case "Wcho":
            path = _load_noto_try("Wancho", serif)
        case "Chrs":
            path = _load_noto_try("Chorasmian", serif)
        case "Diak":
            path = _load_noto_try("DivesAkuru", serif)
        case "Kits":
            path = _load_noto_try("KhitanSmallScript", serif)
        case "Yezi":
            path = _load_noto_try("Yezidi", serif)
        case "Vith":
            path = _load_noto_try("Vithkuqi", serif)
        case "Ougr":
            path = _load_noto_try("OldUyghur", serif)
        case "Cpmn":
            path = _load_noto_try("CyproMinoan", serif)
        case "Tnsa":
            path = _load_noto_try("Tangsa", serif)
        case "Toto":
            path = _load_noto_try("Toto", serif)
        case _:
            return None

    if path is None:
        return None

    try:
        font_info = FontInfo.load(path)
        ctx.fallback[script] = font_info
        logging.info(f"🎉 Loaded path {path.name} for script {script}")
        return font_info
    except Exception:
        logging.warning(f"Failed to load font {path} for script {script}")
        return None

    return None
