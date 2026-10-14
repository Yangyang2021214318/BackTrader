# -*- coding = utf-8 -*-
# @Time: 2026/10/10 12:19
# @Author: Yang Yang
# @File: inspect_adjustment_factor
# @Software: PyCharm

from pathlib import Path
import pandas as pd
import numpy as np

from quantbt.data.a_share import DATA_ROOT
from scripts.build_parquet import PROJECT_DIR

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_DIR / "data"/"processed"/"a_share"

SYMBOL ="000001"
YEAR =2025
FACTOR_COLUMN ="复权因子"

def main():
    parts = []
    for month in range(1,13):
        path = DATA_ROOT/str(YEAR)/f"{YEAR}{month:02d}.parquet"

        monthly = pd.read_parquet(path, columns=["date","symbol","open","close",FACTOR_COLUMN])
        selected = monthly.loc[monthly["symbol"].eq(SYMBOL)].copy()
        parts.append(selected)

    bars = (pd.concat(parts, ignore_index=True).sort_values("date").set_index("date").rename(columns={FACTOR_COLUMN:"factor"}))
    if bars.empty:
        raise ValueError(f"No data found for {SYMBOL} in {YEAR}")

    bars["previous_close"] = bars["close"].shift(1)
    bars["previous_factor"] = bars["factor"].shift(1)
    bars["factor_ratio"] = bars["factor"] / bars["previous_factor"]

    bars["raw_close_return_pct"] = (bars["close"]/bars["previous_close"]-1)*100
    # This calculation tests a candidate convention.
    # It does not establish the source's factor definition.
    bars["candidate_adjusted_return_pct"] = (
        (bars["close"] * bars["factor"])
        / (bars["previous_close"] * bars["previous_factor"])
        - 1
    ) * 100

    changed = (
        bars["previous_close"].notna()
        & ~np.isclose(bars["factor"],bars["previous_factor"],rtol=1e-8, atol=1e-8)
    )

    print(f"Symbol: {SYMBOL}")
    print(f"Period: {YEAR}")
    print(f"Rows: {len(bars)}")
    print(f"First date: {bars.index.min().date()}")
    print(f"Last date: {bars.index.max().date()}")

    print(f"first factor: {bars['factor'].iloc[0]:.8f}")
    print(f"last factor: {bars['factor'].iloc[-1]:.8f}")
    print(f"factor changes within period: {int(changed.sum())}")

    print("\nFirst and last observations:")
    print(
        bars[["open", "close", "factor"]]
        .iloc[[0, -1]]
        .to_string(float_format=lambda value: f"{value:.8f}")
    )

    columns = [
        "previous_close",
        "close",
        "previous_factor",
        "factor",
        "factor_ratio",
        "raw_close_return_pct",
        "candidate_adjusted_return_pct",
    ]

    print("\nObservations on factor-change dates:")
    print(
        bars.loc[changed, columns].to_string(
            float_format=lambda value: f"{value:.8f}"
        )
    )

if __name__ == "__main__":
    main()




