#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
import random
from pathlib import Path
from typing import Optional


def generate_by_ngram_alltext(alltext: str, ngram: int, length: int) -> str:
    """
    Generate a string of requested length using the simplified n-gram method described.

    For bigram (ngram=2):
      - pick random k with k+1 < M, output alltext[k:k+2], set A = alltext[k+1]
      - repeat: pick random k', search from k' for first occurrence of A where i+1 < M,
        if found append alltext[i+1] to output and set A = alltext[i+1]
        otherwise retry a limited number of times and fallback to random adjacent char

    For trigram (ngram=3): similar but A is last (n-1) characters and we search for A
    occurrences and take the following character.
    """
    M = len(alltext)
    if M == 0:
        return ""

    # ensure we can form at least one ngram
    if ngram < 2 or ngram > 3:
        raise ValueError("ngram must be 2 or 3")

    # seed: choose initial k so that k+(ngram-1) < M
    max_k = M - (ngram - 1)
    if max_k <= 0:
        return ""
    k = random.randint(0, max_k - 1)
    out_chars = list(alltext[k : k + ngram])

    # the 'context' A is last n-1 chars
    A = "".join(out_chars[-(ngram - 1) :])

    # generate until reaching desired length
    while len(out_chars) < length:
        # pick random start
        start = random.randint(0, M - 1)
        found = -1
        # try searching from start to end
        idx = alltext.find(A, start)
        if idx != -1 and idx + (ngram - 1) < M:
            found = idx
        else:
            # try from beginning to start (wrap)
            idx = alltext.find(A, 0)
            if idx != -1 and idx + (ngram - 1) < M:
                found = idx

        if found != -1:
            # append the character following the matched context
            next_pos = found + (ngram - 1)
            next_char = alltext[next_pos]
            out_chars.append(next_char)
            A = (A + next_char)[-(ngram - 1) :]
        else:
            # fallback: pick random position with room and append next char
            fk = random.randint(0, M - ngram)
            next_char = alltext[fk + ngram - 1]
            out_chars.append(next_char)
            A = (A + next_char)[-(ngram - 1) :]

    return "".join(out_chars[:length])


def main() -> int:
    p = argparse.ArgumentParser(
        description="手順5: 二ッ組/三ッ組出現率に従った簡便なランダム文字列生成"
    )
    p.add_argument(
        "--ngram", type=int, choices=[2, 3], default=2, help="2=bigram, 3=trigram"
    )
    p.add_argument(
        "--length", type=int, default=100, help="生成する文字列の長さ（文字数）"
    )
    p.add_argument(
        "--alltext", default="ALL_TEXT.txt", help="結合済みテキスト ALL_TEXT.txt のパス"
    )
    p.add_argument("--out", default=None, help="出力先ファイル（省略時は標準出力）")
    p.add_argument(
        "--no-newline",
        action="store_true",
        help="出力時に改行文字を削除して横並びにする",
    )
    args = p.parse_args()

    allp = Path(args.alltext)
    if not allp.exists():
        print(
            f"ALL_TEXT.txt が見つかりません: {allp} — 先に scripts/process4/build_all_text.py で作成してください"
        )
        return 2

    alltxt = allp.read_text(encoding="utf-8", errors="replace")
    if not alltxt:
        print(f"ALL_TEXT.txt が空です: {allp}")
        return 2

    result = generate_by_ngram_alltext(alltxt, args.ngram, args.length)
    if args.no_newline:
        result = result.replace("\n", "")

    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
        print(f"生成結果を保存しました: {args.out}")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
