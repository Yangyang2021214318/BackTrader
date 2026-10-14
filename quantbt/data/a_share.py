# -*- coding = utf-8 -*-
# @Time: 2026/10/4 13:15
# @Author: Yang Yang
# @File: a_share
# @Software: PyCharm

from pathlib import Path
import pandas as pd

DATA_ROOT = (Path(__file__).resolve().parents[2]/'data'/'processed'/'a_share')
COLUMNS =["date","symbol","open","high","low","close","成交量（手）"]

def load_a_share_bars(symbol,start,end):
    if not isinstance(symbol,str) or len(symbol)!=6 or not symbol.isdigit():
        raise ValueError('symbol must be a valid symbol')

    start_date = pd.Timestamp(start).normalize()
    end_date = pd.Timestamp(end).normalize()
    if start_date > end_date:
        raise ValueError('start date must be before end date')

    parts =[]
    for month in pd.period_range(start_date, end_date,freq='M'):
        path = (DATA_ROOT/str(month.year)/
                f"{month.year}{month.month:02d}.parquet")

        if not path.is_file():
            raise FileNotFoundError(path)

        monthly = pd.read_parquet(path,columns=COLUMNS)

        selected = monthly.loc[monthly['symbol'].eq(symbol)
        & monthly['date'].between(start_date,end_date)]

        if not selected.empty:
            parts.append(selected)

    if not parts:
        raise ValueError('no data found')

    bars = pd.concat(parts, ignore_index=True).sort_values("date")

    if bars["date"].duplicated().any():
        raise ValueError('duplicate date found')

    bars["volume"] = bars["成交量（手）"]*100
    bars["openinterest"] = 0
    bars = bars.set_index("date")
    bars.index.name = "datetime"

    return bars[["open","high","low","close","volume","openinterest"]].copy()

if __name__ == '__main__':
    sample = load_a_share_bars("000001","2025-01-01","2025-01-31")
    print(f"记录数：{len(sample)}")
    print(f"首日：{sample.index.min().date()}")
    print(f"末日：{sample.index.max().date()}")
    print(f"字段：{sample.columns.tolist()}")
    print(sample.head(2))
















