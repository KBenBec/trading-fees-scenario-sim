# src/stress.py
from __future__ import annotations
from typing import Dict, Tuple
from .scenario_engine import apply_fee_response

def run_stress_shocks(
    base_volume_by_cluster: Dict[str, float],
    base_fee_bps_by_cluster: Dict[str, float],
    scenario_fee_bps_by_cluster: Dict[str, int],
    elasticity_by_cluster: Dict[str, float],
    downside_shock: float,
    upside_shock: float,
) -> Tuple[Dict[str, float], Dict[str, float]]:
    down = apply_fee_response(
        base_volume_by_cluster, base_fee_bps_by_cluster, scenario_fee_bps_by_cluster,
        elasticity_by_cluster, exogenous_volume_shock=downside_shock
    )
    up = apply_fee_response(
        base_volume_by_cluster, base_fee_bps_by_cluster, scenario_fee_bps_by_cluster,
        elasticity_by_cluster, exogenous_volume_shock=upside_shock
    )
    return down, up
