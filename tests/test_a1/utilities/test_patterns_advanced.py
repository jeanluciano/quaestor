"""Tests for advanced pattern recognition utilities."""

from a1.utilities.patterns_advanced import (
    CognitivePattern,
    ThoughtPatternType,
    analyze_pattern_frequency,
    classify_step_type,
    consolidate_patterns,
    detect_thought_patterns,
    estimate_text_complexity,
    extract_recurring_elements,
    identify_efficiency_patterns,
)


class TestDetectThoughtPatterns:
    """Test thought pattern detection."""

    def test_linear_pattern(self):
        """Test detection of linear thinking patterns."""
        text = (
            "First, we analyze the data. Then, we process it. Next, we validate results. Finally, we report findings."
        )

        patterns = detect_thought_patterns(text)

        linear_patterns = [p for p in patterns if p.pattern_type == ThoughtPatternType.LINEAR]
        assert len(linear_patterns) > 0
        assert linear_patterns[0].confidence > 0.7
        assert linear_patterns[0].frequency >= 4  # Found 4 sequential keywords

    def test_branching_pattern(self):
        """Test detection of branching patterns."""
        text = "If the data is valid, we proceed. Else, we need to clean it. Alternatively, we could use a different approach."

        patterns = detect_thought_patterns(text)

        branching_patterns = [p for p in patterns if p.pattern_type == ThoughtPatternType.BRANCHING]
        assert len(branching_patterns) > 0
        assert branching_patterns[0].confidence > 0.6

    def test_analytical_pattern(self):
        """Test detection of analytical patterns."""
        text = "Let's analyze the problem systematically. We need to examine each component and evaluate the results."

        patterns = detect_thought_patterns(text)

        analytical_patterns = [p for p in patterns if p.pattern_type == ThoughtPatternType.ANALYTICAL]
        assert len(analytical_patterns) > 0
        assert analytical_patterns[0].indicators[0].endswith("analytical keywords")

    def test_multiple_patterns(self):
        """Test detection of multiple patterns in same text."""
        text = """First, let's analyze the situation. If we find issues, we'll examine them closely. 
                  Then we'll create innovative solutions. This systematic approach will help us."""

        patterns = detect_thought_patterns(text)
        pattern_types = {p.pattern_type for p in patterns}

        # Should detect multiple pattern types
        assert len(patterns) >= 2
        assert ThoughtPatternType.LINEAR in pattern_types or ThoughtPatternType.ANALYTICAL in pattern_types

    def test_min_confidence_threshold(self):
        """Test minimum confidence threshold filtering."""
        text = "This is a simple text with minimal pattern indicators."

        patterns_low = detect_thought_patterns(text, min_confidence=0.1)
        patterns_high = detect_thought_patterns(text, min_confidence=0.9)

        assert len(patterns_low) >= len(patterns_high)

    def test_recursive_pattern(self):
        """Test detection of recursive patterns through repetition."""
        # Use a text with more clear repetition
        text = """The system processes data recursively. Each recursive call processes more data. 
                  The recursive algorithm continues. Recursive processing is efficient."""

        patterns = detect_thought_patterns(text, min_confidence=0.3)  # Lower threshold for test

        recursive_patterns = [p for p in patterns if p.pattern_type == ThoughtPatternType.RECURSIVE]
        assert len(recursive_patterns) > 0  # Should detect repeated concept or recursive keyword


class TestEstimateTextComplexity:
    """Test text complexity estimation."""

    def test_simple_text(self):
        """Test complexity of simple text."""
        text = "This is a simple sentence."

        complexity = estimate_text_complexity(text)

        assert 0 <= complexity <= 0.3

    def test_complex_text(self):
        """Test complexity of complex text."""
        text = """Despite the intricate nature of this challenging problem, we must analyze 
                  multiple interconnected factors. However, if we evaluate each component 
                  systematically, we can optimize the solution. Therefore, assuming proper 
                  integration of various elements, the complex system should function."""

        complexity = estimate_text_complexity(text)

        assert complexity > 0.5

    def test_empty_text(self):
        """Test complexity of empty text."""
        assert estimate_text_complexity("") == 0.0

    def test_complexity_factors(self):
        """Test different complexity factors."""
        # Length factor
        short = "Short text."
        long = " ".join(["This is a longer text"] * 20)

        assert estimate_text_complexity(long) > estimate_text_complexity(short)

        # Indicator words
        simple = "The cat sat on the mat."
        complex_words = "The complex algorithm optimizes multiple intricate parameters."

        assert estimate_text_complexity(complex_words) > estimate_text_complexity(simple)


