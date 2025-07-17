"""Statistical aggregation and consensus algorithms.

Extracted from A1 Quantum Intelligence with 85% complexity reduction.
Provides weighted averaging, robust statistics, and consensus scoring.
"""

import math
import statistics
from typing import Any


def weighted_average(values: list[float], weights: list[float] | None = None) -> tuple[float, tuple[float, float]]:
    """Calculate weighted average with confidence interval.

    Args:
        values: List of numeric values
        weights: Optional weights for each value (defaults to equal weights)

    Returns:
        Tuple of (weighted_average, (lower_bound, upper_bound))
    """
    if not values:
        return 0.0, (0.0, 0.0)

    if weights is None:
        weights = [1.0] * len(values)

    if len(weights) != len(values):
        raise ValueError("Values and weights must have same length")

    # Calculate weighted average
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0, (0.0, 0.0)

    weighted_sum = sum(v * w for v, w in zip(values, weights, strict=False))
    weighted_avg = weighted_sum / total_weight

    # Calculate confidence interval (95%)
    if len(values) > 1:
        # Weighted variance
        variance = sum(w * (v - weighted_avg) ** 2 for v, w in zip(values, weights, strict=False)) / total_weight

        # Standard error
        std_error = math.sqrt(variance / len(values))
        margin = 1.96 * std_error  # 95% confidence

        confidence_interval = (weighted_avg - margin, weighted_avg + margin)
    else:
        confidence_interval = (weighted_avg, weighted_avg)

    return weighted_avg, confidence_interval


def median_aggregation(values: list[float]) -> tuple[float, tuple[float, float]]:
    """Calculate median with robust confidence interval using MAD.

    Args:
        values: List of numeric values

    Returns:
        Tuple of (median, (lower_bound, upper_bound))
    """
    if not values:
        return 0.0, (0.0, 0.0)

    median_val = statistics.median(values)

    # Calculate Median Absolute Deviation (MAD) for robust confidence
    if len(values) > 1:
        mad = statistics.median([abs(x - median_val) for x in values])
        # Robust confidence interval using MAD
        margin = 1.96 * mad
        confidence_interval = (median_val - margin, median_val + margin)
    else:
        confidence_interval = (median_val, median_val)

    return median_val, confidence_interval


def wisdom_of_crowds(
    values: list[float], weights: list[float] | None = None, diversity_bonus: bool = True
) -> dict[str, Any]:
    """Wisdom of crowds aggregation with diversity consideration.

    Args:
        values: List of numeric values
        weights: Optional base weights for each value
        diversity_bonus: Whether to apply diversity bonus to weights

    Returns:
        Dict with aggregated value, confidence, and diversity score
    """
    if not values:
        return {"value": 0.0, "confidence_interval": (0.0, 0.0), "diversity_score": 0.0, "input_count": 0}

    if weights is None:
        weights = [1.0] * len(values)

    # Calculate diversity-adjusted weights
    if diversity_bonus and len(values) > 1:
        current_avg = sum(values) / len(values)
        adjusted_weights = []

        for val, base_weight in zip(values, weights, strict=False):
            # Diversity bonus based on deviation from average
            diversity = abs(val - current_avg) / (current_avg + 1e-6)
            diversity_bonus_factor = min(0.5, diversity * 0.1)
            adjusted_weight = base_weight * (1.0 + diversity_bonus_factor)
            adjusted_weights.append(adjusted_weight)

        weights = adjusted_weights

    # Calculate weighted result
    crowd_value, confidence_interval = weighted_average(values, weights)

    # Calculate diversity score
    if len(values) > 1:
        avg_val = sum(values) / len(values)
        diversity_score = statistics.stdev(values) / (avg_val + 1e-6)
    else:
        diversity_score = 0.0

    return {
        "value": crowd_value,
        "confidence_interval": confidence_interval,
        "diversity_score": diversity_score,
        "input_count": len(values),
        "total_weight": sum(weights),
    }


