# src/config.py
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class Config:
    # Clusters (membership types)
    clusters: Tuple[str, ...] = ("retail_broker", "bank", "market_maker", "prop_firm")

    # Baseline elasticity priors (rough defaults, will be calibrated)
    # Elasticity is defined as: d ln(V) / d FeeBps  (negative)
    elasticity_prior: Dict[str, float] = None

    # Bounds for plausible elasticities (to avoid nonsense fits)
    elasticity_bounds: Tuple[float, float] = (-0.80, -0.01)

    # Bootstrap
    bootstrap_n: int = 400
    bootstrap_seed: int = 42

    # Scenarios
    scenarios_per_run: int = 500
    fee_bps_grid: Tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10)  # example fee menu

    # Stress shocks
    downside_volume_shock: float = -0.06   # -6% exogenous shock
    upside_volume_shock: float = +0.03     # +3% exogenous shock

    # Liquidity proxy weight (simple)
    liquidity_alpha: float = 0.50  # higher => penalize volume loss more

    def __post_init__(self):
        if self.elasticity_prior is None:
            object.__setattr__(self, "elasticity_prior", {
                "retail_broker": -0.10,
                "bank": -0.06,
                "market_maker": -0.03,
                "prop_firm": -0.08,
            })