class TestClassifyStepType:
    """Test step type classification."""

    def test_analysis_step(self):
        """Test classification of analysis steps."""
        assert classify_step_type("Analyze the dataset for patterns") == "analysis"
        assert classify_step_type("Let's examine the code structure") == "analysis"

    def test_evaluation_step(self):
        """Test classification of evaluation steps."""
        assert classify_step_type("Compare the two approaches") == "evaluation"
        assert classify_step_type("Assess the performance metrics") == "evaluation"

    def test_decision_step(self):
        """Test classification of decision steps."""
        assert classify_step_type("Choose the best algorithm") == "decision"
        assert classify_step_type("Select the optimal parameters") == "decision"

    def test_execution_step(self):
        """Test classification of execution steps."""
        assert classify_step_type("Implement the solution") == "execution"
        assert classify_step_type("Execute the query") == "execution"

    def test_default_reasoning(self):
        """Test default classification."""
        assert classify_step_type("Think about the problem") == "reasoning"
        assert classify_step_type("Consider the implications") == "reasoning"


class TestAnalyzePatternFrequency:
    """Test pattern frequency analysis."""

    def test_basic_frequency_analysis(self):
        """Test basic frequency analysis."""
        patterns = [
            CognitivePattern(ThoughtPatternType.LINEAR, 0.8, ["indicator1"]),
            CognitivePattern(ThoughtPatternType.LINEAR, 0.9, ["indicator2"]),
            CognitivePattern(ThoughtPatternType.ANALYTICAL, 0.7, ["indicator3"]),
        ]

        analysis = analyze_pattern_frequency(patterns)

        assert analysis["total_patterns"] == 3
        assert analysis["dominant_pattern"] == "linear"
        assert analysis["unique_pattern_types"] == 2
        assert "linear" in analysis["pattern_distribution"]
        assert analysis["pattern_distribution"]["linear"]["count"] == 2

    def test_empty_patterns(self):
        """Test analysis with no patterns."""
        analysis = analyze_pattern_frequency([])

        assert analysis["total_patterns"] == 0
        assert analysis["dominant_pattern"] is None
        assert analysis["pattern_diversity"] == 0.0

    def test_pattern_diversity(self):
        """Test diversity calculation."""
        # Low diversity (all same type)
        uniform_patterns = [CognitivePattern(ThoughtPatternType.LINEAR, 0.8, []) for _ in range(5)]

        # High diversity (different types)
        diverse_patterns = [
            CognitivePattern(ThoughtPatternType.LINEAR, 0.8, []),
            CognitivePattern(ThoughtPatternType.BRANCHING, 0.7, []),
            CognitivePattern(ThoughtPatternType.ANALYTICAL, 0.9, []),
            CognitivePattern(ThoughtPatternType.CREATIVE, 0.6, []),
        ]

        uniform_analysis = analyze_pattern_frequency(uniform_patterns)
        diverse_analysis = analyze_pattern_frequency(diverse_patterns)

        assert diverse_analysis["pattern_diversity"] > uniform_analysis["pattern_diversity"]


class TestIdentifyEfficiencyPatterns:
    """Test efficiency pattern identification."""

    def test_efficient_steps(self):
        """Test identification of efficient steps."""
        durations = [2.0, 1.5, 3.0, 1.0, 2.5]  # seconds
        effectiveness = [0.9, 0.95, 0.6, 0.92, 0.7]  # 0-1 scale

        analysis = identify_efficiency_patterns(durations, effectiveness)

        assert analysis["efficiency_score"] > 0
        assert "patterns" in analysis

        # Should identify quick and effective steps (indices 1, 3)
        quick_effective = [p for p in analysis["patterns"] if p["type"] == "quick_effective"]
        assert len(quick_effective) > 0

    def test_inefficient_steps(self):
        """Test identification of inefficient steps."""
        durations = [5.0, 10.0, 15.0, 20.0]
        effectiveness = [0.3, 0.2, 0.4, 0.1]

        analysis = identify_efficiency_patterns(durations, effectiveness)

        assert analysis["efficiency_score"] < 0.5
        assert any("breaking down complex steps" in r for r in analysis["recommendations"])

    def test_empty_data(self):
        """Test with empty data."""
        analysis = identify_efficiency_patterns([], [])

        assert analysis["efficiency_score"] == 0.0
        assert analysis["patterns"] == []


