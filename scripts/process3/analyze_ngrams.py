#!/usr/bin/env python3
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
    lines = text.splitlines()
    norm_lines = [re.sub(r" {2,}", " ", line) for line in lines]
    return "\n".join(norm_lines) + ("\n" if text.endswith("\n") else "")


def char_list(text: str) -> list[str]:
    text = normalize_spaces(text)
    return re.findall(r"[A-Za-z \n]", text)


def ngrams_from_chars(chars: list[str], n: int) -> list[str]:
    return ["".join(chars[i : i + n]) for i in range(len(chars) - n + 1)]


def save_ngram_csv(counter: Counter, total: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "ngram", "count", "ratio"])
        for i, (ng, cnt) in enumerate(counter.most_common(), start=1):
            w.writerow([i, ng, cnt, f"{cnt/total:.6f}"])


def try_show_gui(bigram_csv: Path, trigram_csv: Path, top: int | None) -> None:
    try:
        import tkinter as tk
        import matplotlib

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

    try:
        bg = pd.read_csv(bigram_csv)
        tg = pd.read_csv(trigram_csv)
    except Exception as e:
        print(f"CSV 読み込みに失敗しました: {e}")
        return

    if top:
        bgp = bg.head(top)
        tgp = tg.head(top)
    else:
        bgp = bg
        tgp = tg

    root = tk.Tk()
    root.title("二ッ組・三ッ組出現率")

    # 画面サイズを取得してフィットするように figure サイズを決める
    scr_w = root.winfo_screenwidth()
    scr_h = root.winfo_screenheight()

    # 表示データの件数に応じた幅を計算するが、画面幅の90%を超えないようにする
    n1 = len(bgp)
    n2 = len(tgp)
    # 基本的なバー幅(ピクセル)を設定し、最大幅を画面の90%に制限
    bar_px = 12
    desired_width_px = max(800, int(max(n1, n2) * bar_px))
    max_width_px = int(scr_w * 0.9)
    width_px = min(desired_width_px, max_width_px)

    # 高さは大まかに設定（各プロットに300px）
    height_px = min(int(scr_h * 0.8), 700)

    dpi = 100
    fig_w = max(6, width_px / dpi)
    fig_h = max(4, height_px / dpi)

    fig, axes = plt.subplots(2, 1, figsize=(fig_w, fig_h), constrained_layout=True)

    # ラベルとフォントサイズの調整
    def plot_axis(ax, df, title):
        labels = df["ngram"].astype(str).tolist()
        counts = df["count"].tolist()
        ax.bar(labels, counts)
        ax.set_title(title)
        # ラベルの数が多い場合は小さいフォントと90度回転
        if len(labels) > 20:
            ax.tick_params(axis="x", rotation=90, labelsize=8)
        else:
            ax.tick_params(axis="x", rotation=45, labelsize=10)

    plot_axis(axes[0], bgp, "Bigram (二ッ組)")
    plot_axis(axes[1], tgp, "Trigram (三ッ組)")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=1)

    root.mainloop()


def main() -> int:
    p = argparse.ArgumentParser(description="二ッ組・三ッ組解析を行い CSV を出力します")
    p.add_argument("--src", default="examples/processed", help="処理済みテキストのディレクトリ")
    p.add_argument("--case-sensitive", action="store_true", help="大文字小文字を区別する")
    p.add_argument(
        "--top",
        type=int,
        default=None,
        help="GUI 表示または top CSV の上位 N（省略で全て）",
    )
    p.add_argument(
        "--outdir",
        default="/home/leo0607y/work/numerical_analysis/Output/process3",
        help="出力先ディレクトリ",
    )
    p.add_argument("--gui", action="store_true", help="GUI を表示する（Tk が必要）")
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

    # case-insensitive by default
    if not args.case_sensitive:
        proc_chars = [c.lower() if c != "\n" and c != " " else c for c in chars]
    else:
        proc_chars = chars

    bigrams = ngrams_from_chars(proc_chars, 2)
    trigrams = ngrams_from_chars(proc_chars, 3)

    cb = Counter(bigrams)
    ct = Counter(trigrams)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # save full CSVs
    total_b = sum(cb.values())
    total_t = sum(ct.values())
    bg_csv = outdir / "bigram_freq.csv"
    tg_csv = outdir / "trigram_freq.csv"
    save_ngram_csv(cb, total_b, bg_csv)
    save_ngram_csv(ct, total_t, tg_csv)
    print(f"作成: {bg_csv}")
    print(f"作成: {tg_csv}")

    # save top-N CSVs if top specified
    if args.top:
        save_ngram_csv(
            Counter(dict(cb.most_common(args.top))),
            total_b,
            outdir / f"bigram_freq_top{args.top}.csv",
        )
        save_ngram_csv(
            Counter(dict(ct.most_common(args.top))),
            total_t,
            outdir / f"trigram_freq_top{args.top}.csv",
        )

    if args.gui:
        try_show_gui(bg_csv, tg_csv, args.top)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
