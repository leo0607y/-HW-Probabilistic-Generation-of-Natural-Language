#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def build_followers(alltext: str, n: int) -> Dict[str, List[str]]:
    """Build a mapping (n-1)-gram -> list of following characters (with repetition).

    Example: n=2 (bigram) -> keys are single chars, values are list of following chars.
    """
    M = len(alltext)
    followers: Dict[str, List[str]] = defaultdict(list)
    if M < n:
        return followers
    for i in range(M - n + 1):
        key = alltext[i : i + n - 1]
        follow = alltext[i + n - 1]
        followers[key].append(follow)
    return followers


def generate_markov(alltext: str, n: int, length: int, seed: int | None = None) -> str:
    if seed is not None:
        random.seed(seed)

    followers = build_followers(alltext, n)
    keys = list(followers.keys())
    if not keys:
        return ""

    # pick initial key randomly
    key = random.choice(keys)
    out = list(key)

    while len(out) < length:
        if key in followers and followers[key]:
            next_char = random.choice(followers[key])
        else:
            # fallback: pick random key and take one of its followers if available
            fk = random.choice(keys)
            next_char = random.choice(followers.get(fk, [" "]))
        out.append(next_char)
        # update key to last n-1 chars
        key = "".join(out[-(n - 1) :])

    return "".join(out[:length])


def main() -> int:
    p = argparse.ArgumentParser(
        description="手順6: (n-1)-gram->followers 辞書を使った高速生成 (Markov 風)"
    )
    p.add_argument(
        "--ngram", type=int, choices=[2, 3], default=2, help="2=bigram,3=trigram"
    )
    p.add_argument("--length", type=int, default=200, help="生成する文字数")
    p.add_argument("--alltext", default="ALL_TEXT.txt", help="結合済みテキストのパス")
    p.add_argument("--seed", type=int, default=None, help="乱数シード（再現性のため）")
    p.add_argument("--out", default=None, help="出力ファイル（省略で stdout）")
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

    result = generate_markov(alltxt, args.ngram, args.length, args.seed)
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
