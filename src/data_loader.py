# src/data_loader.py
from __future__ import annotations
import pandas as pd

REQUIRED_TRADES_COLS = {
    "date", "cluster", "notional", "volume", "fee_bps"
}

REQUIRED_FEES_COLS = {
    "cluster", "fee_bps"
}

def load_trades(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_TRADES_COLS - set(df.columns)
    if missing:
        raise ValueError(f"sample_trades.csv missing columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    df["cluster"] = df["cluster"].astype(str)
    for c in ["notional", "volume", "fee_bps"]:
        df[c] = pd.to_numeric(df[c], errors="raise")

    # Basic sanity
    df = df[(df["volume"] > 0) & (df["notional"] > 0) & (df["fee_bps"] >= 0)].copy()
    return df

def load_fee_menu(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_FEES_COLS - set(df.columns)
    if missing:
        raise ValueError(f"sample_fees.csv missing columns: {sorted(missing)}")

    df["cluster"] = df["cluster"].astype(str)
    df["fee_bps"] = pd.to_numeric(df["fee_bps"], errors="raise").astype(int)
    return df
