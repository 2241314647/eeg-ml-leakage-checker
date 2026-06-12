# EEG-ML Leakage Checker

A compact, locally runnable Python utility for finding common EEG/BCI machine-learning data leakage risks in tabular feature exports.

It checks for:

- subject, session, trial, and window IDs that appear in multiple splits
- exact duplicate feature rows crossing train/validation/test boundaries
- near-duplicate feature vectors across splits
- suspicious feature names such as target-, label-, fold-, split-, or subject-derived columns
- numeric features that are almost perfectly correlated with the target label

The goal is to catch avoidable leakage before training EEG classifiers, especially when using overlapping windows, subject-level data, repeated sessions, or notebook-generated features.

## Install

```powershell
cd "D:\Codex 自动化\eeg-github-projects\eeg-ml-leakage-checker"
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run the demo

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker demo
```

This writes:

- `examples/simulated_leaky_eeg_features.csv`
- `reports/demo_leakage_report.md`

## Analyze your own CSV

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker analyze path\to\eeg_features.csv --report-out reports\my_report.md
```

Expected default columns:

- `split`
- `subject_id`
- `session_id`
- `trial_id`
- `window_id`
- `label`

You can override the column names:

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker analyze features.csv --subject-col participant --label-col y
```

## Input Format

Use one row per EEG epoch/window/trial. Metadata columns describe how the row was split; numeric columns not listed as metadata are treated as model features.

```csv
split,subject_id,session_id,trial_id,window_id,label,alpha_power,beta_power
train,S01,session_a,T01,W01,1,0.54,0.21
test,S01,session_a,T01,W02,1,0.55,0.22
```

## Notes

This utility is a preflight audit, not a statistical guarantee. It is most useful before model training, after split generation, and after feature engineering. For EEG/BCI work, the highest-risk pattern is often allowing a subject, session, trial, or overlapping time window to appear in both training and evaluation data.
