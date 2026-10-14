# Backtrader Quant Framework

A reusable quantitative backtesting framework for A-share research,
with US-market support planned for later.

## Current capabilities

- Convert daily Excel data into monthly Parquet files.
- Validate source data and verify identical duplicate files during conversion.
- Load daily bars for one A-share stock.
- Convert trading volume from lots to shares.
- Run Backtrader buy and sell exercises.
- Apply a simple percentage commission.
- Inspect adjustment-factor changes.

## Project structure

- `quantbt/data/`: reusable data loaders.
- `quantbt/strategies/`: Backtrader strategies.
- `scripts/`: runnable exercises and data preparation tools.
- `data/`: local datasets excluded from Git.

## Running an exercise

Open the project in PyCharm with the configured Python virtual environment.

Run `scripts/run_first_trade.py` to exercise one buy-and-sell trade
with percentage commission. The script requires local processed data
for stock 000001 in January 2025.

## Current limitations

The data loader returns raw, unadjusted OHLC prices.
Adjustment-factor behavior has been investigated for stock 000001,
but adjusted signal prices have not yet been added to the loader.

Realistic A-share costs, trading constraints, corporate-action accounting,
multiple-stock strategies, and performance analyzers remain planned work.

## Development workflow

After completing and verifying a meaningful feature:

1. Review the changed files.
2. Commit the related changes with a clear message.
3. Push the commit to GitHub.