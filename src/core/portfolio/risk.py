"""Risk sizing utilities."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskParameters:
    risk_per_trade: float = 0.01  # fraction of equity
    stop_distance: float = 0.02   # relative stop distance


def position_size(equity: float, params: RiskParameters) -> float:
    """Compute position size based on risk parameters."""

    risk_amount = equity * params.risk_per_trade
    if params.stop_distance <= 0:
        raise ValueError("stop_distance must be positive")
    return risk_amount / params.stop_distance


__all__ = ["RiskParameters", "position_size"]