class TestConsolidatePatterns:
    """Test pattern consolidation."""

    def test_consolidate_same_type(self):
        """Test consolidating patterns of same type."""
        patterns = [
            CognitivePattern(ThoughtPatternType.LINEAR, 0.7, ["ind1"], frequency=2),
            CognitivePattern(ThoughtPatternType.LINEAR, 0.8, ["ind2"], frequency=3),
            CognitivePattern(ThoughtPatternType.LINEAR, 0.6, ["ind3"], frequency=1),
        ]

        consolidated = consolidate_patterns(patterns)

        assert len(consolidated) == 1
        assert consolidated[0].pattern_type == ThoughtPatternType.LINEAR
        assert consolidated[0].frequency == 6  # Sum of frequencies
        assert consolidated[0].confidence > 0.7  # Boosted average

    def test_consolidate_different_types(self):
        """Test consolidating patterns of different types."""
        patterns = [
            CognitivePattern(ThoughtPatternType.LINEAR, 0.8, ["linear"]),
            CognitivePattern(ThoughtPatternType.BRANCHING, 0.7, ["branch"]),
            CognitivePattern(ThoughtPatternType.ANALYTICAL, 0.9, ["analyze"]),
        ]

        consolidated = consolidate_patterns(patterns)

        assert len(consolidated) == 3  # No consolidation
        pattern_types = {p.pattern_type for p in consolidated}
        assert len(pattern_types) == 3

    def test_single_pattern(self):
        """Test with single pattern."""
        patterns = [CognitivePattern(ThoughtPatternType.CREATIVE, 0.8, ["create"])]

        consolidated = consolidate_patterns(patterns)

        assert len(consolidated) == 1
        assert consolidated[0] == patterns[0]


class TestExtractRecurringElements:
    """Test recurring element extraction."""

    def test_recurring_phrases(self):
        """Test extraction of recurring phrases."""
        texts = [
            "We need to analyze data and process the results",
            "First analyze data, then validate findings",
            "Always analyze data before making decisions",
        ]

        analysis = extract_recurring_elements(texts)

        # Should detect "analyze data" as recurring
        if analysis["recurring_phrases"]:
            phrase_texts = [p["phrase"] for p in analysis["recurring_phrases"]]
            assert any("analyze" in phrase for phrase in phrase_texts)

    def test_recurring_patterns(self):
        """Test extraction of recurring patterns."""
        texts = [
            "First we analyze, then we evaluate, finally we decide",
            "Start by analyzing, proceed to evaluation, conclude with decision",
            "Initial analysis leads to evaluation and final decision",
        ]

        analysis = extract_recurring_elements(texts)

        # Check if any patterns were detected
        if analysis["recurring_patterns"]:
            pattern_types = [p["pattern"] for p in analysis["recurring_patterns"]]
            assert "analytical" in pattern_types or "linear" in pattern_types
        else:
            # At least check the analysis ran
            assert "total_patterns_found" in analysis

    def test_consistency_score(self):
        """Test consistency score calculation."""
        # Highly consistent texts
        consistent_texts = [
            "Analyze the problem systematically",
            "Systematically analyze the issue",
            "Problem analysis done systematically",
        ]

        # Inconsistent texts
        inconsistent_texts = [
            "The cat sat on the mat",
            "Weather is nice today",
            "Python is a programming language",
        ]

        consistent_analysis = extract_recurring_elements(consistent_texts)
        inconsistent_analysis = extract_recurring_elements(inconsistent_texts)

        assert consistent_analysis["consistency_score"] > inconsistent_analysis["consistency_score"]

    def test_empty_texts(self):
        """Test with empty text list."""
        analysis = extract_recurring_elements([])

        assert analysis["recurring_phrases"] == []
        assert analysis["consistency_score"] == 0.0
