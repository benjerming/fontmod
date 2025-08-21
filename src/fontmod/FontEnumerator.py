import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from fontmod.FontInfo import FontInfo


@dataclass(frozen=True)
class FontRecord:
    info: FontInfo
    path: Path

    def __hash__(self):
        return hash(self.path)


FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".otc"}


class FontEnumerator:
    def __init__(self):
        self.dirs: set[Path] = {
            Path("C:/Windows/Fonts"),
            Path("/system/fonts"),
            Path("/usr/share/fonts"),
            Path("/Library/Fonts"),
        }

        self.font_records: set[FontRecord] = set()
        self.path_to_records: dict[Path, FontRecord] = {}
        self.name_to_records: dict[str, FontRecord] = {}
        self.name_to_paths: dict[str, list[Path]] = {}

        self._update_fonts()

    def register_font_dir(self, dir: str | Path):
        self.dirs.add(Path(dir).resolve())
        self._update_fonts()

    def enumerate_fonts(self) -> Generator[Path, None, None]:
        for dir in self.dirs:
            for path in dir.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in FONT_SUFFIXES:
                    continue
                yield path

    def _update_fonts(self):
        for path in self.enumerate_fonts():
            if path in self.path_to_records:
                continue
            try:
                info = FontInfo.load(path)
                record = FontRecord(info, path)
                self.font_records.add(record)
            except Exception as e:
                logging.warning(f"Failed to load font {path}: {e}")
                continue
        self._update_fonts_map()

    def _update_fonts_map(self):
        for record in self.font_records:
            self.path_to_records[record.path] = record
            self.name_to_records[record.info.name] = record
            try:
                self.name_to_paths[record.info.name].append(record.path)
            except KeyError:
                self.name_to_paths[record.info.name] = [record.path]

    def get_font(self, path: Path) -> FontRecord | None:
        return self.path_to_records.get(path)

    def get_font_by_name(self, name: str) -> FontRecord | None:
        return self.name_to_records.get(name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fe = FontEnumerator()
    # logging.info(list(fe.enumerate_fonts()))
    logging.info(len(fe.font_records))
    logging.info(len(fe.path_to_records))
    logging.info(len(fe.name_to_records))
    import json

    class PathEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Path):
                return str(obj)
            return super().default(obj)

    logging.info(
        json.dumps(fe.name_to_paths, indent=2, cls=PathEncoder, ensure_ascii=False)
    )
