import sys

import fontTools
import fontTools.unicodedata

from fontmod.context import FontContext
from fontmod.info import FontInfo

if sys.platform == "win32":
    from fontmod.platform.windows import (
        load_system_boxes_font,
        load_system_emoji_font,
        load_system_math_font,
        load_system_music_font,
        load_system_symbol1_font,
        load_system_symbol2_font,
        load_system_text_font,
    )
else:
    from fontmod.platform.unix import (
        load_system_boxes_font,
        load_system_emoji_font,
        load_system_math_font,
        load_system_music_font,
        load_system_symbol1_font,
        load_system_symbol2_font,
        load_system_text_font,
    )


def fz_encode_character_with_system_font(
    ctx: FontContext,
    user_font: FontInfo | None,
    unicode: int,
    is_serif: bool | None = None,
    is_italic: bool | None = None,
    is_bold: bool | None = None,
) -> tuple[FontInfo, int] | None:
    is_serif = (
        (user_font.is_serif if user_font else False) if is_serif is None else is_serif
    )
    is_italic = (
        (user_font.is_italic if user_font else False)
        if is_italic is None
        else is_italic
    )
    is_bold = (
        (user_font.is_bold if user_font else False) if is_bold is None else is_bold
    )

    if user_font:
        gid = user_font.get_gid(unicode)
        if gid is not None:
            return user_font, gid

    script = fontTools.unicodedata.script(unicode)

    font = load_system_text_font(ctx, script, is_serif, is_bold, is_italic)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    font = load_system_boxes_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid
    font = load_system_emoji_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    font = load_system_math_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    font = load_system_music_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    font = load_system_symbol1_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    font = load_system_symbol2_font(ctx)
    if font:
        gid = font.get_gid(unicode)
        if gid is not None:
            return font, gid

    return None
