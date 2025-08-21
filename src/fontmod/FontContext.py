from fontmod.FontEnumerator import FontInfo


class FontContext:
    def __init__(self):
        self.fallback: dict[str, FontInfo] = {}
        self.boxes: FontInfo | None = None
        self.emoji: FontInfo | None = None
        self.math: FontInfo | None = None
        self.music: FontInfo | None = None
        self.symbol1: FontInfo | None = None
        self.symbol2: FontInfo | None = None
