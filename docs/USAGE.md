## 使い方（クイックスタート）

以下は本リポジトリ内でよく使うコマンド例です。プロジェクトのルートに移動して実行してください。

- 全体を順に実行（デフォルト: step1..6、GUI を step2/step3 で表示）

```bash
python3 scripts/run_all.py
```

- 実行前にコマンドを確認する（dry-run）

```bash
python3 scripts/run_all.py --dry-run
```

- GUI を無効にしてヘッドレス実行する（サーバ上など X がない環境向け）

```bash
python3 scripts/run_all.py --gui-steps ""
```

- 一部ステップだけ実行する（例：step1 と step4 のみ）

```bash
python3 scripts/run_all.py --steps 1,4
```

- 乱数シードを固定して再現可能にする（step6 の生成に伝搬）

```bash
python3 scripts/run_all.py --seed 42
```

ログと出力:
- run_all の実行ログは `logs/run_all_YYYYMMDD_HHMMSS.log` に保存されます。
- 各処理スクリプトのCSV は `Output/process2` や `Output/process3` に出力されます。
- run_all による生成（step5/6 の短いサンプル）は `Output/run_all/` に保存されます。

GUI に関する注意:
- `--gui` を使う場合は X サーバーが必要です（リモートの Linux 環境で表示するには X forwarding などを利用してください）。
- 必要な Python パッケージ: `tkinter`（OS パッケージ名は `python3-tk`）、`matplotlib`、`pandas`。Debian/Ubuntu 系の例:

```bash
sudo apt update && sudo apt install -y python3-tk python3-matplotlib python3-pandas
python3 -m pip install --user matplotlib pandas
```

その他:
- `ALL_TEXT.txt` は `scripts/process4/build_all_text.py` で生成されます。大きなテキストファイルは `.gitignore` に入っているため誤ってコミットされません。

---

必要があればこのファイルを README に統合します。
