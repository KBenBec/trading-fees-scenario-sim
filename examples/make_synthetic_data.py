# examples/make_synthetic_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def main(out_trades="data/sample_trades.csv", out_fees="data/sample_fees.csv", seed=123):
    rng = np.random.default_rng(seed)

    clusters = ["retail_broker", "bank", "market_maker", "prop_firm"]
    # baseline fee around 5-7 bps depending on cluster
    base_fee = {
        "retail_broker": 7,
        "bank": 6,
        "market_maker": 4,
        "prop_firm": 6,
    }
    # true elasticities (hidden)
    beta_true = {
        "retail_broker": -0.10,
        "bank": -0.06,
        "market_maker": -0.03,
        "prop_firm": -0.08,
    }

    start = datetime(2025, 1, 1)
    n_days = 120
    rows = []

    for d in range(n_days):
        date = (start + timedelta(days=d)).date()
        for c in clusters:
            fee = base_fee[c] + int(rng.integers(-2, 3))
            v0 = {
                "retail_broker": 1200,
                "bank": 1800,
                "market_maker": 2600,
                "prop_firm": 900,
            }[c]
            # multiplicative noise and fee response
            noise = float(np.exp(rng.normal(0, 0.12)))
            volume = v0 * np.exp(beta_true[c] * (fee - base_fee[c])) * noise
            notional = volume * float(rng.uniform(0.9, 1.3))

            rows.append({
                "date": str(date),
                "cluster": c,
                "notional": round(notional, 4),
                "volume": round(volume, 4),
                "fee_bps": int(fee),
            })

    trades = pd.DataFrame(rows)
    trades.to_csv(out_trades, index=False)

    fee_menu = pd.DataFrame([{"cluster": c, "fee_bps": f} for c in clusters for f in range(2, 11)])
    fee_menu.to_csv(out_fees, index=False)

    print(f"Saved: {out_trades} ({len(trades)} rows), {out_fees} ({len(fee_menu)} rows)")

if __name__ == "__main__":
    main()
