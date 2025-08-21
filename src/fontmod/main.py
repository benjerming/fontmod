from __future__ import annotations

import logging
# import unicodedata

import fire

from fontmod.context import FontContext
# from fontmod.enumerator import FontEnumerator, FontRecord
from fontmod.picker import fz_encode_character_with_system_font

WORDS = (
    ("拉丁文字 (Latin)", "AaBbCcÀáÂâÃãÄäÅåÆæÇçÈéÊêËëÌíÎîÏïÐðÑñÒóÔôÕõÖöØøÙúÛûÜüÝýÞþßÿ"),
    ("中文汉字 (Chinese/CJK)", "你好世界中国汉字繁體字簡体字"),
    ("日文 (Japanese)", "あいうえおかきくけこひらがなアイウエオカキクケコカタカナ"),
    ("韩文 (Korean)", "안녕하세요한국어한글조선말"),
    ("阿拉伯文 (Arabic)", "مرحبا العالم العربية اللغة"),
    ("希伯来文 (Hebrew)", "שלום עולם עברית שפה"),
    ("俄文/西里尔文 (Russian/Cyrillic)", "Привет мир русский язык ЁёЪъЬь"),
    ("希腊文 (Greek)", "Γεια σας κόσμος ελληνικά γλώσσα ΑΒΓΔΕΖΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδν"),
    ("印地语/梵文 (Hindi/Devanagari)", "नमस्ते दुनिया हिंदी भाषा संस्कृत"),
    ("泰文 (Thai)", "สวัสดีโลกไทยภาษา"),
    ("越南文 (Vietnamese)", "Xin chào thế giới tiếng Việt"),
    ("土耳其文 (Turkish)", "Merhaba dünya Türkçe dil ÇçĞğİıÖöŞşÜü"),
    ("波兰文 (Polish)", "Witaj świecie polski język ĄąĆćĘęŁłŃńÓóŚśŹźŻż"),
    ("捷克文 (Czech)", "Ahoj světe český jazyk ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž"),
    ("匈牙利文 (Hungarian)", "Helló világ magyar nyelv ÁáÉéÍíÓóÖöŐőÚúÜüŰű"),
    ("芬兰文 (Finnish)", "Hei maailma suomi kieli ÄäÖö"),
    ("挪威文 (Norwegian)", "Hei verden norsk språk ÆæØøÅå"),
    ("丹麦文 (Danish)", "Hej verden dansk sprog ÆæØøÅå"),
    ("瑞典文 (Swedish)", "Hej världen svenska språk ÄäÅåÖö"),
    ("荷兰文 (Dutch)", "Hallo wereld Nederlands taal"),
    ("德文 (German)", "Hallo Welt deutsch Sprache ÄäÖöÜüß"),
    ("法文 (French)", "Bonjour monde français langue ÀàÂâÄäÇçÉéÈèÊêËëÎîÏïÔôÖöÙùÛûÜüŸÿ"),
    ("西班牙文 (Spanish)", "Hola mundo español idioma ÁáÉéÍíÑñÓóÚúÜü"),
    ("意大利文 (Italian)", "Ciao mondo italiano lingua ÀàÈèÉéÌìÍíÎîÒòÓóÙùÚú"),
    ("葡萄牙文 (Portuguese)", "Olá mundo português idioma ÁáÀàÂâÃãÇçÉéÊêÍíÓóÔôÕõÚú"),
    ("罗马尼亚文 (Romanian)", "Salut lume română limbă ĂăÂâÎîȘșȚț"),
    ("保加利亚文 (Bulgarian)", "Здравей свят български език"),
    ("塞尔维亚文 (Serbian)", "Здраво свете српски језик"),
    ("克罗地亚文 (Croatian)", "Pozdrav svijete hrvatski jezik ĆćČčĐđŠšŽž"),
    ("斯洛文尼亚文 (Slovenian)", "Pozdravljeni svet slovenščina jezik ČčŠšŽž"),
    ("立陶宛文 (Lithuanian)", "Labas pasauli lietuvių kalba ĄąČčĘęĖėĮįŠšŪūŲųŽž"),
    ("拉脱维亚文 (Latvian)", "Sveika pasaule latviešu valoda ĀāČčĒēĢģĪīĶķĻļŅņŠšŪūŽž"),
    ("爱沙尼亚文 (Estonian)", "Tere maailm eesti keel ÄäÖöÜüŠšŽž"),
    ("马耳他文 (Maltese)", "Bonġu dinja Malti lingwa ĊċĠġĦħŻż"),
    ("冰岛文 (Icelandic)", "Halló heimur íslenska tungumál ÁáÐðÉéÍíÓóÚúÝýÞþÆæÖö"),
    ("威尔士文 (Welsh)", "Helo byd Cymraeg iaith ÂâÊêÎîÔôÛûŴŵŶŷ"),
    ("爱尔兰文 (Irish)", "Dia dhuit domhan Gaeilge teanga ÁáÉéÍíÓóÚú"),
    ("苏格兰盖尔文 (Scottish Gaelic)", "Halò saoghal Gàidhlig cànan ÀàÈèÌìÒòÙù"),
    ("巴斯克文 (Basque)", "Kaixo mundua euskera hizkuntza"),
    ("加泰罗尼亚文 (Catalan)", "Hola món català idioma ÀàÇçÉéÈèÍíÒòÓóÚúÜü"),
    ("加利西亚文 (Galician)", "Ola mundo galego idioma ÁáÉéÍíÓóÚúÑñ"),
    ("阿尔巴尼亚文 (Albanian)", "Përshëndetje botë shqip gjuhë ÇçËë"),
    ("马其顿文 (Macedonian)", "Здраво свет македонски јазик"),
    ("波斯尼亚文 (Bosnian)", "Zdravo svijete bosanski jezik ĆćČčĐđŠšŽž"),
    ("黑山文 (Montenegrin)", "Zdravo svijete crnogorski jezik ĆćČčĐđŠšŽž"),
    ("波斯文/法尔西文 (Persian/Farsi)", "سلام جهان فارسی زبان"),
    ("乌尔都文 (Urdu)", "ہیلو دنیا اردو زبان"),
    ("印地文 (Hindi)", "नमस्ते दुनिया हिन्दी भाषा"),
    ("孟加拉文 (Bengali)", "হ্যালো বিশ্ব বাংলা ভাষা"),
    ("泰米尔文 (Tamil)", "வணக்கம் உலகம் தமிழ் மொழி"),
    ("泰卢固文 (Telugu)", "హలో ప్రపంచం తెలుగు భాష"),
    ("马拉雅拉姆文 (Malayalam)", "ഹലോ ലോകം മലയാളം ഭാഷ"),
    ("卡纳达文 (Kannada)", "ಹಲೋ ಜಗತ್ತು ಕನ್ನಡ ಭಾಷೆ"),
    ("古吉拉特文 (Gujarati)", "હેલો વિશ્વ ગુજરાતી ભાષા"),
    ("旁遮普文 (Punjabi)", "ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨੀਆ ਪੰਜਾਬੀ ਭਾਸ਼ਾ"),
    ("马拉地文 (Marathi)", "नमस्कार जग मराठी भाषा"),
    ("奥里亚文 (Odia)", "ନମସ୍କାର ବିଶ୍ୱ ଓଡ଼ିଆ ଭାଷା"),
    ("阿萨姆文 (Assamese)", "নমস্কাৰ বিশ্ব অসমীয়া ভাষা"),
    ("僧伽罗文 (Sinhala)", "හෙලෝ ලෝකය සිංහල භාෂාව"),
    ("缅甸文 (Myanmar/Burmese)", "မင်္ဂလာပါ ကမ္ဘာ မြန်မာ ဘာသာ"),
    ("老挝文 (Lao)", "ສະບາຍດີ ໂລກ ລາວ ພາສາ"),
    ("高棉文/柬埔寨文 (Khmer/Cambodian)", "ជំរាបសួរ ពិភពលោក ខ្មែរ ភាសា"),
    ("蒙古文 (Mongolian)", "Сайн байна уу дэлхий монгол хэл"),
    ("藏文 (Tibetan)", "བཀྲ་ཤིས་བདེ་ལེགས། འཇིག་རྟེན། བོད་ཡིག་"),
    ("格鲁吉亚文 (Georgian)", "გამარჯობა მსოფლიო ქართული ენა"),
    ("亚美尼亚文 (Armenian)", "Բարեւ աշխարհ հայերեն լեզու"),
    ("阿姆哈拉文 (Amharic)", "ሰላም ዓለም አማርኛ ቋንቋ"),
    ("希伯来文 (Hebrew)", "שלום עולם עברית שפה"),
    ("马来文 (Malay)", "Hello dunia Bahasa Melayu"),
    ("印尼文 (Indonesian)", "Halo dunia Bahasa Indonesia"),
    ("菲律宾文 (Filipino/Tagalog)", "Kumusta mundo Filipino wika"),
    ("斯瓦希里文 (Swahili)", "Hujambo dunia Kiswahili lugha"),
    ("南非荷兰文 (Afrikaans)", "Hallo wêreld Afrikaans taal"),
    ("约鲁巴文 (Yoruba)", "Pẹlẹ o ayé Yorùbá èdè"),
    ("豪萨文 (Hausa)", "Sannu duniya Hausa harshe"),
    ("阿姆哈拉文 (Amharic)", "ሰላም ዓለም አማርኛ ቋንቋ"),
    ("数字符号", "0123456789①②③④⑤⑥⑦⑧⑨⑩"),
    ("标点符号", '.,;:!?¡¿‚„"«»‹›\'\'""–—…‰‱'),
    ("数学符号", "+-×÷=≠≈≤≥∞∑∏∫∂√∆∇∈∉∪∩⊂⊃⊆⊇∧∨¬∀∃∅"),
    ("货币符号", "$€£¥¢₹₽₩₪₫₨₦₡₵₴₸₼₿"),
    ("特殊符号", "©®™§¶†‡•◦‣⁃▪▫◊○●◐◑◒◓◔◕◖◗◘◙◚◛◜◝◞◟◠◡"),
    ("箭头符号", "←↑→↓↔↕↖↗↘↙⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙➔➡⬅⬆⬇⬈⬉⬊⬋"),
    ("几何形状", "▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅■□▪▫▬▭▮▯▰▱▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅"),
    ("星星符号", "★☆✦✧✩✪✫✬✭✮✯✰✱✲✳✴✵✶✷✸✹✺✻✼✽✾✿❀❁❂❃❄❅❆❇❈❉❊❋"),
    ("表情符号 (Emoji)", "😀😃😄😁😆😅🤣😂🙂🙃😉😊😇🥰😍🤩😘😗"),
    ("手势符号", "👋🤚🖐✋🖖👌🤌🤏✌🤞🤟🤘🤙👈👉👆🖕👇☝👍👎👊✊🤛🤜"),
)


