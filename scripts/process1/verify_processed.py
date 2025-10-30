#!/usr/bin/env python3
"""
processed 出力の検証スクリプト (process1 フォルダ版)

目的:
 - `Unprocessed/` 以下の各 `*.txt` に対して、対応する
   `examples/processed/{basename}_processed.txt` が存在すること
 - 出力ファイルが許可された文字のみ (英字 A-Z/a-z、空白、改行) で構成されていること

使い方:
  python3 scripts/process1/verify_processed.py --src Unprocessed --dst examples/processed

日本語コメントは自然で読みやすい表現を心がけています。
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
import sys


# 許可された文字: 英字 (大文字/小文字)、半角スペース、改行のみ
RE_ALLOWED = re.compile(r"^[A-Za-z \n]*$", re.MULTILINE)


def check_file_allowed(path: Path) -> tuple[bool, str | None]:
    """ファイルが許可文字のみで構成されているかチェックする。

    戻り値: (ok, sample_of_bad_lines)
    """
    txt = path.read_text(encoding="utf-8", errors="replace")
    if RE_ALLOWED.match(txt):
        return True, None

    # 問題がある場合、最初に不許可文字を含む行を探して返す
    for i, line in enumerate(txt.splitlines(), start=1):
        if not RE_ALLOWED.match(line + "\n"):
            # その行の不許可文字を抽出（最大表示幅を制限）
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
        print(f"ソースディレクトリが見つかりません: {src_dir}")
        return 2
    if not dst_dir.is_dir():
        print(f"出力ディレクトリが見つかりません: {dst_dir}")
        return 2

    src_files = sorted(src_dir.glob("*.txt"))
    if not src_files:
        print(f"ソースにテキストファイルが見つかりません: {src_dir}")
        return 2

    overall_ok = True
    # 各ソースに対する期待される出力ファイル名をチェック
    for s in src_files:
        expected = dst_dir / f"{s.stem}_processed.txt"
        if not expected.exists():
            print(f"Missing: {expected} (対応する処理済みファイルがありません)")
            overall_ok = False
            continue

        ok, sample = check_file_allowed(expected)
        if not ok:
            print(f"NG: {expected} に不許可文字があります -> {sample}")
            overall_ok = False
        else:
            # 見た目の簡易確認: 元ファイルに数値があればそれが消えているかも見る
            s_text = s.read_text(encoding="utf-8", errors="replace")
            has_digits = bool(re.search(r"\d", s_text))
            if has_digits:
                dst_text = expected.read_text(encoding="utf-8", errors="replace")
                if re.search(r"\d", dst_text):
                    print(f"警告: {expected} に数字が残っています (元: 数字あり)" )
                    overall_ok = False
                else:
                    # 良い兆候: 数字が消えている
                    print(f"OK: {expected} （許可文字のみ、数字は除去済）")
            else:
                print(f"OK: {expected} （許可文字のみ）")

    if overall_ok:
        print("\n検証に成功しました: processed 出力は期待どおりです。")
        return 0
    else:
        print("\n検証に失敗しました。上のメッセージを確認してください。")
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
