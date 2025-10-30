#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import re
import csv
import sys


def read_all_texts(src_dir: Path) -> str:
    parts = []
    for p in sorted(src_dir.glob("*_processed.txt")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "".join(parts)


def normalize_spaces(text: str) -> str:
    # 連続する半角スペースを 1 つにまとめる（改行はそのまま）
    # 行ごとに処理して改行を保持する
    lines = text.splitlines()
    norm_lines = [re.sub(r" {2,}", " ", line) for line in lines]
    # preserve trailing newline if present
    return "\n".join(norm_lines) + ("\n" if text.endswith("\n") else "")


def char_list(text: str) -> list[str]:
    # テキスト全体を正規化してから、有効な文字（A-Z, a-z, 半角スペース, 改行）を抽出
    text = normalize_spaces(text)
    return re.findall(r"[A-Za-z \n]", text)


def print_table(counter: Counter, total: int, top: int, title: str) -> None:
    print(title)
    print(f"総文字数: {total}")
    print("順位\t文字\t出現数\t割合")
    for i, (ch, cnt) in enumerate(counter.most_common(top), start=1):
        label = ch
        if ch == "\n":
            label = "\\n"
        elif ch == " ":
            label = "space"
        print(f"{i}\t{label}\t{cnt}\t{cnt/total:.6f}")


def save_csv(counter: Counter, total: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "char", "count", "ratio"])
        for i, (ch, cnt) in enumerate(counter.most_common(), start=1):
            label = ch if ch != "\n" else "\\n"
            if ch == " ":
                label = "space"
            w.writerow([i, label, cnt, f"{cnt/total:.6f}"])


def try_plot(counter: Counter, path: Path, top: int, title: str) -> None:
    try:
        import matplotlib

        # plot を保存する用途のときは Agg を使う
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    items = counter.most_common(top)
    labels = [
        ("\\n" if ch == "\n" else "space" if ch == " " else ch) for ch, c in items
    ]
    values = [c for ch, c in items]
    plt.figure(figsize=(max(6, len(labels) * 0.3), 4))
    plt.bar(labels, values)
    plt.title(title)
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path)
    plt.close()


def try_show_gui(csv_paths: list[Path]) -> None:
    """CSV を読み込んで、Tkinter ウィンドウに 3 つの棒グラフを横並びで表示する。

    この関数はユーザーが --gui を指定した場合に呼ばれる。表示には matplotlib の
    TkAgg と Tkinter を使用する。X サーバーがない環境では失敗することがある。
    """
    try:
        import tkinter as tk
        import matplotlib

        # GUI 表示では TkAgg を使うよう明示する（Qt を使わない）
        matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        import pandas as pd
    except Exception as e:
        print(f"GUI 表示を行えません: {e}")
        print(
            "必要なパッケージが足りない可能性があります。Linux (Debian/Ubuntu) なら次を試してください:"
        )
        print(
            "  sudo apt update && sudo apt install -y python3-tk python3-matplotlib python3-pandas"
        )
        print(
            "または pip によるインストール: python3 -m pip install --user matplotlib pandas"
        )
        return

    # 読み込み
    datas = []
    titles = []
    for p in csv_paths:
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"CSV 読み込み失敗: {p} -> {e}")
            return
        datas.append(df)
        titles.append(p.stem)

    # Tk ウィンドウ
    root = tk.Tk()
    root.title("文字出現率（大/小/区別なし）")

    # 4 つの CSV を受け取ることを想定しているので、列数に応じてプロットを作る
    n = len(datas)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]
    for ax, df, title in zip(axes, datas, titles):
        # 上位 30 を表示
        top_n = df.head(30)
        labels = top_n["char"].astype(str).tolist()
        counts = top_n["count"].tolist()
        ax.bar(labels, counts)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=1)

    # ウィンドウを表示
    root.mainloop()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="examples/processed")
    p.add_argument("--top", type=int, default=50)
    p.add_argument("--plot", action="store_true")
    p.add_argument(
        "--gui",
        action="store_true",
        help="CSV を使ってポップアップ的にグラフを表示する（Tk が必要）",
    )
    p.add_argument(
        "--outdir",
        default="/home/leo0607y/work/numerical_analysis/Output/process2",
        help="CSV 出力先ディレクトリ",
    )
    args = p.parse_args()

    src = Path(args.src)
    if not src.is_dir():
        print(f"ソースディレクトリが見つかりません: {src}")
        return 2

    text = read_all_texts(src)
    chars = char_list(text)
    if not chars:
        print(f"処理済みファイルが見つからないか文字が抽出できません: {src}")
        return 2

    total = len(chars)
    cs = Counter(chars)
    lower_chars = [c.lower() if c != "\n" and c != " " else c for c in chars]
    ci = Counter(lower_chars)
    print_table(cs, total, args.top, "文字出現率（大文字小文字を区別）")
    print()
    print_table(ci, total, args.top, "文字出現率（大文字小文字を区別しない）")

    # 大文字のみ / 小文字のみ / 大小区別なし の CSV を作成
    upper_cs = Counter({ch: cnt for ch, cnt in cs.items() if ch.isupper()})
    lower_cs = Counter({ch: cnt for ch, cnt in cs.items() if ch.islower()})
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    up_path = outdir / "char_freq_uppercase.csv"
    low_path = outdir / "char_freq_lowercase.csv"
    ci_path = outdir / "char_freq_case_insensitive.csv"

    save_csv(upper_cs, total, up_path)
    print(f"作成: {up_path}")
    save_csv(lower_cs, total, low_path)
    print(f"作成: {low_path}")
    save_csv(ci, total, ci_path)
    print(f"作成: {ci_path}")

    # 既存の case-sensitive CSV も出力しておく
    save_csv(cs, total, outdir / "char_freq_case_sensitive.csv")

    # プロット画像は GUI 以外で必要な場合にのみ出力
    if args.plot and not args.gui:
        try_plot(
            cs,
            outdir / "char_freq_case_sensitive.png",
            args.top,
            "文字出現率（区別あり）",
        )
        try_plot(
            ci,
            outdir / "char_freq_case_insensitive.png",
            args.top,
            "文字出現率（区別なし）",
        )

    if args.gui:
        # GUI 表示を試みる（失敗したらメッセージを出す）
        csvs = [up_path, low_path, ci_path]
        try_show_gui(csvs)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