# def normalize_text(text: str) -> str:
#     # 归一化，去掉不可见控制字符（保留换行/空格）
#     t = unicodedata.normalize("NFC", text)
#     return "".join(
#         ch
#         for ch in t
#         if not unicodedata.category(ch).startswith("C") or ch in ("\n", "\t", "\r")
#     )


# def needed_codepoints(text: str) -> set[int]:
#     t = normalize_text(text)
#     # 忽略空白
#     return {ord(ch) for ch in t if not ch.isspace()}


# def coverage_for_font(fr: FontRecord, needed: set[int]) -> tuple[int, int, float]:
#     """
#     返回 (命中数, 需求总数, 覆盖率)
#     """
#     supported = fr.info.unicode2gid.keys()
#     if not supported:
#         return (0, len(needed), 0.0)
#     hit = sum(1 for cp in needed if cp in supported)
#     total = len(needed) if needed else 1
#     return (hit, total, hit / total)


# def pick_best_fonts(
#     text: str, top_k: int = 5, require_full: bool = False
# ) -> list[tuple[FontRecord, float]]:
#     """
#     从系统字体中挑选能渲染 `text` 的最佳字体。
#     - require_full=True 时仅返回覆盖率==1 的字体
#     - 否则返回覆盖率最高的 top_k
#     """
#     need = needed_codepoints(text)
#     if not need:
#         return []

