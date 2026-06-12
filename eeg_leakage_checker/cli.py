from __future__ import annotations

import argparse
from pathlib import Path

from .checker import analyze_csv, build_markdown_report, generate_demo_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="eeg-leakage-checker",
        description="Audit EEG/BCI ML split tables for common leakage risks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Generate a simulated leaky EEG feature table and report.")
    demo.add_argument("--data-out", type=Path, default=Path("examples/simulated_leaky_eeg_features.csv"))
    demo.add_argument("--report-out", type=Path, default=Path("reports/demo_leakage_report.md"))

    analyze = sub.add_parser("analyze", help="Analyze a CSV containing split and EEG feature metadata.")
    analyze.add_argument("csv", type=Path)
    analyze.add_argument("--report-out", type=Path, default=Path("reports/leakage_report.md"))
    analyze.add_argument("--split-col", default="split")
    analyze.add_argument("--subject-col", default="subject_id")
    analyze.add_argument("--session-col", default="session_id")
    analyze.add_argument("--trial-col", default="trial_id")
    analyze.add_argument("--window-col", default="window_id")
    analyze.add_argument("--label-col", default="label")
    analyze.add_argument("--near-duplicate-threshold", type=float, default=0.999)

    args = parser.parse_args(argv)

    if args.command == "demo":
        args.data_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        generate_demo_csv(args.data_out)
        result = analyze_csv(args.data_out)
        args.report_out.write_text(build_markdown_report(result), encoding="utf-8")
        print(f"Wrote demo data: {args.data_out}")
        print(f"Wrote report: {args.report_out}")
        print(f"Risk level: {result.risk_level}")
        return 0

    if args.command == "analyze":
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        result = analyze_csv(
            args.csv,
            split_col=args.split_col,
            subject_col=args.subject_col,
            session_col=args.session_col,
            trial_col=args.trial_col,
            window_col=args.window_col,
            label_col=args.label_col,
            near_duplicate_threshold=args.near_duplicate_threshold,
        )
        args.report_out.write_text(build_markdown_report(result), encoding="utf-8")
        print(f"Wrote report: {args.report_out}")
        print(f"Risk level: {result.risk_level}")
        return 0

    return 2
