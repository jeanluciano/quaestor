"""Usage examples for consensus statistical utilities.

These examples demonstrate how to use the consensus algorithms
extracted from V2.0 Quantum Intelligence.
"""

from consensus import (
    aggregate_rankings,
    bayesian_aggregation,
    calculate_consensus_score,
    median_aggregation,
    weighted_average,
    wisdom_of_crowds,
)


def example_weighted_average():
    """Example: Aggregating confidence scores from multiple sources."""
    # Confidence scores from different analysis components
    confidence_scores = [0.8, 0.9, 0.7, 0.85]

    # Weights based on component reliability
    reliability_weights = [1.0, 1.5, 0.8, 1.2]

    # Calculate weighted average with confidence interval
    avg_confidence, (lower, upper) = weighted_average(confidence_scores, reliability_weights)

    print(f"Average confidence: {avg_confidence:.3f}")
    print(f"95% confidence interval: [{lower:.3f}, {upper:.3f}]")

    return avg_confidence


def example_median_aggregation():
    """Example: Robust aggregation of performance metrics."""
    # Performance measurements (some with outliers)
    response_times_ms = [45, 52, 48, 51, 250, 47, 49]  # 250ms is outlier

    # Median is robust to outliers
    median_time, (lower, upper) = median_aggregation(response_times_ms)

    print(f"Median response time: {median_time:.1f}ms")
    print(f"MAD-based interval: [{lower:.1f}, {upper:.1f}]ms")

    # Compare with mean (affected by outlier)
    mean_time = sum(response_times_ms) / len(response_times_ms)
    print(f"Mean response time: {mean_time:.1f}ms (affected by outlier)")

    return median_time


def example_wisdom_of_crowds():
    """Example: Crowd-sourced estimation with diversity bonus."""
    # Estimates from multiple AI agents
    size_estimates = [150, 180, 165, 220, 170, 160]

    # Base weights from agent expertise
    agent_weights = [1.0, 0.8, 1.2, 0.7, 1.1, 0.9]

    # Apply wisdom of crowds with diversity bonus
    crowd_result = wisdom_of_crowds(size_estimates, weights=agent_weights, diversity_bonus=True)

    print(f"Crowd estimate: {crowd_result['value']:.1f}")
    print(f"Diversity score: {crowd_result['diversity_score']:.3f}")
    print(f"Confidence interval: {crowd_result['confidence_interval']}")

    return crowd_result


def example_bayesian_aggregation():
    """Example: Bayesian combination of predictions."""
    # Predictions from different models
    predictions = [0.75, 0.82, 0.78]

    # Model precisions (inverse of prediction variance)
    # Higher precision = more confident/reliable model
    model_precisions = [10.0, 15.0, 12.0]

    # Bayesian aggregation
    bayes_result = bayesian_aggregation(predictions, model_precisions)

    print(f"Bayesian prediction: {bayes_result['value']:.3f}")
    print(f"Posterior precision: {bayes_result['posterior_precision']:.1f}")
    print(f"Confidence interval: {bayes_result['confidence_interval']}")

    return bayes_result


def example_consensus_scoring():
    """Example: Measuring agreement in team decisions."""
    # Team member ratings (1-10 scale)
    scenario1 = [8, 8, 9, 8, 7]  # High consensus
    scenario2 = [5, 9, 3, 8, 7]  # Low consensus

    consensus1 = calculate_consensus_score(scenario1)
    consensus2 = calculate_consensus_score(scenario2)

    print(f"Scenario 1 consensus: {consensus1:.3f} (high agreement)")
    print(f"Scenario 2 consensus: {consensus2:.3f} (low agreement)")

    return consensus1, consensus2


def example_ranking_aggregation():
    """Example: Combining rankings from multiple evaluators."""
    # Rankings from 3 different evaluation methods
    rankings = [
        ["Feature A", "Feature B", "Feature C", "Feature D"],
        ["Feature B", "Feature A", "Feature D", "Feature C"],
        ["Feature A", "Feature C", "Feature B", "Feature D"],
    ]

    # Evaluator weights (e.g., based on past accuracy)
    evaluator_weights = [1.0, 0.8, 1.2]

    # Aggregate rankings
    consensus_ranking = aggregate_rankings(rankings, evaluator_weights)

    print("Consensus ranking:")
    for i, feature in enumerate(consensus_ranking, 1):
        print(f"{i}. {feature}")

    return consensus_ranking


def example_real_world_decision():
    """Example: Complex decision making with multiple algorithms."""
    print("\n=== Multi-Algorithm Decision Support ===\n")

    # Scenario: Estimating project completion time
    # Multiple team members provide estimates
    estimates_days = [14, 18, 16, 25, 15, 17]
    member_experience = [2.0, 5.0, 3.0, 1.0, 4.0, 3.5]  # Years

    # 1. Simple average
    simple_avg = sum(estimates_days) / len(estimates_days)
    print(f"Simple average: {simple_avg:.1f} days")

    # 2. Experience-weighted average
    weighted_est, conf_interval = weighted_average(estimates_days, member_experience)
    print(f"Experience-weighted: {weighted_est:.1f} days {conf_interval}")

    # 3. Median (robust to outliers)
    median_est, _ = median_aggregation(estimates_days)
    print(f"Median estimate: {median_est:.1f} days")

    # 4. Wisdom of crowds
    crowd_est = wisdom_of_crowds(estimates_days, member_experience, diversity_bonus=True)
    print(f"Crowd wisdom: {crowd_est['value']:.1f} days")

    # 5. Consensus score
    consensus = calculate_consensus_score(estimates_days)
    print(f"\nTeam consensus level: {consensus:.2%}")

    if consensus < 0.7:
        print("⚠️  Low consensus - consider further discussion")
    else:
        print("✓ Good consensus among team members")


if __name__ == "__main__":
    print("=== Consensus Utilities Examples ===\n")

    print("1. Weighted Average:")
    example_weighted_average()

    print("\n2. Median Aggregation:")
    example_median_aggregation()

    print("\n3. Wisdom of Crowds:")
    example_wisdom_of_crowds()

    print("\n4. Bayesian Aggregation:")
    example_bayesian_aggregation()

    print("\n5. Consensus Scoring:")
    example_consensus_scoring()

    print("\n6. Ranking Aggregation:")
    example_ranking_aggregation()

    print("\n7. Real-World Decision Example:")
    example_real_world_decision()
