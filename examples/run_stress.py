# examples/run_stress.py
import pandas as pd

from src.config import Config
from src.data_loader import load_trades
from src.elasticity import calibrate_elasticities_with_bootstrap
from src.scenario_engine import generate_scenarios, apply_fee_response
from src.metrics import compute_metrics
from src.stress import run_stress_shocks

def main():
    cfg = Config()
    trades = load_trades("data/sample_trades.csv")

    base = trades.groupby("cluster").agg(volume=("volume", "mean"), fee_bps=("fee_bps", "mean")).reset_index()
    base_volume = {r["cluster"]: float(r["volume"]) for _, r in base.iterrows()}
    base_fee = {r["cluster"]: float(r["fee_bps"]) for _, r in base.iterrows()}

    calib = calibrate_elasticities_with_bootstrap(
        trades=trades,
        clusters=cfg.clusters,
        bounds=cfg.elasticity_bounds,
        n_boot=cfg.bootstrap_n,
        seed=cfg.bootstrap_seed,
    )

    # Pick one scenario as example: “revenue up with limited volume loss” style
    s = generate_scenarios(cfg.clusters, cfg.fee_bps_grid, n_scenarios=1, seed=99)[0]

    base_case_vol = apply_fee_response(base_volume, base_fee, s.fee_bps_by_cluster, calib.beta_by_cluster, 0.0)
    down_vol, up_vol = run_stress_shocks(
        base_volume, base_fee, s.fee_bps_by_cluster, calib.beta_by_cluster,
        downside_shock=cfg.downside_volume_shock,
        upside_shock=cfg.upside_volume_shock,
    )

    m0 = compute_metrics(base_volume, base_fee, base_case_vol, s.fee_bps_by_cluster, cfg.liquidity_alpha)
    md = compute_metrics(base_volume, base_fee, down_vol, s.fee_bps_by_cluster, cfg.liquidity_alpha)
    mu = compute_metrics(base_volume, base_fee, up_vol, s.fee_bps_by_cluster, cfg.liquidity_alpha)

    print("\nScenario fees:", s.fee_bps_by_cluster)
    print(f"Base-case: revenue_uplift={m0.revenue_uplift_pct:+.2f}%  volume_shift={m0.volume_shift_pct:+.2f}%  risk={m0.risk_flag}")
    print(f"Downside : revenue_uplift={md.revenue_uplift_pct:+.2f}%  volume_shift={md.volume_shift_pct:+.2f}%  risk={md.risk_flag}")
    print(f"Upside   : revenue_uplift={mu.revenue_uplift_pct:+.2f}%  volume_shift={mu.volume_shift_pct:+.2f}%  risk={mu.risk_flag}")

if __name__ == "__main__":
    main()
