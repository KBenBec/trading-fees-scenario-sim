# examples/run_simulation.py
import pandas as pd

from src.config import Config
from src.data_loader import load_trades
from src.elasticity import calibrate_elasticities_with_bootstrap
from src.scenario_engine import generate_scenarios, apply_fee_response, scenario_to_row
from src.metrics import compute_metrics
from src.reporting import rank_scenarios, to_csv

def main():
    cfg = Config()
    trades = load_trades("data/sample_trades.csv")

    # Baselines from history
    base = trades.groupby("cluster").agg(volume=("volume", "mean"), fee_bps=("fee_bps", "mean")).reset_index()
    base_volume = {r["cluster"]: float(r["volume"]) for _, r in base.iterrows()}
    base_fee = {r["cluster"]: float(r["fee_bps"]) for _, r in base.iterrows()}

    # Calibrate elasticities
    calib = calibrate_elasticities_with_bootstrap(
        trades=trades,
        clusters=cfg.clusters,
        bounds=cfg.elasticity_bounds,
        n_boot=cfg.bootstrap_n,
        seed=cfg.bootstrap_seed,
    )

    # Scenarios
    scenarios = generate_scenarios(
        clusters=cfg.clusters,
        fee_grid=cfg.fee_bps_grid,
        n_scenarios=cfg.scenarios_per_run,
        seed=11,
    )

    rows = []
    for s in scenarios:
        new_vol = apply_fee_response(
            base_volume_by_cluster=base_volume,
            base_fee_bps_by_cluster=base_fee,
            scenario_fee_bps_by_cluster=s.fee_bps_by_cluster,
            elasticity_by_cluster=calib.beta_by_cluster,
            exogenous_volume_shock=0.0,
        )
        m = compute_metrics(
            base_volume_by_cluster=base_volume,
            base_fee_bps_by_cluster=base_fee,
            new_volume_by_cluster=new_vol,
            new_fee_bps_by_cluster=s.fee_bps_by_cluster,
            liquidity_alpha=cfg.liquidity_alpha,
        )
        row = {}
        row.update(scenario_to_row(s))
        row.update({
            "revenue": m.revenue,
            "volume_total": m.volume_total,
            "volume_shift_pct": m.volume_shift_pct,
            "revenue_uplift_pct": m.revenue_uplift_pct,
            "market_share_uplift_pct": m.market_share_uplift_pct,
            "liquidity_proxy": m.liquidity_proxy,
            "risk_flag": m.risk_flag,
        })
        rows.append(row)

    df = pd.DataFrame(rows)
    top = rank_scenarios(df, k=15)

    print("\nTop candidate fee schedules:")
    print(top[[
        "revenue_uplift_pct", "volume_shift_pct", "market_share_uplift_pct", "risk_flag",
        "fee_bps__retail_broker", "fee_bps__bank", "fee_bps__market_maker", "fee_bps__prop_firm"
    ]].to_string(index=False))

    to_csv(df, "data/scenario_results.csv")
    to_csv(top, "data/top15_scenarios.csv")
    print("\nSaved: data/scenario_results.csv and data/top15_scenarios.csv")

if __name__ == "__main__":
    main()
