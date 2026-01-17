# examples/run_calibration.py
from src.config import Config
from src.data_loader import load_trades
from src.elasticity import calibrate_elasticities_with_bootstrap

def main():
    cfg = Config()
    trades = load_trades("data/sample_trades.csv")

    res = calibrate_elasticities_with_bootstrap(
        trades=trades,
        clusters=cfg.clusters,
        bounds=cfg.elasticity_bounds,
        n_boot=cfg.bootstrap_n,
        seed=cfg.bootstrap_seed,
    )

    print("\nElasticities (beta) with 95% CI:")
    for c in cfg.clusters:
        b = res.beta_by_cluster[c]
        lo, hi = res.ci95_by_cluster[c]
        print(f"  {c:14s}: beta={b:+.3f}  CI95=[{lo:+.3f},{hi:+.3f}]  (se={res.se_by_cluster[c]:.3f})")

if __name__ == "__main__":
    main()