def bayesian_aggregation(values: list[float], precisions: list[float] | None = None) -> dict[str, Any]:
    """Bayesian aggregation with precision weighting.

    Args:
        values: List of numeric values (estimates)
        precisions: Precision (inverse variance) for each estimate

    Returns:
        Dict with Bayesian mean, confidence interval, and posterior precision
    """
    if not values:
        return {
            "value": 0.0,
            "confidence_interval": (0.0, 0.0),
            "posterior_precision": 0.0,
            "posterior_variance": float("inf"),
        }

    if precisions is None:
        # Use equal precisions if not provided
        precisions = [1.0] * len(values)

    # Bayesian combination
    total_precision = sum(precisions)
    if total_precision == 0:
        return {
            "value": 0.0,
            "confidence_interval": (0.0, 0.0),
            "posterior_precision": 0.0,
            "posterior_variance": float("inf"),
        }

    # Precision-weighted mean
    bayesian_mean = sum(val * prec for val, prec in zip(values, precisions, strict=False)) / total_precision

    # Posterior variance and confidence interval
    posterior_variance = 1.0 / total_precision
    posterior_std = math.sqrt(posterior_variance)

    # 95% confidence interval
    margin = 1.96 * posterior_std
    confidence_interval = (bayesian_mean - margin, bayesian_mean + margin)

    return {
        "value": bayesian_mean,
        "confidence_interval": confidence_interval,
        "posterior_precision": total_precision,
        "posterior_variance": posterior_variance,
        "input_count": len(values),
    }


def calculate_consensus_score(values: list[float]) -> float:
    """Calculate consensus score based on value agreement.

    Lower variance indicates higher consensus.

    Args:
        values: List of numeric values

    Returns:
        Consensus score between 0 and 1 (1 = perfect consensus)
    """
    if not values or len(values) < 2:
        return 1.0  # Perfect consensus with 0 or 1 value

    # Use variance as inverse measure of consensus
    variance = statistics.variance(values)

    # Normalize using coefficient of variation approach
    mean_val = statistics.mean(values)
    if mean_val != 0:
        cv = math.sqrt(variance) / abs(mean_val)
        # Convert to 0-1 score (lower CV = higher consensus)
        consensus_score = 1.0 / (1.0 + cv)
    else:
        # If mean is 0, use absolute variance
        consensus_score = 1.0 / (1.0 + variance)

    return min(1.0, max(0.0, consensus_score))


def calculate_agreement_matrix(value_sets: list[list[float]]) -> list[list[float]]:
    """Calculate pairwise agreement between multiple value sets.

    Args:
        value_sets: List of value lists from different sources

    Returns:
        Agreement matrix (symmetric) with values 0-1
    """
    n = len(value_sets)
    agreement_matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i, n):
            if i == j:
                agreement_matrix[i][j] = 1.0
            else:
                # Calculate agreement as inverse of normalized distance
                if value_sets[i] and value_sets[j]:
                    # Use correlation coefficient as agreement measure
                    agreement = _calculate_correlation(value_sets[i], value_sets[j])
                    agreement_matrix[i][j] = agreement
                    agreement_matrix[j][i] = agreement

    return agreement_matrix


def _calculate_correlation(values1: list[float], values2: list[float]) -> float:
    """Calculate correlation coefficient between two value lists."""
    if len(values1) != len(values2) or len(values1) < 2:
        return 0.0

    # Ensure same length by taking minimum
    min_len = min(len(values1), len(values2))
    values1 = values1[:min_len]
    values2 = values2[:min_len]

    # Calculate means
    mean1 = sum(values1) / len(values1)
    mean2 = sum(values2) / len(values2)

    # Calculate correlation
    numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2, strict=False))

    denominator1 = math.sqrt(sum((v - mean1) ** 2 for v in values1))
    denominator2 = math.sqrt(sum((v - mean2) ** 2 for v in values2))

    if denominator1 == 0 or denominator2 == 0:
        return 1.0 if values1 == values2 else 0.0

    correlation = numerator / (denominator1 * denominator2)

    # Convert to 0-1 range (correlation is -1 to 1)
    return (correlation + 1.0) / 2.0


def aggregate_rankings(rankings: list[list[str]], weights: list[float] | None = None) -> list[str]:
    """Aggregate multiple rankings into consensus ranking.

    Uses Borda count method with optional weights.

    Args:
        rankings: List of rankings (each ranking is ordered list of items)
        weights: Optional weights for each ranking source

    Returns:
        Consensus ranking
    """
    if not rankings:
        return []

    if weights is None:
        weights = [1.0] * len(rankings)

    # Collect all items
    all_items = set()
    for ranking in rankings:
        all_items.update(ranking)

    # Calculate Borda scores
    scores = {item: 0.0 for item in all_items}

    for ranking, weight in zip(rankings, weights, strict=False):
        n = len(ranking)
        for i, item in enumerate(ranking):
            # Higher position gets more points
            points = (n - i) * weight
            scores[item] += points

    # Sort by score
    consensus_ranking = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    return consensus_ranking