#     fe = FontEnumerator()

#     candidates = fe.font_records
#     scored: list[tuple[FontRecord, float]] = []
#     for fr in candidates:
#         hit, total, ratio = coverage_for_font(fr, need)
#         if ratio == 1.0 and require_full:
#             scored.append((fr, ratio))
#         elif not require_full:
#             # 提前剪枝：覆盖率过低的跳过（比如 0）
#             if hit > 0:
#                 scored.append((fr, ratio))

#     scored.sort(key=lambda x: (x[1], x[0].info.name.lower()), reverse=True)

#     if require_full:
#         return scored[:top_k]
#     return scored[:top_k]


# def pick_font_fallback_chain(text: str, max_fonts: int = 3) -> list[FontRecord]:
#     remaining = needed_codepoints(text)
#     if not remaining:
#         return []

#     fe = FontEnumerator()
#     chain: list[FontRecord] = []
#     fonts = fe.font_records

#     for _ in range(max_fonts):
#         best: tuple[FontRecord, int] | None = None
#         for fr in fonts:
#             cps = fr.info.unicode2gid.keys()
#             gain = len(remaining & set(cps))
#             if gain == 0:
#                 continue
#             if best is None or gain > best[1]:
#                 best = (fr, gain)
#         if best is None:
#             break
#         fr, _ = best
#         chain.append(fr)
#         remaining = remaining - set(fr.info.unicode2gid.keys())
#         if not remaining:
#             break
#     return chain


# def main():
#     for lang, word in WORDS:
#         best = pick_best_fonts(word, top_k=5, require_full=False)
#         for fr, ratio in best:
#             print(f"    {word} -> {fr.info.name}  —  {ratio:.1%}  @ {fr.path}")

#         chain = pick_font_fallback_chain(word, max_fonts=3)
#         print("\nFallback chain:")
#         for fr in chain:
#             print(f"- {fr.info.name} @ {fr.path}")


def main():
    ctx = FontContext()
    font = None
    for lang, word in WORDS:
        logging.info(f"{lang=}")
        for c in word:
            res = fz_encode_character_with_system_font(ctx, font, ord(c))
            if res is not None:
                font, gid = res
                logging.info(f"    {c} -> {font.name=}  —  {gid=}")
            else:
                logging.info(f"    {c} -> ❌")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
