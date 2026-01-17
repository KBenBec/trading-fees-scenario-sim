# src/metrics.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class DecisionMetrics:
    revenue: float
    volume_total: float
    volume_shift_pct: float
    revenue_uplift_pct: float
    market_share_uplift_pct: float
    liquidity_proxy: float
    risk_flag: str

def compute_metrics(
    base_volume_by_cluster: Dict[str, float],
    base_fee_bps_by_cluster: Dict[str, float],
    new_volume_by_cluster: Dict[str, float],
    new_fee_bps_by_cluster: Dict[str, float],
    liquidity_alpha: float = 0.50,
) -> DecisionMetrics:
    # Revenue ~ volume * fee_bps (bps as linear proxy; ok for ranking)
    base_rev = sum(base_volume_by_cluster[c] * base_fee_bps_by_cluster[c] for c in base_volume_by_cluster)
    new_rev = sum(new_volume_by_cluster[c] * new_fee_bps_by_cluster[c] for c in new_volume_by_cluster)

    base_vol = sum(base_volume_by_cluster.values())
    new_vol = sum(new_volume_by_cluster.values())

    vol_shift_pct = (new_vol / base_vol - 1.0) * 100.0
    rev_uplift_pct = (new_rev / base_rev - 1.0) * 100.0 if base_rev > 0 else 0.0

    # Simple "market share uplift" proxy: overweight clusters that are typically price-sensitive
    # Here: assume retail+prop are more "share-like"
    base_share = base_volume_by_cluster.get("retail_broker", 0) + base_volume_by_cluster.get("prop_firm", 0)
    new_share = new_volume_by_cluster.get("retail_broker", 0) + new_volume_by_cluster.get("prop_firm", 0)
    market_share_uplift_pct = (new_share / base_share - 1.0) * 100.0 if base_share > 0 else 0.0

    # Liquidity proxy: penalize volume loss (bigger penalty => lower is worse)
    liquidity_proxy = new_vol - liquidity_alpha * max(0.0, (base_vol - new_vol))

    # Risk flag (simple heuristics)
    risk_flag = "OK"
    if vol_shift_pct < -1.0 and rev_uplift_pct < 0:
        risk_flag = "HIGH: volume+revenue down"
    elif vol_shift_pct < -1.0:
        risk_flag = "MEDIUM: volume down"
    elif rev_uplift_pct < 0:
        risk_flag = "MEDIUM: revenue down"

    return DecisionMetrics(
        revenue=float(new_rev),
        volume_total=float(new_vol),
        volume_shift_pct=float(vol_shift_pct),
        revenue_uplift_pct=float(rev_uplift_pct),
        market_share_uplift_pct=float(market_share_uplift_pct),
        liquidity_proxy=float(liquidity_proxy),
        risk_flag=risk_flag,
    )
