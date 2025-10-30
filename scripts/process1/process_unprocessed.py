#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path


RE_NON_ALLOWED = re.compile(r"[^A-Za-z \n]")


def process_text(text: str) -> str:

    s = RE_NON_ALLOWED.sub(" ", text)
    lines = [re.sub(r" {2,}", " ", line) for line in s.splitlines()]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def process_file(src_path: Path, dst_path: Path, overwrite: bool = False) -> None:
    if dst_path.exists() and not overwrite:
        print(f"Skipping existing output: {dst_path}")
        return
    text = src_path.read_text(encoding="utf-8", errors="replace")
    processed = process_text(text)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(processed, encoding="utf-8")
    print(f"Wrote: {dst_path} (bytes: {len(processed)})")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Process Unprocessed texts into processed/ folder"
    )
    p.add_argument(
        "--src", default="Unprocessed", help="Source directory containing .txt files"
    )
    p.add_argument(
        "--dst",
        default="examples/processed",
        help="Destination directory for processed files",
    )
    p.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing processed files"
    )
    args = p.parse_args()

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)

    if not src_dir.is_dir():
        raise SystemExit(f"ディレクトリが見つからない: {src_dir}")

    txt_files = sorted(src_dir.glob("*.txt"))
    if not txt_files:
        print(f" {src_dir}にテキストが見つからない")
        return

    for src in txt_files:
        name = src.stem
        dst = dst_dir / f"{name}_processed.txt"
        process_file(src, dst, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
