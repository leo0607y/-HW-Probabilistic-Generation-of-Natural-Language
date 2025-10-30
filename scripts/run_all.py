#!/usr/bin/env python3
# Copyright (c) 2025 Reo Yamaguchi
# All rights reserved.
# Contact: reo.yamaguchi0607@gmail.com
from __future__ import annotations
import argparse
import subprocess
import shlex
from datetime import datetime
from pathlib import Path
import sys
import os


def parse_steps(s: str) -> list[int]:
    # accept formats like "1-6" or "1,2,4"
    s = s.strip()
    parts = []
    for token in s.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            parts.extend(range(int(a), int(b) + 1))
        else:
            parts.append(int(token))
    return sorted(set(parts))


def run_cmd(cmd: str, dry_run: bool, log_f):
    print(f"CMD: {cmd}")
    log_f.write(f"CMD: {cmd}\n")
    if dry_run:
        return 0, "(dry-run)"
    try:
        # step2/step3 の GUI 実行時はタイムアウトを設ける（300秒）
        timeout_sec = 500
        proc = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_sec,
        )
        log_f.write(proc.stdout or "")
        log_f.write(proc.stderr or "")
        return proc.returncode, proc.stdout + (
            "\n" + proc.stderr if proc.stderr else ""
        )
    except subprocess.TimeoutExpired as e:
        msg = f"Timeout ({e.timeout}s) for: {cmd}\n"
        log_f.write(msg)
        print(
            f"警告: {msg.strip()}\n--continue-on-error を付ければ次のステップに進みます"
        )
        return 124, msg
    except Exception as e:
        log_f.write(f"Exception while running: {e}\n")
        return 2, str(e)


def main():
    p = argparse.ArgumentParser(
        description="Run full pipeline steps 1..6 (or subset) as an orchestrator"
    )
    p.add_argument(
        "--steps", default="1-6", help="Which steps to run, e.g. 1-6 or 1,2,3"
    )
    p.add_argument(
        "--gui-steps",
        default="2,3",
        help="Which steps to show GUI for (comma separated). Default: 2,3",
    )
    p.add_argument(
        "--top", type=int, default=50, help="Top-N to show in GUI (default 50)"
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing outputs (default is to overwrite)",
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Print commands only, do not execute"
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed to pass to generators (default=random)",
    )
    p.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue to next step when a step fails (default: stop on error)",
    )
    args = p.parse_args()

    steps = parse_steps(args.steps)
    gui_steps = parse_steps(args.gui_steps)
    overwrite = not args.no_overwrite

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"run_all_{now}.log"

    with log_path.open("w", encoding="utf-8") as log_f:
        log_f.write(f"run_all start: {datetime.now().isoformat()}\n")
        log_f.write(
            f"steps={steps} gui_steps={gui_steps} top={args.top} overwrite={overwrite} seed={args.seed}\n"
        )

        base_cmd = sys.executable or "python3"

        for step in steps:
            log_f.write(f"\n--- STEP {step} ---\n")
            cmds = []
            outdir = Path("Output/run_all")
            outdir.mkdir(parents=True, exist_ok=True)
            if step == 1:
                cmd = f"{base_cmd} scripts/process1/process_unprocessed.py"
                if overwrite:
                    cmd += " --overwrite"
                cmds.append(cmd)
            elif step == 2:
                cmd = f"{base_cmd} scripts/process2/analyze_chars.py --top {args.top} --outdir Output/process2"
                if step in gui_steps:
                    cmd += " --gui"
                cmds.append(cmd)
            elif step == 3:
                cmd = f"{base_cmd} scripts/process3/analyze_ngrams.py --top {args.top} --outdir Output/process3"
                if step in gui_steps:
                    cmd += " --gui"
                cmds.append(cmd)
            elif step == 4:
                # build ALL_TEXT.txt
                cmds.append(f"{base_cmd} scripts/process4/build_all_text.py")
                # 文字分布からランダム生成（step4の出力）
                cmds.append(
                    f"{base_cmd} scripts/process4/generate_chars.py --mode text --n 100 --no-newline --out {outdir}/step4_chars.txt"
                )
            elif step == 5:
                # 二ッ組
                cmds.append(
                    f"{base_cmd} scripts/process5/generate_ngrams.py --ngram 2 --length 200 --alltext ALL_TEXT.txt --out {outdir}/step5_ngram2.txt"
                )
                # 三ッ組
                cmds.append(
                    f"{base_cmd} scripts/process5/generate_ngrams.py --ngram 3 --length 200 --alltext ALL_TEXT.txt --out {outdir}/step5_ngram3.txt"
                )
            elif step == 6:
                seed_part = f" --seed {args.seed}" if args.seed is not None else ""
                # 二ッ組Markov
                cmds.append(
                    f"{base_cmd} scripts/process6/generate_markov.py --ngram 2 --length 200 --alltext ALL_TEXT.txt{seed_part} --out {outdir}/step6_markov2.txt"
                )
                # 三ッ組Markov
                cmds.append(
                    f"{base_cmd} scripts/process6/generate_markov.py --ngram 3 --length 200 --alltext ALL_TEXT.txt{seed_part} --out {outdir}/step6_markov3.txt"
                )
            else:
                log_f.write(f"Unknown step: {step}\n")

            for cmd in cmds:
                rc, output = run_cmd(cmd, args.dry_run, log_f)
                log_f.write(f"RETURNCODE: {rc}\n")
                if rc != 0:
                    log_f.write(f"STEP {step} failed (rc={rc})\n")
                    print(f"STEP {step} failed (rc={rc}) — see {log_path}")
                    if not args.continue_on_error:
                        log_f.write("Aborting due to failure\n")
                        return rc
                    else:
                        log_f.write("Continuing despite failure as requested\n")

        log_f.write(f"run_all finished: {datetime.now().isoformat()}\n")

    print(f"run_all finished. Log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
