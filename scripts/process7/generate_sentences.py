#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
"""
STEP7: 単語単位のMarkovモデルによる英文生成＋コナン・ドイルらしさ語彙優先
"""
from __future__ import annotations
import argparse
import random
import re
from pathlib import Path
from collections import defaultdict, Counter

# コナン・ドイルらしさ語彙・フレーズ例
DOYLE_WORDS = [
    "Holmes",
    "Watson",
    "detective",
    "mystery",
    "London",
    "Scotland Yard",
    "crime",
    "clue",
    "evidence",
    "case",
    "client",
    "baker street",
    "deduction",
    "adventure",
    "remarked",
    "observe",
    "peculiar",
    "extraordinary",
    "solution",
    "investigation",
    "suspect",
    "villain",
    "inquiry",
    "exclaimed",
    "elementary",
]
DOYLE_PHRASES = [
    "My dear Watson",
    "It is elementary",
    "I deduced",
    "The case was peculiar",
    "Scotland Yard",
    "Baker Street",
    "Holmes remarked",
    "The client arrived",
]

# 英文の区切り（簡易）
SENTENCE_END = re.compile(r"[.!?]")
WORD_SPLIT = re.compile(r"\b\w+\b|[.,!?;:\-']")


def tokenize(text: str) -> list[str]:
    # 単語・記号単位で分割
    return WORD_SPLIT.findall(text)


def build_markov(words: list[str], n: int = 2) -> dict:
    # (n-1)-gram -> 次の単語リスト
    markov = defaultdict(list)
    for i in range(len(words) - n):
        key = tuple(words[i : i + n - 1])
        next_word = words[i + n - 1]
        markov[key].append(next_word)
    return markov


def generate_sentence(markov: dict, length: int = 20, seed: int | None = None) -> str:
    if seed is not None:
        random.seed(seed)
    keys = list(markov.keys())
    # コナン・ドイル語彙・フレーズを優先的に開始語に
    start_candidates = [k for k in keys if any(w in DOYLE_WORDS for w in k)]
    key = random.choice(start_candidates) if start_candidates else random.choice(keys)
    out = list(key)
    for _ in range(length - len(key)):
        nexts = markov.get(tuple(out[-(len(key)) :]), [])
        # らしさ語彙・フレーズを優先
        doyle_nexts = [w for w in nexts if w in DOYLE_WORDS]
        if doyle_nexts:
            next_word = random.choice(doyle_nexts)
        elif nexts:
            next_word = random.choice(nexts)
        else:
            next_word = random.choice(DOYLE_WORDS)
        out.append(next_word)
    # 句読点・大文字補正
    sentence = " ".join(out)
    sentence = (
        sentence.replace(" .", ".")
        .replace(" ,", ",")
        .replace(" !", "!")
        .replace(" ?", "?")
    )
    sentence = sentence[0].upper() + sentence[1:]
    return sentence


def main():
    p = argparse.ArgumentParser(
        description="STEP7: 単語Markov＋コナン・ドイル語彙優先 英文生成"
    )
    p.add_argument("--alltext", default="ALL_TEXT.txt", help="学習用テキスト")
    p.add_argument(
        "--ngram", type=int, default=2, help="n-gramのn (2=bigram, 3=trigram)"
    )
    p.add_argument("--length", type=int, default=30, help="生成する単語数")
    p.add_argument("--num", type=int, default=5, help="生成する文の数")
    p.add_argument("--seed", type=int, default=None, help="乱数シード")
    p.add_argument("--out", default=None, help="出力ファイル (省略で標準出力)")
    args = p.parse_args()

    allp = Path(args.alltext)
    if not allp.exists():
        print(f"ALL_TEXT.txt が見つかりません: {allp}")
        return 2
    text = allp.read_text(encoding="utf-8", errors="replace")
    # 1行ごとに分割し、単語化
    words = []
    for line in text.splitlines():
        words.extend(tokenize(line))
    if not words:
        print("単語が抽出できません")
        return 2
    markov = build_markov(words, n=args.ngram)
    results = []
    for i in range(args.num):
        sent = generate_sentence(markov, length=args.length, seed=args.seed)
        results.append(sent)
    out_text = "\n".join(results)
    if args.out:
        Path(args.out).write_text(out_text, encoding="utf-8")
        print(f"生成結果を保存しました: {args.out}")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
