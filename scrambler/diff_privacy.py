"""
Differential privacy module.
Uses Laplace mechanism for adding calibrated noise to numeric device data.
Legitimate real technique (Cynthia Dwork et al.).
Epsilon controls privacy-utility tradeoff.
"""

from __future__ import annotations

import numpy as np
from typing import List, Union


def add_laplace_noise(
    value: float, epsilon: float = 1.0, sensitivity: float = 1.0, seed: int | None = None
) -> float:
    """
    Add Laplace noise for (epsilon, delta=0)-DP.
    sensitivity: max change one record can cause.
    """
    if seed is not None:
        np.random.seed(seed)
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return float(value + noise)


def privatize_list(
    values: List[float], epsilon: float = 1.0, sensitivity: float = 1.0, seed: int | None = None
) -> List[float]:
    """Apply noise to each value in list."""
    if seed is not None:
        np.random.seed(seed)
    return [add_laplace_noise(v, epsilon, sensitivity) for v in values]


def privatize_device_field(
    field_name: str, value: Union[int, float], epsilon: float = 0.5
) -> float:
    """
    Domain aware: e.g. for battery % sensitivity 100, for lat sensitivity 0.01 etc.
    Simplified here.
    """
    sens = 1.0
    if "battery" in field_name.lower() or "percent" in field_name.lower():
        sens = 100.0
    elif "lat" in field_name.lower() or "lon" in field_name.lower():
        sens = 0.01
    elif "screen" in field_name.lower() or "width" in field_name.lower():
        sens = 100.0
    return add_laplace_noise(float(value), epsilon, sens)
