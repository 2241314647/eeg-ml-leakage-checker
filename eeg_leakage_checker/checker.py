from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


SUSPICIOUS_NAME_PARTS = ("label", "target", "class", "outcome", "split", "fold", "subject")
METADATA_DEFAULTS = {"split", "subject_id", "session_id", "trial_id", "window_id", "label"}


@dataclass(frozen=True)
class Finding:
    severity: str
    title: str
    detail: str


@dataclass(frozen=True)
class LeakageReport:
    csv_path: Path
    row_count: int
    split_counts: dict[str, int]
    feature_columns: list[str]
    findings: list[Finding]

    @property
    def risk_level(self) -> str:
        severities = {finding.severity for finding in self.findings}
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        if "low" in severities:
            return "low"
        return "clear"


def generate_demo_csv(path: Path) -> None:
    rng = np.random.default_rng(42)
    rows: list[dict[str, object]] = []
    subjects = [f"S{i:02d}" for i in range(1, 9)]
    splits = {"S01": "train", "S02": "train", "S03": "train", "S04": "train", "S05": "val", "S06": "val", "S07": "test", "S08": "test"}

    for subject in subjects:
        for trial in range(1, 4):
            subject_num = int(subject[1:])
            label = int((subject_num + trial) % 2 == 0)
            base = rng.normal(loc=label * 0.8, scale=0.25, size=5)
            for window in range(1, 5):
                features = base + rng.normal(scale=0.03, size=5)
                rows.append(
                    {
                        "split": splits[subject],
                        "subject_id": subject,
                        "session_id": "session_a",
                        "trial_id": f"T{trial:02d}",
                        "window_id": f"W{window:02d}",
                        "label": label,
                        "alpha_power": round(float(features[0]), 5),
                        "beta_power": round(float(features[1]), 5),
                        "theta_power": round(float(features[2]), 5),
                        "erp_peak_ms": round(float(features[3]), 5),
                        "connectivity_cz_pz": round(float(features[4]), 5),
                        "target_mean_leaky": label,
                    }
                )

    df = pd.DataFrame(rows)

    # Deliberate leakage examples for the demo: one subject crosses splits and one row is duplicated.
    df.loc[(df["subject_id"] == "S05") & (df["trial_id"] == "T01"), "split"] = "train"
    duplicate = df.iloc[[3]].copy()
    duplicate.loc[:, "split"] = "test"
    df = pd.concat([df, duplicate], ignore_index=True)
    df.to_csv(path, index=False)


