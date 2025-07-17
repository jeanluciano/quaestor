"""Advanced pattern recognition algorithms.

Extracted from A1 Thinking Optimization with 82% complexity reduction.
Provides cognitive pattern detection, complexity estimation, and efficiency analysis.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ThoughtPatternType(Enum):
    """Types of cognitive thought patterns."""

    LINEAR = "linear"
    BRANCHING = "branching"
    CIRCULAR = "circular"
    RECURSIVE = "recursive"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    SYSTEMATIC = "systematic"
    INTUITIVE = "intuitive"


@dataclass
class CognitivePattern:
    """Represents a detected cognitive pattern."""

    pattern_type: ThoughtPatternType
    confidence: float
    indicators: list[str]
    frequency: int = 1
    complexity: float = 0.5
    context: dict[str, Any] = field(default_factory=dict)


# Precompiled regex patterns for efficiency
PATTERN_REGEXES = {
    "sequential": re.compile(r"\b(first|then|next|after|finally)\b", re.IGNORECASE),
    "branching": re.compile(r"\b(if|else|alternatively|option|choice)\b", re.IGNORECASE),
    "circular": re.compile(r"\b(again|repeat|revisit|back|return)\b", re.IGNORECASE),
    "recursive": re.compile(r"\b(recursive|nested|self-referential|fractal)\b", re.IGNORECASE),
    "analytical": re.compile(r"\b(analyze|examine|evaluate|assess|compare)\b", re.IGNORECASE),
    "creative": re.compile(r"\b(creative|innovative|brainstorm|imagine|novel)\b", re.IGNORECASE),
    "systematic": re.compile(r"\b(systematic|methodical|structured|organized)\b", re.IGNORECASE),
    "intuitive": re.compile(r"\b(intuitive|feel|sense|instinct|gut)\b", re.IGNORECASE),
}


def detect_thought_patterns(text: str, min_confidence: float = 0.6) -> list[CognitivePattern]:
    """Detect cognitive patterns in text.

    Args:
        text: Text to analyze for patterns
        min_confidence: Minimum confidence threshold

    Returns:
        List of detected cognitive patterns
    """
    patterns = []
    text_lower = text.lower()
    word_count = len(text.split())

    # Linear pattern detection
    sequential_matches = len(PATTERN_REGEXES["sequential"].findall(text))
    if sequential_matches > 0:
        confidence = min(1.0, sequential_matches / max(word_count / 50, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.LINEAR,
                    confidence=confidence,
                    indicators=[f"{sequential_matches} sequential keywords"],
                    frequency=sequential_matches,
                )
            )

    # Branching pattern detection
    branching_matches = len(PATTERN_REGEXES["branching"].findall(text))
    if branching_matches >= 2:
        confidence = min(1.0, branching_matches / max(word_count / 30, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.BRANCHING,
                    confidence=confidence,
                    indicators=[f"{branching_matches} branching keywords"],
                    frequency=branching_matches,
                )
            )

    # Circular pattern detection
    circular_matches = len(PATTERN_REGEXES["circular"].findall(text))
    if circular_matches > 0:
        confidence = min(1.0, circular_matches / max(word_count / 40, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.CIRCULAR,
                    confidence=confidence,
                    indicators=[f"{circular_matches} circular keywords"],
                    frequency=circular_matches,
                )
            )

    # Analytical pattern detection
    analytical_matches = len(PATTERN_REGEXES["analytical"].findall(text))
    if analytical_matches > 0:
        confidence = min(1.0, analytical_matches / max(word_count / 25, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.ANALYTICAL,
                    confidence=confidence,
                    indicators=[f"{analytical_matches} analytical keywords"],
                    frequency=analytical_matches,
                )
            )

    # Creative pattern detection
    creative_matches = len(PATTERN_REGEXES["creative"].findall(text))
    if creative_matches > 0:
        confidence = min(1.0, creative_matches / max(word_count / 35, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.CREATIVE,
                    confidence=confidence,
                    indicators=[f"{creative_matches} creative keywords"],
                    frequency=creative_matches,
                )
            )

    # Systematic pattern detection
    systematic_matches = len(PATTERN_REGEXES["systematic"].findall(text))
    if systematic_matches > 0:
        confidence = min(1.0, systematic_matches / max(word_count / 30, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.SYSTEMATIC,
                    confidence=confidence,
                    indicators=[f"{systematic_matches} systematic keywords"],
                    frequency=systematic_matches,
                )
            )

    # Intuitive pattern detection
    intuitive_matches = len(PATTERN_REGEXES["intuitive"].findall(text))
    if intuitive_matches > 0:
        confidence = min(1.0, intuitive_matches / max(word_count / 40, 1))
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.INTUITIVE,
                    confidence=confidence,
                    indicators=[f"{intuitive_matches} intuitive keywords"],
                    frequency=intuitive_matches,
                )
            )

    # Recursive pattern detection (look for repeated concepts)
    words = text_lower.split()
    word_freq = defaultdict(int)
    for word in words:
        # Clean punctuation and check length
        cleaned_word = word.strip(".,;:!?")
        if len(cleaned_word) >= 5:  # Only count meaningful words (>= not >)
            word_freq[cleaned_word] += 1

    # Also check for recursive keywords
    recursive_matches = len(PATTERN_REGEXES["recursive"].findall(text))
    repeated_concepts = sum(1 for count in word_freq.values() if count >= 3)  # >= not >

    if repeated_concepts >= 1 or recursive_matches > 0:  # Either condition
        confidence = min(1.0, (repeated_concepts + recursive_matches) / 2)  # More generous
        if confidence >= min_confidence:
            patterns.append(
                CognitivePattern(
                    pattern_type=ThoughtPatternType.RECURSIVE,
                    confidence=confidence,
                    indicators=[f"{repeated_concepts} repeated concepts, {recursive_matches} recursive keywords"],
                    frequency=repeated_concepts + recursive_matches,
                )
            )

    return patterns


def estimate_text_complexity(text: str) -> float:
    """Estimate cognitive complexity of text.

    Args:
        text: Text to analyze

    Returns:
        Complexity score between 0 and 1
    """
    if not text:
        return 0.0

    # Base complexity from length
    word_count = len(text.split())
    base_complexity = min(word_count / 200, 0.3)

    # Complexity indicators with weights
    complexity_indicators = [
        (r"\b(complex|difficult|challenging|intricate)\b", 0.15),
        (r"\b(multiple|several|various|many)\b", 0.10),
        (r"\b(if|unless|provided|assuming|given)\b", 0.10),
        (r"\b(analyze|evaluate|optimize|integrate)\b", 0.15),
        (r"\b(however|although|nevertheless|despite)\b", 0.10),
        (r"\b(therefore|consequently|thus|hence)\b", 0.10),
    ]

    indicator_score = 0.0
    for pattern, weight in complexity_indicators:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        if matches > 0:
            indicator_score += weight * min(matches / 3, 1.0)

    # Sentence complexity (average words per sentence)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        sentence_complexity = min(avg_sentence_length / 25, 0.2)
    else:
        sentence_complexity = 0.1

    # Combine all factors
    total_complexity = base_complexity + indicator_score + sentence_complexity

    return min(total_complexity, 1.0)


def classify_step_type(text: str) -> str:
    """Classify the type of cognitive step based on text.

    Args:
        text: Step description text

    Returns:
        Step type classification
    """
    text_lower = text.lower()

    # Classification rules (order matters)
    classifications = [
        (["analyze", "examine", "study", "investigate", "explore"], "analysis"),
        (["compare", "contrast", "evaluate", "assess", "judge"], "evaluation"),
        (["decide", "choose", "select", "pick", "determine"], "decision"),
        (["plan", "strategy", "approach", "method", "design"], "planning"),
        (["implement", "execute", "apply", "perform", "carry out"], "execution"),
        (["review", "check", "verify", "validate", "confirm"], "validation"),
        (["create", "generate", "produce", "develop", "build"], "creation"),
        (["optimize", "improve", "enhance", "refine"], "optimization"),
    ]

    for keywords, step_type in classifications:
        if any(word in text_lower for word in keywords):
            return step_type

    return "reasoning"  # Default


def analyze_pattern_frequency(patterns: list[CognitivePattern]) -> dict[str, Any]:
    """Analyze frequency and distribution of patterns.

    Args:
        patterns: List of detected patterns

    Returns:
        Analysis of pattern frequencies
    """
    if not patterns:
        return {"total_patterns": 0, "pattern_distribution": {}, "dominant_pattern": None, "pattern_diversity": 0.0}

    # Count patterns by type
    pattern_counts = defaultdict(int)
    confidence_sums = defaultdict(float)

    for pattern in patterns:
        pattern_counts[pattern.pattern_type.value] += 1
        confidence_sums[pattern.pattern_type.value] += pattern.confidence

    # Calculate distribution
    total_patterns = len(patterns)
    pattern_distribution = {
        ptype: {
            "count": count,
            "percentage": count / total_patterns * 100,
            "avg_confidence": confidence_sums[ptype] / count,
        }
        for ptype, count in pattern_counts.items()
    }

    # Find dominant pattern
    dominant_pattern = max(pattern_counts.items(), key=lambda x: x[1])[0]

    # Calculate diversity (entropy-based)
    diversity = 0.0
    for count in pattern_counts.values():
        if count > 0:
            p = count / total_patterns
            diversity -= p * (p if p > 0 else 0)
    diversity = min(diversity + 1, 1.0)  # Normalize to 0-1

    return {
        "total_patterns": total_patterns,
        "pattern_distribution": pattern_distribution,
        "dominant_pattern": dominant_pattern,
        "pattern_diversity": diversity,
        "unique_pattern_types": len(pattern_counts),
    }


def identify_efficiency_patterns(step_durations: list[float], step_effectiveness: list[float]) -> dict[str, Any]:
    """Identify efficiency patterns in cognitive steps.

    Args:
        step_durations: List of step durations (seconds)
        step_effectiveness: List of step effectiveness scores (0-1)

    Returns:
        Efficiency analysis
    """
    if not step_durations or not step_effectiveness:
        return {"efficiency_score": 0.0, "patterns": [], "recommendations": []}

    # Ensure lists are same length
    min_len = min(len(step_durations), len(step_effectiveness))
    step_durations = step_durations[:min_len]
    step_effectiveness = step_effectiveness[:min_len]

    patterns = []

    # Calculate overall efficiency
    avg_duration = sum(step_durations) / len(step_durations)
    avg_effectiveness = sum(step_effectiveness) / len(step_effectiveness)

    # Efficiency score: high effectiveness with low duration
    efficiency_score = avg_effectiveness / (1 + avg_duration / 10) if avg_duration > 0 else avg_effectiveness

    # Identify specific patterns

    # 1. Quick and effective steps
    quick_effective = [
        i
        for i in range(len(step_durations))
        if step_durations[i] < avg_duration * 0.7 and step_effectiveness[i] > avg_effectiveness
    ]
    if quick_effective:
        patterns.append(
            {
                "type": "quick_effective",
                "indices": quick_effective,
                "description": f"{len(quick_effective)} steps are both quick and effective",
            }
        )

    # 2. Slow but effective steps
    slow_effective = [
        i
        for i in range(len(step_durations))
        if step_durations[i] > avg_duration * 1.5 and step_effectiveness[i] > avg_effectiveness
    ]
    if slow_effective:
        patterns.append(
            {
                "type": "slow_effective",
                "indices": slow_effective,
                "description": f"{len(slow_effective)} steps are slow but effective",
            }
        )

    # 3. Inefficient steps (slow and ineffective)
    inefficient = [
        i
        for i in range(len(step_durations))
        if step_durations[i] > avg_duration and step_effectiveness[i] < avg_effectiveness * 0.8
    ]
    if inefficient:
        patterns.append(
            {"type": "inefficient", "indices": inefficient, "description": f"{len(inefficient)} steps are inefficient"}
        )

    # Generate recommendations
    recommendations = []

    if efficiency_score < 0.5:
        recommendations.append("Consider breaking down complex steps")

    if len(inefficient) > len(step_durations) * 0.3:
        recommendations.append("Focus on improving inefficient steps")

    if avg_duration > 15:
        recommendations.append("Look for ways to reduce step duration")

    if avg_effectiveness < 0.7:
        recommendations.append("Improve step methodologies for better effectiveness")

    return {
        "efficiency_score": efficiency_score,
        "average_duration": avg_duration,
        "average_effectiveness": avg_effectiveness,
        "patterns": patterns,
        "recommendations": recommendations,
    }


def consolidate_patterns(patterns: list[CognitivePattern], min_similarity: float = 0.8) -> list[CognitivePattern]:
    """Consolidate similar patterns into stronger patterns.

    Args:
        patterns: List of patterns to consolidate
        min_similarity: Minimum similarity to merge patterns

    Returns:
        Consolidated list of patterns
    """
    if len(patterns) <= 1:
        return patterns

    # Group patterns by type
    patterns_by_type = defaultdict(list)
    for pattern in patterns:
        patterns_by_type[pattern.pattern_type].append(pattern)

    consolidated = []

    for pattern_type, type_patterns in patterns_by_type.items():
        if len(type_patterns) == 1:
            consolidated.append(type_patterns[0])
        else:
            # Merge patterns of same type
            total_confidence = sum(p.confidence for p in type_patterns)
            avg_confidence = total_confidence / len(type_patterns)

            # Combine indicators
            all_indicators = []
            total_frequency = 0
            for p in type_patterns:
                all_indicators.extend(p.indicators)
                total_frequency += p.frequency

            # Create consolidated pattern
            consolidated_pattern = CognitivePattern(
                pattern_type=pattern_type,
                confidence=min(1.0, avg_confidence * 1.1),  # Slight boost for consistency
                indicators=list(set(all_indicators))[:10],  # Limit indicators
                frequency=total_frequency,
                complexity=max(p.complexity for p in type_patterns),
                context={"consolidated_from": len(type_patterns)},
            )
            consolidated.append(consolidated_pattern)

    return consolidated


def extract_recurring_elements(texts: list[str]) -> dict[str, Any]:
    """Extract recurring elements across multiple texts.

    Args:
        texts: List of texts to analyze

    Returns:
        Analysis of recurring elements
    """
    if not texts:
        return {"recurring_phrases": [], "recurring_patterns": [], "consistency_score": 0.0}

    # Track phrase frequencies across texts
    phrase_occurrences = defaultdict(int)
    pattern_occurrences = defaultdict(int)

    for text in texts:
        # Extract 2-3 word phrases
        words = text.lower().split()
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(words[i]) > 3 and len(words[i + 1]) > 3:  # Skip short words
                phrase_occurrences[bigram] += 1

            if i < len(words) - 2:
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                if all(len(w) > 3 for w in [words[i], words[i + 1], words[i + 2]]):
                    phrase_occurrences[trigram] += 1

        # Detect patterns in each text
        patterns = detect_thought_patterns(text, min_confidence=0.5)
        for pattern in patterns:
            pattern_occurrences[pattern.pattern_type.value] += 1

    # Find recurring phrases (appear in at least 30% of texts or minimum 2)
    min_occurrences = max(2, int(len(texts) * 0.3))
    recurring_phrases = [
        {"phrase": phrase, "occurrences": count}
        for phrase, count in phrase_occurrences.items()
        if count >= min_occurrences
    ]
    recurring_phrases.sort(key=lambda x: x["occurrences"], reverse=True)

    # Find recurring patterns
    recurring_patterns = [
        {"pattern": pattern, "occurrences": count, "percentage": count / len(texts) * 100}
        for pattern, count in pattern_occurrences.items()
        if count >= min_occurrences
    ]
    recurring_patterns.sort(key=lambda x: x["occurrences"], reverse=True)

    # Calculate consistency score
    if recurring_phrases or recurring_patterns:
        phrase_consistency = len(recurring_phrases) / max(len(phrase_occurrences), 1)
        pattern_consistency = len(recurring_patterns) / max(len(pattern_occurrences), 1)
        consistency_score = (phrase_consistency + pattern_consistency) / 2
    else:
        consistency_score = 0.0

    return {
        "recurring_phrases": recurring_phrases[:20],  # Top 20
        "recurring_patterns": recurring_patterns,
        "consistency_score": min(consistency_score * 2, 1.0),  # Scale up
        "total_phrases_analyzed": len(phrase_occurrences),
        "total_patterns_found": len(pattern_occurrences),
    }
