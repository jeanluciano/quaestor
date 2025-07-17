"""Tests for consensus statistical utilities."""

import math

import pytest

from a1.utilities.consensus import (
    aggregate_rankings,
    bayesian_aggregation,
    calculate_agreement_matrix,
    calculate_consensus_score,
    median_aggregation,
    weighted_average,
    wisdom_of_crowds,
)


class TestWeightedAverage:
    """Test weighted average calculations."""

    def test_basic_weighted_average(self):
        """Test basic weighted average calculation."""
        values = [10.0, 20.0, 30.0]
        weights = [1.0, 2.0, 3.0]

        avg, (lower, upper) = weighted_average(values, weights)

        # Expected: (10*1 + 20*2 + 30*3) / 6 = 23.33
        assert abs(avg - 23.33) < 0.01
        assert lower < avg < upper

    def test_equal_weights(self):
        """Test with equal weights (simple average)."""
        values = [10.0, 20.0, 30.0]

        avg, _ = weighted_average(values)

        assert avg == 20.0

    def test_single_value(self):
        """Test with single value."""
        values = [42.0]

        avg, (lower, upper) = weighted_average(values)

        assert avg == 42.0
        assert lower == 42.0
        assert upper == 42.0

    def test_empty_values(self):
        """Test with empty values."""
        avg, (lower, upper) = weighted_average([])

        assert avg == 0.0
        assert lower == 0.0
        assert upper == 0.0

    def test_zero_weights(self):
        """Test with zero total weight."""
        values = [10.0, 20.0]
        weights = [0.0, 0.0]

        avg, _ = weighted_average(values, weights)

        assert avg == 0.0

    def test_mismatched_lengths(self):
        """Test error on mismatched lengths."""
        with pytest.raises(ValueError):
            weighted_average([1.0, 2.0], [1.0])


class TestMedianAggregation:
    """Test median aggregation with MAD confidence."""

    def test_basic_median(self):
        """Test basic median calculation."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]

        median, _ = median_aggregation(values)

        assert median == 30.0

    def test_median_with_outliers(self):
        """Test median is robust to outliers."""
        values = [10.0, 20.0, 30.0, 40.0, 1000.0]

        median, _ = median_aggregation(values)

        assert median == 30.0

    def test_confidence_interval(self):
        """Test MAD-based confidence interval."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]

        median, (lower, upper) = median_aggregation(values)

        # MAD = median(|10-30|, |20-30|, |30-30|, |40-30|, |50-30|)
        # MAD = median(20, 10, 0, 10, 20) = 10
        expected_margin = 1.96 * 10

        assert abs(lower - (median - expected_margin)) < 0.01
        assert abs(upper - (median + expected_margin)) < 0.01

    def test_single_value(self):
        """Test with single value."""
        median, (lower, upper) = median_aggregation([42.0])

        assert median == 42.0
        assert lower == 42.0
        assert upper == 42.0


class TestWisdomOfCrowds:
    """Test wisdom of crowds aggregation."""

    def test_basic_aggregation(self):
        """Test basic wisdom of crowds."""
        values = [10.0, 20.0, 30.0]

        result = wisdom_of_crowds(values)

        assert result["input_count"] == 3
        assert result["value"] == 20.0  # Equal weights
        assert result["diversity_score"] > 0

    def test_diversity_bonus(self):
        """Test diversity bonus application."""
        values = [10.0, 20.0, 30.0, 100.0]  # 100 is diverse

        # With diversity bonus
        result_with = wisdom_of_crowds(values, diversity_bonus=True)

        # Without diversity bonus
        result_without = wisdom_of_crowds(values, diversity_bonus=False)

        # The diverse value (100) should have more influence with bonus
        assert result_with["value"] > result_without["value"]

    def test_custom_weights(self):
        """Test with custom base weights."""
        values = [10.0, 20.0, 30.0]
        weights = [1.0, 2.0, 3.0]

        result = wisdom_of_crowds(values, weights=weights)

        # Should be weighted towards higher values
        assert result["value"] > 20.0

    def test_diversity_score(self):
        """Test diversity score calculation."""
        # Low diversity
        low_div = wisdom_of_crowds([20.0, 21.0, 22.0])

        # High diversity
        high_div = wisdom_of_crowds([10.0, 50.0, 90.0])

        assert high_div["diversity_score"] > low_div["diversity_score"]


