#!/usr/bin/env python3
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
        return "\n".join(repr(c) for c in lst)
    else:
        # join as a continuous string, showing newlines as literal '\\n' in repr
        return "".join(c if c != "\n" else "\n" for c in lst)


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
    p.add_argument("--n", type=int, default=100, help="生成する文字数")
    p.add_argument(
        "--out", default=None, help="生成結果の出力先ファイル (省略で標準出力)"
    )
    p.add_argument("--lines", action="store_true", help="1 行に 1 文字ずつ出力する")
    args = p.parse_args()

    if args.mode == "dist":
        csvp = Path(args.csv)
        if not csvp.exists():
            print(f"CSV ファイルが見つかりません: {csvp}")
            return 2
        chars, counts = read_distribution_from_csv(csvp)
        out = generate_by_distribution(chars, counts, args.n)
    else:
        src = Path(args.src)
        if not src.is_dir():
            print(f"処理済みディレクトリが見つかりません: {src}")
            return 2
        out = generate_by_text(src, args.n)

    text = render_list(out, args.lines)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"生成結果を保存しました: {args.out}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
