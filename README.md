# EEG-ML Leakage Checker

English | [中文](#中文说明)

A compact Python utility for finding common EEG/BCI machine-learning data leakage risks in tabular feature exports.

It helps you check whether your train/validation/test split accidentally shares subjects, sessions, trials, windows, duplicate feature rows, or label-derived columns across splits.

## What It Checks

- Subject, session, trial, and window IDs that appear in multiple splits
- Exact duplicate feature rows crossing train/validation/test boundaries
- Near-duplicate feature vectors across splits
- Suspicious feature names such as target, label, fold, split, or subject-derived columns
- Numeric features that are almost perfectly correlated with the target label

The goal is to catch avoidable leakage before training EEG classifiers, especially when using overlapping windows, subject-level data, repeated sessions, or notebook-generated feature tables.

## Download

Option 1: clone with Git.

```bash
git clone https://github.com/2241314647/eeg-ml-leakage-checker.git
cd eeg-ml-leakage-checker
```

Option 2: download ZIP from GitHub.

1. Open <https://github.com/2241314647/eeg-ml-leakage-checker>
2. Click **Code** -> **Download ZIP**
3. Unzip the file
4. Open a terminal in the unzipped `eeg-ml-leakage-checker` folder

## Install

Python 3.10 or newer is recommended.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

macOS or Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

The `cd` command is not shown with a fixed path because each user may download the project to a different folder. Run the install commands from inside your local `eeg-ml-leakage-checker` folder.

## Run the Demo

Windows PowerShell:

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker demo
```

macOS or Linux:

```bash
./.venv/bin/python -m eeg_leakage_checker demo
```

This writes:

- `examples/simulated_leaky_eeg_features.csv`
- `reports/demo_leakage_report.md`

Open the Markdown report to see the leakage findings.

## Analyze Your Own CSV

Windows PowerShell:

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker analyze path\to\eeg_features.csv --report-out reports\my_report.md
```

macOS or Linux:

```bash
./.venv/bin/python -m eeg_leakage_checker analyze path/to/eeg_features.csv --report-out reports/my_report.md
```

Expected default columns:

- `split`
- `subject_id`
- `session_id`
- `trial_id`
- `window_id`
- `label`

You can override column names when your CSV uses different headers:

```bash
./.venv/bin/python -m eeg_leakage_checker analyze features.csv --subject-col participant --label-col y
```

## Input Format

Use one row per EEG epoch, window, or trial. Metadata columns describe how the row was split. Numeric columns not listed as metadata are treated as model features.

```csv
split,subject_id,session_id,trial_id,window_id,label,alpha_power,beta_power
train,S01,session_a,T01,W01,1,0.54,0.21
test,S01,session_a,T01,W02,1,0.55,0.22
```

## Notes

This utility is a preflight audit, not a statistical guarantee. It is most useful before model training, after split generation, and after feature engineering. For EEG/BCI work, the highest-risk pattern is often allowing a subject, session, trial, or overlapping time window to appear in both training and evaluation data.

---

## 中文说明

一个轻量级 Python 工具，用于检查 EEG/BCI 机器学习特征表中常见的数据泄漏风险。

它可以帮助你确认训练集、验证集、测试集之间是否意外共享了被试、session、trial、window、重复特征行，或者由标签派生出来的特征列。

## 检查内容

- 同一个被试、session、trial 或 window 是否出现在多个数据划分中
- 完全相同的特征行是否跨越训练集、验证集、测试集
- 高度相似的近重复特征向量是否跨越数据划分
- 可疑特征名，例如 target、label、fold、split、subject 等派生列
- 与目标标签几乎完全相关的数值特征

这个工具的目标是在训练 EEG 分类模型前，尽早发现可以避免的数据泄漏问题，尤其适用于重叠时间窗、被试级数据、重复 session、Notebook 导出的特征表等场景。

## 下载

方式 1：使用 Git 克隆。

```bash
git clone https://github.com/2241314647/eeg-ml-leakage-checker.git
cd eeg-ml-leakage-checker
```

方式 2：从 GitHub 下载 ZIP。

1. 打开 <https://github.com/2241314647/eeg-ml-leakage-checker>
2. 点击 **Code** -> **Download ZIP**
3. 解压 ZIP 文件
4. 在解压后的 `eeg-ml-leakage-checker` 文件夹中打开终端

## 安装

建议使用 Python 3.10 或更新版本。

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

macOS 或 Linux：

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

这里不写固定的 `cd` 本机路径，因为每个用户下载项目的位置都不同。请先进入你本地的 `eeg-ml-leakage-checker` 文件夹，再运行上面的安装命令。

## 运行示例

Windows PowerShell：

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker demo
```

macOS 或 Linux：

```bash
./.venv/bin/python -m eeg_leakage_checker demo
```

运行后会生成：

- `examples/simulated_leaky_eeg_features.csv`
- `reports/demo_leakage_report.md`

打开 Markdown 报告即可查看检测到的数据泄漏风险。

## 分析自己的 CSV

Windows PowerShell：

```powershell
.\.venv\Scripts\python -m eeg_leakage_checker analyze path\to\eeg_features.csv --report-out reports\my_report.md
```

macOS 或 Linux：

```bash
./.venv/bin/python -m eeg_leakage_checker analyze path/to/eeg_features.csv --report-out reports/my_report.md
```

默认需要以下列名：

- `split`
- `subject_id`
- `session_id`
- `trial_id`
- `window_id`
- `label`

如果你的 CSV 使用了不同列名，可以通过参数覆盖：

```bash
./.venv/bin/python -m eeg_leakage_checker analyze features.csv --subject-col participant --label-col y
```

## 输入格式

每一行代表一个 EEG epoch、window 或 trial。元数据列用于描述这一行属于哪个数据划分；不属于元数据列的数值列会被当作模型特征检查。

```csv
split,subject_id,session_id,trial_id,window_id,label,alpha_power,beta_power
train,S01,session_a,T01,W01,1,0.54,0.21
test,S01,session_a,T01,W02,1,0.55,0.22
```

## 说明

这个工具用于训练前的快速审查，不是统计意义上的完整保证。建议在生成数据划分后、特征工程后、模型训练前运行。对于 EEG/BCI 任务，最常见的高风险问题是同一个被试、session、trial 或重叠时间窗同时出现在训练集和评估集里。
