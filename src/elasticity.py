# src/elasticity.py
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class ElasticityResult:
    beta_by_cluster: Dict[str, float]            # elasticity
    ci95_by_cluster: Dict[str, Tuple[float, float]]
    se_by_cluster: Dict[str, float]

def _fit_cluster_elasticity(df_c: pd.DataFrame, bounds: Tuple[float, float]) -> float:
    """
    Fit beta in: ln(volume) = a + beta * fee_bps + eps
    beta is elasticity in bps space.
    """
    x = df_c["fee_bps"].to_numpy(dtype=float)
    y = np.log(df_c["volume"].to_numpy(dtype=float))

    # OLS closed-form with intercept
    X = np.column_stack([np.ones_like(x), x])
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0][1]
    beta_hat = float(np.clip(beta_hat, bounds[0], bounds[1]))
    return beta_hat

def calibrate_elasticities_with_bootstrap(
    trades: pd.DataFrame,
    clusters: Tuple[str, ...],
    bounds: Tuple[float, float],
    n_boot: int = 400,
    seed: int = 42,
) -> ElasticityResult:
    rng = np.random.default_rng(seed)
    beta = {}
    se = {}
    ci95 = {}

    for c in clusters:
        df_c = trades[trades["cluster"] == c].copy()
        if len(df_c) < 30:
            # Fallback to mild negative elasticity if too few samples
            beta[c] = float(np.clip(-0.05, bounds[0], bounds[1]))
            se[c] = float("nan")
            ci95[c] = (float("nan"), float("nan"))
            continue

        beta_hat = _fit_cluster_elasticity(df_c, bounds)
        beta[c] = beta_hat

        # Bootstrap
        boot = []
        idx = np.arange(len(df_c))
        for _ in range(n_boot):
            sample_idx = rng.choice(idx, size=len(idx), replace=True)
            df_b = df_c.iloc[sample_idx]
            boot.append(_fit_cluster_elasticity(df_b, bounds))
        boot = np.array(boot, dtype=float)

        se[c] = float(np.std(boot, ddof=1))
        lo, hi = np.quantile(boot, [0.025, 0.975])
        ci95[c] = (float(lo), float(hi))

    return ElasticityResult(beta_by_cluster=beta, ci95_by_cluster=ci95, se_by_cluster=se)
