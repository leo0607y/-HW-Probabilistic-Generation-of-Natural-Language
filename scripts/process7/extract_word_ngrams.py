#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
"""
ALL_TEXT.txtから全単語・全2語/3語フレーズの頻度ランキングをCSV出力
"""
from __future__ import annotations
import argparse
import re
import csv
from pathlib import Path
from collections import Counter


def tokenize(text: str) -> list[str]:
    # 単語・記号単位で分割
    return re.findall(r"\b\w+\b|[.,!?;:\-']", text)


def ngrams(words: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


def save_csv(counter: Counter, path: Path, label: str = "ngram"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", label, "count", "ratio"])
        total = sum(counter.values())
        for i, (ng, cnt) in enumerate(counter.most_common(), start=1):
            ng_str = " ".join(ng) if isinstance(ng, tuple) else ng
            w.writerow([i, ng_str, cnt, f"{cnt/total:.8f}"])


def main():
    p = argparse.ArgumentParser(
        description="ALL_TEXT.txtから全単語・全2語/3語フレーズ頻度CSV出力"
    )
    p.add_argument("--alltext", default="ALL_TEXT.txt", help="学習用テキスト")
    p.add_argument("--outdir", default="Output/process7", help="出力ディレクトリ")
    args = p.parse_args()

    allp = Path(args.alltext)
    if not allp.exists():
        print(f"ALL_TEXT.txt が見つかりません: {allp}")
        return 2
    text = allp.read_text(encoding="utf-8", errors="replace")
    words = []
    for line in text.splitlines():
        words.extend(tokenize(line))
    if not words:
        print("単語が抽出できません")
        return 2
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # 単語頻度
    wc = Counter(words)
    save_csv(wc, outdir / "word_freq.csv", label="word")
    # 2語フレーズ
    bg = Counter(ngrams(words, 2))
    save_csv(bg, outdir / "bigram_freq.csv", label="bigram")
    # 3語フレーズ
    tg = Counter(ngrams(words, 3))
    save_csv(tg, outdir / "trigram_freq.csv", label="trigram")
    print(f"保存: {outdir}/word_freq.csv, bigram_freq.csv, trigram_freq.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
