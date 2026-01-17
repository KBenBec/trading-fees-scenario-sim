# src/scenario_engine.py
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class Scenario:
    fee_bps_by_cluster: Dict[str, int]

def generate_scenarios(
    clusters: Tuple[str, ...],
    fee_grid: Tuple[int, ...],
    n_scenarios: int,
    seed: int = 7,
) -> List[Scenario]:
    rng = np.random.default_rng(seed)
    scenarios = []
    fee_grid = np.array(list(fee_grid), dtype=int)

    for _ in range(n_scenarios):
        fees = rng.choice(fee_grid, size=len(clusters), replace=True)
        scenarios.append(Scenario({c: int(f) for c, f in zip(clusters, fees)}))
    return scenarios

def apply_fee_response(
    base_volume_by_cluster: Dict[str, float],
    base_fee_bps_by_cluster: Dict[str, float],
    scenario_fee_bps_by_cluster: Dict[str, int],
    elasticity_by_cluster: Dict[str, float],
    exogenous_volume_shock: float = 0.0,
) -> Dict[str, float]:
    """
    Volume model (log-linear):
      V_new = V0 * exp( beta * (fee_new - fee0) ) * (1 + shock)
    """
    out = {}
    for c, v0 in base_volume_by_cluster.items():
        fee0 = float(base_fee_bps_by_cluster[c])
        fee1 = float(scenario_fee_bps_by_cluster[c])
        beta = float(elasticity_by_cluster[c])
        v1 = v0 * float(np.exp(beta * (fee1 - fee0))) * (1.0 + exogenous_volume_shock)
        out[c] = max(0.0, float(v1))
    return out

def scenario_to_row(s: Scenario) -> Dict[str, float]:
    return {f"fee_bps__{k}": v for k, v in s.fee_bps_by_cluster.items()}