class TestBayesianAggregation:
    """Test Bayesian aggregation."""

    def test_basic_bayesian(self):
        """Test basic Bayesian aggregation."""
        values = [10.0, 20.0, 30.0]
        precisions = [1.0, 2.0, 3.0]  # Higher precision = more weight

        result = bayesian_aggregation(values, precisions)

        # Expected: (10*1 + 20*2 + 30*3) / 6 = 23.33
        assert abs(result["value"] - 23.33) < 0.01
        assert result["posterior_precision"] == 6.0
        assert result["posterior_variance"] == 1.0 / 6.0

    def test_equal_precisions(self):
        """Test with equal precisions."""
        values = [10.0, 20.0, 30.0]

        result = bayesian_aggregation(values)

        assert result["value"] == 20.0
        assert result["posterior_precision"] == 3.0

    def test_confidence_interval(self):
        """Test confidence interval calculation."""
        values = [10.0, 20.0, 30.0]
        precisions = [1.0, 1.0, 1.0]

        result = bayesian_aggregation(values, precisions)
        lower, upper = result["confidence_interval"]

        # Check interval contains the mean
        assert lower < result["value"] < upper

        # Check interval width is reasonable
        posterior_std = math.sqrt(result["posterior_variance"])
        expected_margin = 1.96 * posterior_std
        assert abs((upper - lower) / 2 - expected_margin) < 0.01


class TestConsensusScore:
    """Test consensus score calculation."""

    def test_perfect_consensus(self):
        """Test perfect consensus (all same value)."""
        score = calculate_consensus_score([20.0, 20.0, 20.0])
        assert score == 1.0

    def test_no_consensus(self):
        """Test low consensus (high variance)."""
        score = calculate_consensus_score([0.0, 100.0, -100.0])
        assert score < 0.5

    def test_moderate_consensus(self):
        """Test moderate consensus."""
        score = calculate_consensus_score([18.0, 20.0, 22.0])
        assert 0.7 < score <= 0.95  # Allow for higher consensus with small variance

    def test_single_value(self):
        """Test with single value."""
        score = calculate_consensus_score([42.0])
        assert score == 1.0

    def test_zero_mean(self):
        """Test with zero mean."""
        score = calculate_consensus_score([-10.0, 0.0, 10.0])
        assert 0 <= score <= 1


class TestAgreementMatrix:
    """Test agreement matrix calculation."""

    def test_basic_agreement(self):
        """Test basic agreement matrix."""
        value_sets = [
            [10.0, 20.0, 30.0],
            [11.0, 19.0, 31.0],  # Similar to first
            [50.0, 60.0, 70.0],  # Different
        ]

        matrix = calculate_agreement_matrix(value_sets)

        # Diagonal should be 1.0
        assert matrix[0][0] == 1.0
        assert matrix[1][1] == 1.0
        assert matrix[2][2] == 1.0

        # Should be symmetric
        assert matrix[0][1] == matrix[1][0]
        assert matrix[0][2] == matrix[2][0]

        # First two should have high agreement
        assert matrix[0][1] > 0.8

        # Agreement values should be between 0 and 1
        assert 0 <= matrix[0][2] <= 1
        assert 0 <= matrix[1][2] <= 1

    def test_empty_sets(self):
        """Test with empty value sets."""
        value_sets = [[], [1.0, 2.0], []]

        matrix = calculate_agreement_matrix(value_sets)

        # Empty sets have 0 agreement with non-empty
        assert matrix[0][1] == 0.0
        assert matrix[1][0] == 0.0


class TestAggregateRankings:
    """Test ranking aggregation."""

    def test_basic_ranking(self):
        """Test basic ranking aggregation."""
        rankings = [
            ["A", "B", "C"],
            ["A", "C", "B"],
            ["B", "A", "C"],
        ]

        consensus = aggregate_rankings(rankings)

        # A appears high in all rankings
        assert consensus[0] == "A"
        assert "B" in consensus
        assert "C" in consensus

    def test_weighted_rankings(self):
        """Test weighted ranking aggregation."""
        rankings = [
            ["A", "B", "C"],
            ["C", "B", "A"],
        ]
        weights = [3.0, 1.0]  # First ranking has 3x weight

        consensus = aggregate_rankings(rankings, weights)

        # First ranking should dominate
        assert consensus[0] == "A"

    def test_different_items(self):
        """Test with different items in rankings."""
        rankings = [
            ["A", "B"],
            ["B", "C"],
            ["A", "C"],
        ]

        consensus = aggregate_rankings(rankings)

        # All items should appear
        assert len(consensus) == 3
        assert set(consensus) == {"A", "B", "C"}

    def test_empty_rankings(self):
        """Test with empty rankings."""
        consensus = aggregate_rankings([])
        assert consensus == []