def analyze_csv(
    csv_path: Path,
    *,
    split_col: str = "split",
    subject_col: str = "subject_id",
    session_col: str = "session_id",
    trial_col: str = "trial_id",
    window_col: str = "window_id",
    label_col: str = "label",
    near_duplicate_threshold: float = 0.999,
) -> LeakageReport:
    df = pd.read_csv(csv_path)
    required = [split_col, subject_col, label_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    metadata = {split_col, subject_col, session_col, trial_col, window_col, label_col}
    feature_columns = [
        col for col in df.columns if col not in metadata and pd.api.types.is_numeric_dtype(df[col])
    ]
    findings: list[Finding] = []

    findings.extend(_check_entity_overlap(df, split_col, subject_col, "subject"))
    for col, label in ((session_col, "session"), (trial_col, "trial"), (window_col, "window")):
        if col in df.columns:
            findings.extend(_check_entity_overlap(df, split_col, col, label))

    identity_cols = [col for col in [subject_col, session_col, trial_col, window_col] if col in df.columns]
    if identity_cols:
        findings.extend(_check_window_identity_overlap(df, split_col, identity_cols))

    if feature_columns:
        findings.extend(_check_exact_feature_duplicates(df, split_col, feature_columns))
        findings.extend(_check_near_duplicates(df, split_col, feature_columns, near_duplicate_threshold))
        findings.extend(_check_suspicious_features(df, label_col, feature_columns))

    split_counts = df[split_col].astype(str).value_counts().sort_index().to_dict()
    return LeakageReport(
        csv_path=csv_path,
        row_count=len(df),
        split_counts={str(k): int(v) for k, v in split_counts.items()},
        feature_columns=feature_columns,
        findings=findings,
    )


def _check_entity_overlap(df: pd.DataFrame, split_col: str, entity_col: str, entity_name: str) -> list[Finding]:
    grouped = df.groupby(entity_col)[split_col].nunique()
    leaked = grouped[grouped > 1].index.astype(str).tolist()
    if not leaked:
        return []
    sample = ", ".join(leaked[:8])
    return [
        Finding(
            "high",
            f"{entity_name.title()} IDs appear in multiple splits",
            f"{len(leaked)} {entity_name} IDs cross split boundaries. Examples: {sample}.",
        )
    ]


def _check_window_identity_overlap(df: pd.DataFrame, split_col: str, identity_cols: list[str]) -> list[Finding]:
    grouped = df.groupby(identity_cols, dropna=False)[split_col].nunique()
    repeated = grouped[grouped > 1]
    if repeated.empty:
        return []
    return [
        Finding(
            "high",
            "Same EEG window identity appears in multiple splits",
            f"{len(repeated)} unique identity keys cross split boundaries using columns: {', '.join(identity_cols)}.",
        )
    ]


def _check_exact_feature_duplicates(df: pd.DataFrame, split_col: str, feature_cols: list[str]) -> list[Finding]:
    feature_hash = pd.util.hash_pandas_object(df[feature_cols], index=False)
    tmp = pd.DataFrame({"feature_hash": feature_hash, "split": df[split_col].astype(str)})
    grouped = tmp.groupby("feature_hash")["split"].nunique()
    duplicate_hashes = grouped[grouped > 1]
    if duplicate_hashes.empty:
        return []
    return [
        Finding(
            "high",
            "Exact feature duplicates cross splits",
            f"{len(duplicate_hashes)} distinct feature rows are present in more than one split.",
        )
    ]


def _check_near_duplicates(
    df: pd.DataFrame, split_col: str, feature_cols: list[str], threshold: float
) -> list[Finding]:
    if len(df) > 2000:
        return [
            Finding(
                "low",
                "Near-duplicate scan skipped",
                "Dataset has more than 2000 rows; use exact hashes or sample the table before near-duplicate scanning.",
            )
        ]

    values = df[feature_cols].to_numpy(dtype=float)
    std = values.std(axis=0)
    std[std == 0] = 1.0
    z = (values - values.mean(axis=0)) / std
    norms = np.linalg.norm(z, axis=1)
    norms[norms == 0] = 1.0
    z = z / norms[:, None]
    splits = df[split_col].astype(str).to_numpy()

    pairs = 0
    for i, j in combinations(range(len(df)), 2):
        if splits[i] == splits[j]:
            continue
        if float(np.dot(z[i], z[j])) >= threshold:
            pairs += 1
            if pairs >= 25:
                break

    if pairs == 0:
        return []
    return [
        Finding(
            "medium",
            "Near-duplicate feature vectors cross splits",
            f"Found at least {pairs} cross-split row pairs with cosine similarity >= {threshold:.4f}.",
        )
    ]


def _check_suspicious_features(df: pd.DataFrame, label_col: str, feature_cols: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    suspicious_names = [
        col
        for col in feature_cols
        if any(part in col.lower() for part in SUSPICIOUS_NAME_PARTS)
        and col.lower() not in METADATA_DEFAULTS
    ]
    if suspicious_names:
        findings.append(
            Finding(
                "medium",
                "Feature names look label- or split-derived",
                "Review these columns before modeling: " + ", ".join(suspicious_names[:12]) + ".",
            )
        )

    if pd.api.types.is_numeric_dtype(df[label_col]):
        label = df[label_col].to_numpy(dtype=float)
        risky_corrs: list[str] = []
        for col in feature_cols:
            values = df[col].to_numpy(dtype=float)
            if np.std(values) == 0 or np.std(label) == 0:
                continue
            corr = float(np.corrcoef(values, label)[0, 1])
            if abs(corr) >= 0.98:
                risky_corrs.append(f"{col} ({corr:.3f})")
        if risky_corrs:
            findings.append(
                Finding(
                    "high",
                    "Feature is almost perfectly correlated with the label",
                    "Possible target leakage columns: " + ", ".join(risky_corrs[:12]) + ".",
                )
            )

    return findings


def build_markdown_report(report: LeakageReport) -> str:
    lines = [
        "# EEG-ML Leakage Check Report",
        "",
        f"- Source CSV: `{report.csv_path}`",
        f"- Rows: {report.row_count}",
        f"- Risk level: **{report.risk_level}**",
        f"- Numeric feature columns checked: {len(report.feature_columns)}",
        "",
        "## Split Counts",
        "",
    ]
    for split, count in report.split_counts.items():
        lines.append(f"- `{split}`: {count}")

    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("No leakage risks were detected by these checks.")
    else:
        for finding in report.findings:
            lines.append(f"### [{finding.severity.upper()}] {finding.title}")
            lines.append("")
            lines.append(finding.detail)
            lines.append("")

    lines.extend(
        [
            "## Recommended Next Steps",
            "",
            "- Prefer subject- or session-grouped train/validation/test splits for EEG decoding.",
            "- Keep preprocessing fit operations inside the training fold only.",
            "- Remove direct label, split, fold, subject, or post-hoc outcome columns from model features.",
            "- Re-run this report after regenerating split assignments.",
            "",
        ]
    )
    return "\n".join(lines)
