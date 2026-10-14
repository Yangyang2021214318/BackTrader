# -*- coding = utf-8 -*-
# @Time: 2026/9/28 17:04
# @Author: Yang Yang
# @File: build_parquet
# @Software: PyCharm
import hashlib
import json
from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = Path(r"D:\A股日线回测\raw_data")
YEARS_TO_BUILD = range(2015, 2026)

# 顺序：原始文件数、保留的日期文件数、重复日期数
EXPECTED_COUNTS = {
    2015: (244, 244, 0),
    2016: (244, 244, 0),
    2017: (244, 244, 0),
    2018: (243, 243, 0),
    2019: (385, 244, 141),
    2020: (243, 243, 0),
    2021: (243, 243, 0),
    2022: (242, 242, 0),
    2023: (242, 242, 0),
    2024: (242, 242, 0),
    2025: (243, 243, 0),
}


PRICE_COLUMNS = {
    "开盘价（元）": "open",
    "最高价（元）": "high",
    "最低价（元）": "low",
    "收盘价（元）": "close",
}

ISSUE_COLUMNS = (
    "issue_date",
    "issue_code",
    "issue_duplicate_code",
    "issue_price",
    "issue_volume",
    "issue_factor",
)

def file_sha256(path):
    with path.open(mode="rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def convert_one(path):
    source_hash = file_sha256(path)

    df = pd.read_excel(
        path,
        engine="openpyxl",
        dtype={"股票代码": "string"},
    )
    required = {
        "交易日期", "股票代码", "股票名称",
        *PRICE_COLUMNS, "成交量（手）", "复权因子",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} 缺少字段：{sorted(missing)}")

    df["date"] = pd.to_datetime(df["交易日期"], errors="coerce").dt.normalize()
    df["symbol"] = df["股票代码"].astype("string").str.strip()

    parse_errors = 0
    for column in df.columns:
        if column in {"交易日期", "股票代码", "股票名称", "date", "symbol"}:
            continue
        converted = pd.to_numeric(df[column], errors="coerce")
        parse_errors += int((df[column].notna() & converted.isna()).sum())
        df[column] = converted

    for original, standard in PRICE_COLUMNS.items():
        df[standard] = df[original]

    df["source_file"] = path.name
    expected_date = pd.Timestamp(path.name[:8])
    prices = df[["open", "high", "low", "close"]]

    df["issue_date"] = df["date"].isna() | df["date"].ne(expected_date)
    df["issue_code"] = ~df["symbol"].str.fullmatch(r"\d{6}").fillna(False)
    df["issue_duplicate_code"] = (
        df["symbol"].notna() & df["symbol"].duplicated(keep=False)
    )
    df["issue_price"] = (
        prices.isna().any(axis=1)
        | prices.le(0).any(axis=1)
        | df["open"].lt(df["low"])
        | df["open"].gt(df["high"])
        | df["close"].lt(df["low"])
        | df["close"].gt(df["high"])
    )

    volume = df["成交量（手）"]
    factor = df["复权因子"]
    df["issue_volume"] = volume.isna() | volume.lt(0)
    df["issue_factor"] = factor.isna() | factor.le(0)
    df["has_issue"] = df[list(ISSUE_COLUMNS)].any(axis=1)

    summary = {
        "source_file": path.name,
        "source_sha256": source_hash,
        "rows": len(df),
        "numeric_parse_errors": parse_errors,
        "rows_with_any_issue": int(df["has_issue"].sum()),
        **{column: int(df[column].sum()) for column in ISSUE_COLUMNS},
    }
    return df, summary

def build_year(year):
    output_dir = PROJECT_DIR / "data" / "processed" / "a_share" / str(year)
    year_dir = RAW_DIR / str(year)
    raw_files = sorted(year_dir.glob("*.xlsx"))

    files_by_date = {}
    for path in raw_files:
        date_text = path.name[:8]
        if len(date_text) != 8 or not date_text.isdigit():
            raise ValueError(f"文件名没有以 8 位日期开头：{path.name}")
        files_by_date.setdefault(date_text, []).append(path)

    files = []
    duplicate_report = []

    for date_text, same_day_files in sorted(files_by_date.items()):
        if len(same_day_files) > 1:
            hashes = {file_sha256(path) for path in same_day_files}
            if len(hashes) != 1:
                raise RuntimeError(f"{date_text} 的重复文件内容不同，停止转换")

            duplicate_report.append({
                "date": date_text,
                "sha256": next(iter(hashes)),
                "kept": same_day_files[0].name,
                "skipped": [path.name for path in same_day_files[1:]],
            })

        files.append(same_day_files[0])

    actual_counts = (len(raw_files), len(files), len(duplicate_report))
    if actual_counts != EXPECTED_COUNTS[year]:
        raise RuntimeError(
            f"{year} 年文件数量不符："
            f"预期 {EXPECTED_COUNTS[year]}，实际 {actual_counts}"
        )

    print(
        f"\n{year}: 原始 {len(raw_files)} 个，"
        f"保留 {len(files)} 个，"
        f"重复日期 {len(duplicate_report)} 个"
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report = []

    for month in range(1, 13):
        month_text = f"{month:02d}"
        month_files = [
            path for path in files
            if path.name[4:6] == month_text
        ]
        if not month_files:
            raise RuntimeError(f"{year}-{month_text} 没有找到文件")

        frames = []
        for path in month_files:
            frame, summary = convert_one(path)
            frames.append(frame)
            report.append(summary)

        monthly_data = pd.concat(frames, ignore_index=True)
        parquet_path = output_dir / f"{year}{month_text}.parquet"
        monthly_data.to_parquet(parquet_path, engine="pyarrow", index=False)

        saved_rows = len(pd.read_parquet(parquet_path, columns=["date"]))
        if saved_rows != len(monthly_data):
            raise RuntimeError(f"{parquet_path.name} 写入与读回行数不一致")

        print(
            f"{year}-{month_text}: 文件 {len(month_files)} 个，"
            f"写入 {len(monthly_data)} 行，读回 {saved_rows} 行"
        )
        del frames, monthly_data

    if len(report) != len(files):
        raise RuntimeError(f"{year} 年有文件未按月处理")

    (output_dir / "quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "duplicate_report.json").write_text(
        json.dumps(duplicate_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    issue_rows = sum(item["rows_with_any_issue"] for item in report)
    parse_errors = sum(item["numeric_parse_errors"] for item in report)
    print(
        f"{year} 年完成：文件 {len(report)} 个，"
        f"记录 {sum(item['rows'] for item in report)} 行，"
        f"异常行 {issue_rows}，数值解析错误 {parse_errors}"
    )

    if issue_rows or parse_errors:
        raise RuntimeError(
            f"{year} 年发现异常；请查看 {output_dir / 'quality_report.json'}"
        )


if __name__ == "__main__":
    for year in YEARS_TO_BUILD:
        build_year(year)














