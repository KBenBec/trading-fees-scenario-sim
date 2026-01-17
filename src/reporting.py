# src/reporting.py
from __future__ import annotations
import pandas as pd

def rank_scenarios(df: pd.DataFrame, k: int = 15) -> pd.DataFrame:
    # Rank by revenue uplift, then limit volume loss, then liquidity proxy
    out = df.sort_values(
        by=["revenue_uplift_pct", "volume_shift_pct", "liquidity_proxy"],
        ascending=[False, False, False],
    ).head(k)
    return out.reset_index(drop=True)

def to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
