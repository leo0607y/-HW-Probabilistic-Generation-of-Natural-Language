#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
import csv
import random
from pathlib import Path
from typing import List, Tuple


def read_distribution_from_csv(path: Path) -> Tuple[List[str], List[int]]:
    chars: List[str] = []
    counts: List[int] = []
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        # Expect columns: rank,char,count,ratio
        for row in r:
            ch = row.get("char")
            if ch is None:
                continue
            # normalize special labels used in CSV: literal '\\n' -> newline, 'space' -> actual space
            if ch == "\\n":
                ch = "\n"
            elif ch == "space":
                ch = " "
            chars.append(ch)
            cnt = row.get("count")
            try:
                counts.append(int(cnt))
            except Exception:
                counts.append(0)
    return chars, counts


def generate_by_distribution(chars: List[str], counts: List[int], n: int) -> List[str]:
    # random.choices supports weights
    if not chars or not counts:
        return []
    return random.choices(chars, weights=counts, k=n)


def generate_by_text(src_dir: Path, n: int) -> List[str]:
    parts: List[str] = []
    for p in sorted(src_dir.glob("*_processed.txt")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    full = "".join(parts)
    if not full:
        return []
    M = len(full)
    out: List[str] = []
    for _ in range(n):
        k = random.randint(1, M)
        out.append(full[k - 1])
    return out


def render_list(lst: List[str], one_per_line: bool) -> str:
    if one_per_line:
        return "\n".join(c for c in lst)
    else:
        return "".join(lst)


def main() -> int:
    p = argparse.ArgumentParser(
        description="手順4: 文字分布に従ってランダム文字を生成します"
    )
    p.add_argument(
        "--mode",
        choices=["dist", "text"],
        default="dist",
        help="生成方法: dist=CSVの分布を使う, text=全文字列からランダムに選ぶ",
    )
    p.add_argument(
        "--csv",
        default="/home/leo0607y/work/numerical_analysis/Output/process2/char_freq_case_insensitive.csv",
        help="分布CSV のパス (dist モード)",
    )
    p.add_argument(
        "--src",
        default="examples/processed",
        help="処理済みテキストのディレクトリ (text モード) ",
    )
    p.add_argument(
        "--alltext",
        default="ALL_TEXT.txt",
        help="ALL_TEXT.txt のパス (text モードで優先的に使用)",
    )
    p.add_argument("--n", type=int, default=100, help="生成する文字数")
    p.add_argument(
        "--out", default=None, help="生成結果の出力先ファイル (省略で標準出力)"
    )
    p.add_argument("--lines", action="store_true", help="1 行に 1 文字ずつ出力する")
    p.add_argument(
        "--no-newline",
        action="store_true",
        help="インライン出力時に改行文字を削除して横並びにする（--lines と併用しないこと）",
    )
    args = p.parse_args()

    if args.mode == "dist":
        csvp = Path(args.csv)
        if not csvp.exists():
            print(f"CSV ファイルが見つかりません: {csvp}")
            return 2
        chars, counts = read_distribution_from_csv(csvp)
        out = generate_by_distribution(chars, counts, args.n)
    else:
        allp = Path(args.alltext)
        src = Path(args.src)
        # if ALL_TEXT.txt does not exist, build it by concatenating processed files
        if not allp.exists():
            if not src.is_dir():
                print(f"処理済みディレクトリが見つかりません: {src}")
                return 2
            parts: list[str] = []
            for p in sorted(src.glob("*_processed.txt")):
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
            full = "".join(parts)
            allp.write_text(full, encoding="utf-8")
            print(f"作成: {allp} (結合済みテキスト) 文字数={len(full)}")

        alltxt = allp.read_text(encoding="utf-8", errors="replace")
        if not alltxt:
            print(f"ALL_TEXT.txt が空です: {allp}")
            return 2
        M = len(alltxt)
        out_list: list[str] = []
        for _ in range(args.n):
            k = random.randint(1, M)
            out_list.append(alltxt[k - 1])
        out = out_list

    # 出力: 引用符や repr を使わずそのまま表示する
    if args.lines:
        # 1 行に 1 文字ずつ（改行文字は空行となる）
        if args.out:
            Path(args.out).write_text("\n".join(out), encoding="utf-8")
            print(f"生成結果を保存しました: {args.out}")
        else:
            for c in out:
                print(c, end="\n")
    else:
        joined = "".join(out)
        # --no-newline が指定されていれば改行文字を削除して横並びにする
        if getattr(args, "no_newline", False):
            joined = joined.replace("\n", "")
        if args.out:
            Path(args.out).write_text(joined, encoding="utf-8")
            print(f"生成結果を保存しました: {args.out}")
        else:
            print(joined)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
