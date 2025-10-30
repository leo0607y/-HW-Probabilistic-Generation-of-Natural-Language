#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
"""
抽出した単語・2語/3語フレーズ分布（CSV）に従ってランダム生成
"""
from __future__ import annotations
import argparse
import csv
import random
from pathlib import Path
from typing import List


def read_freq_csv(path: Path) -> tuple[List[str], List[int]]:
    items = []
    counts = []
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            item = (
                row.get("word")
                or row.get("bigram")
                or row.get("trigram")
                or row.get("ngram")
            )
            if item is None:
                continue
            cnt = row.get("count")
            try:
                counts.append(int(cnt))
            except Exception:
                counts.append(0)
            items.append(item)
    return items, counts


def generate_by_distribution(items: List[str], counts: List[int], n: int) -> List[str]:
    if not items or not counts:
        return []
    return random.choices(items, weights=counts, k=n)


def main():
    p = argparse.ArgumentParser(description="単語/2語/3語フレーズ分布からランダム生成")
    p.add_argument(
        "--csv",
        required=True,
        help="分布CSV (word_freq.csv, bigram_freq.csv, trigram_freq.csv)",
    )
    p.add_argument("--n", type=int, default=100, help="生成する数")
    p.add_argument("--out", default=None, help="出力ファイル (省略で標準出力)")
    p.add_argument("--lines", action="store_true", help="1行に1件ずつ出力")
    p.add_argument("--seed", type=int, default=None, help="乱数シード")
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
    csvp = Path(args.csv)
    if not csvp.exists():
        print(f"CSVファイルが見つかりません: {csvp}")
        return 2
    items, counts = read_freq_csv(csvp)
    out_list = generate_by_distribution(items, counts, args.n)
    if args.lines:
        out_text = "\n".join(out_list)
    else:
        out_text = " ".join(out_list)
    if args.out:
        Path(args.out).write_text(out_text, encoding="utf-8")
        print(f"生成結果を保存しました: {args.out}")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
