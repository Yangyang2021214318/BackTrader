# -*- coding = utf-8 -*-
# @Time: 2026/9/28 12:42
# @Author: Yang Yang
# @File: inspect_data
# @Software: PyCharm


from collections import Counter
from multiprocessing.reduction import duplicate
from pathlib import Path

RAW_DIR = Path(r"D:\A股日线回测\raw_data")
if not RAW_DIR.is_dir():
    raise FileNotFoundError(f"cannot find raw data directory: {RAW_DIR}")

for year in range(2015,2026):
    year_dir = RAW_DIR/str(year)
    if not year_dir.is_dir():
        raise FileNotFoundError(f"cannot find raw data directory: {year_dir}")

    files = sorted(path for path in year_dir.iterdir() if path.is_file() and path.suffix.lower() in (".csv", ".xlsx"))
    dates = [path.name[:8] for path in files]
    invalid_names =[path.name for path in files if not path.name[:8].isdigit() ]

    date_counts = Counter(dates)
    duplicate_dates = [ date for date, count in date_counts.items() if count>1]

    print(
    f"{year}:文件{len(files)}"
    f"日期{len(date_counts)}"
    f"重复日期{len(duplicate_dates)}"
    f"格式{sorted({path.suffix.lower() for path in files})}")

    if invalid_names:
        print(f"  文件名异常示例：{invalid_names[:3]}")

    if duplicate_dates:
        print(f"  重复日期示例：{sorted(duplicate_dates)[:3]}")


