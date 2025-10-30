#!/usr/bin/env python3
"""
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
"""
"""
processed 出力の検証スクリプト (process1 フォルダ版)
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
import sys


RE_ALLOWED = re.compile(r"^[A-Za-z \n]*$", re.MULTILINE)


def check_file_allowed(path: Path) -> tuple[bool, str | None]:

    txt = path.read_text(encoding="utf-8", errors="replace")
    if RE_ALLOWED.match(txt):
        return True, None

    for i, line in enumerate(txt.splitlines(), start=1):
        if not RE_ALLOWED.match(line + "\n"):
            bad_chars = sorted(set(re.findall(r"[^A-Za-z \n]", line)))
            sample = f"line {i}: {line[:200]!r}... bad_chars={bad_chars}"
            return False, sample
    return False, "unknown issue"


def main() -> int:
    p = argparse.ArgumentParser(description="Verify processed texts")
    p.add_argument("--src", default="Unprocessed")
    p.add_argument("--dst", default="examples/processed")
    args = p.parse_args()

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)

    if not src_dir.is_dir():
        print(f"ディレクトリが見つかりません: {src_dir}")
        return 2
    if not dst_dir.is_dir():
        print(f"出力ディレクトリが見つかりません: {dst_dir}")
        return 2

    src_files = sorted(src_dir.glob("*.txt"))
    if not src_files:
        print(f"テキストファイルが見つかりません: {src_dir}")
        return 2

    overall_ok = True
    for s in src_files:
        expected = dst_dir / f"{s.stem}_processed.txt"
        if not expected.exists():
            print(f"Missing: {expected} (ファイルがない)")
            overall_ok = False
            continue

        ok, sample = check_file_allowed(expected)
        if not ok:
            print(f"NG: {expected} に不許可文字があります -> {sample}")
            overall_ok = False
        else:
            s_text = s.read_text(encoding="utf-8", errors="replace")
            has_digits = bool(re.search(r"\d", s_text))
            if has_digits:
                dst_text = expected.read_text(encoding="utf-8", errors="replace")
                if re.search(r"\d", dst_text):
                    print(f"警告: {expected} に数字が残っています ")
                    overall_ok = False
                else:
                    print(f"OK: {expected} （許可文字のみ、数字は除去済）")
            else:
                print(f"OK: {expected} （許可文字のみ）")

    if overall_ok:
        print("\n成功")
        return 0
    else:
        print("\n失敗")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
