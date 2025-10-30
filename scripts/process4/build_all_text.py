#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path


def build_all_text(src_dir: Path, out_file: Path) -> int:
    """Concatenate all *_processed.txt in src_dir into out_file.

    Returns total number of characters written.
    """
    parts: list[str] = []
    for p in sorted(src_dir.glob("*_processed.txt")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    full = "".join(parts)
    out_file.write_text(full, encoding="utf-8")
    return len(full)


def main() -> int:
    src = Path("examples/processed")
    out = Path("ALL_TEXT.txt")
    if not src.is_dir():
        print(f"processed ディレクトリが見つかりません: {src}")
        return 2
    n = build_all_text(src, out)
    print(f"作成しました: {out} (文字数={n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
