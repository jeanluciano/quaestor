"""Analytics engine for exception patterns and insights."""

from collections import defaultdict
from datetime import datetime
from typing import Any

from .exception_tracker import ExceptionEvent, ExceptionTracker


class ExceptionAnalytics:
    """Analyze exception patterns and generate insights."""

    def __init__(self, tracker: ExceptionTracker):
        self.tracker = tracker

    def analyze_rule_performance(self, rule_id: str, days: int = 30) -> dict[str, Any]:
        """Analyze performance metrics for a specific rule."""
        events = self.tracker.get_events_for_rule(rule_id, hours=days * 24)

        if not events:
            return {"error": "No events found for rule"}

        # Basic metrics
        total_events = len(events)
        overrides = [e for e in events if e.outcome == "overridden"]
        violations = [e for e in events if e.event_type == "violation"]
        adaptations = [e for e in events if e.event_type == "adaptation"]

        # Time-based analysis
        daily_counts = self._calculate_daily_counts(events, days)
        trend = self._calculate_trend(daily_counts)

        # Context analysis
        context_patterns = self._analyze_contexts(events)

        # Enforcement level effectiveness
        level_effectiveness = self._analyze_level_effectiveness(events)

        return {
            "rule_id": rule_id,
            "period_days": days,
            "total_events": total_events,
            "override_count": len(overrides),
            "override_rate": len(overrides) / total_events if total_events > 0 else 0,
            "violation_count": len(violations),
            "adaptation_count": len(adaptations),
            "daily_average": total_events / days if days > 0 else 0,
            "trend": trend,
            "context_patterns": context_patterns,
            "level_effectiveness": level_effectiveness,
            "recommendations": self._generate_recommendations(
                total_events, len(overrides), context_patterns, level_effectiveness
            ),
        }

    def _calculate_daily_counts(self, events: list[ExceptionEvent], days: int) -> list[int]:
        """Calculate daily event counts."""
        counts = [0] * days
        now = datetime.now()

        for event in events:
            event_date = datetime.fromtimestamp(event.timestamp)
            days_ago = (now - event_date).days

            if 0 <= days_ago < days:
                counts[days - days_ago - 1] += 1

        return counts

    def _calculate_trend(self, daily_counts: list[int]) -> str:
        """Calculate trend from daily counts."""
        if len(daily_counts) < 7:
            return "insufficient_data"

        # Compare last week to previous week
        last_week = sum(daily_counts[-7:])
        prev_week = sum(daily_counts[-14:-7])

        if prev_week == 0:
            return "increasing" if last_week > 0 else "stable"

        change_ratio = (last_week - prev_week) / prev_week

        if change_ratio > 0.2:
            return "increasing"
        elif change_ratio < -0.2:
            return "decreasing"
        else:
            return "stable"

    def _analyze_contexts(self, events: list[ExceptionEvent]) -> dict[str, Any]:
        """Analyze common context patterns."""
        patterns = {
            "workflow_phases": defaultdict(int),
            "developer_experience": {"high": 0, "medium": 0, "low": 0},
            "time_pressure": {"high": 0, "medium": 0, "low": 0},
            "file_types": defaultdict(int),
        }

        for event in events:
            context = event.context

            # Workflow phase
            phase = context.get("workflow_phase", "unknown")
            patterns["workflow_phases"][phase] += 1

            # Developer experience
            exp = context.get("developer_experience", 0.5)
            if exp > 0.7:
                patterns["developer_experience"]["high"] += 1
            elif exp > 0.3:
                patterns["developer_experience"]["medium"] += 1
            else:
                patterns["developer_experience"]["low"] += 1

            # Time pressure
            pressure = context.get("time_pressure", 0.5)
            if pressure > 0.7:
                patterns["time_pressure"]["high"] += 1
            elif pressure > 0.3:
                patterns["time_pressure"]["medium"] += 1
            else:
                patterns["time_pressure"]["low"] += 1

            # File types
            file_path = context.get("file_path", "")
            if file_path:
                if file_path.endswith(".py"):
                    patterns["file_types"]["python"] += 1
                elif file_path.endswith((".js", ".ts")):
                    patterns["file_types"]["javascript"] += 1
                elif file_path.endswith(".md"):
                    patterns["file_types"]["markdown"] += 1
                else:
                    patterns["file_types"]["other"] += 1

        return {
            "workflow_phases": dict(patterns["workflow_phases"]),
            "developer_experience": patterns["developer_experience"],
            "time_pressure": patterns["time_pressure"],
            "file_types": dict(patterns["file_types"]),
        }

    def _analyze_level_effectiveness(self, events: list[ExceptionEvent]) -> dict[str, Any]:
        """Analyze effectiveness of different enforcement levels."""
        level_stats = defaultdict(lambda: {"total": 0, "overridden": 0})

        for event in events:
            level = event.enforcement_level
            level_stats[level]["total"] += 1
            if event.outcome == "overridden":
                level_stats[level]["overridden"] += 1

        effectiveness = {}
        for level, stats in level_stats.items():
            total = stats["total"]
            overridden = stats["overridden"]

            effectiveness[level] = {
                "total_enforcements": total,
                "overrides": overridden,
                "override_rate": overridden / total if total > 0 else 0,
                "effectiveness": 1 - (overridden / total) if total > 0 else 1,
            }

        return effectiveness

    def _generate_recommendations(
        self,
        total_events: int,
        override_count: int,
        context_patterns: dict[str, Any],
        level_effectiveness: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check override rate
        override_rate = override_count / total_events if total_events > 0 else 0
        if override_rate > 0.3:
            recommendations.append(
                f"High override rate ({override_rate:.1%}). Consider relaxing enforcement or adding exceptions."
            )

        # Check phase patterns
        phases = context_patterns.get("workflow_phases", {})
        if phases.get("research", 0) > total_events * 0.4:
            recommendations.append("Many events during research phase. Consider more lenient rules for exploration.")

        # Check developer experience
        dev_exp = context_patterns.get("developer_experience", {})
        if dev_exp.get("high", 0) > total_events * 0.5:
            recommendations.append("Mostly experienced developers affected. Consider trust-based adaptations.")

        # Check level effectiveness
        for level, stats in level_effectiveness.items():
            if stats["override_rate"] > 0.5 and stats["total_enforcements"] > 5:
                recommendations.append(
                    f"{level} level has {stats['override_rate']:.0%} override rate. Consider adjusting."
                )

        return recommendations

    def compare_rules(self, rule_ids: list[str], days: int = 30) -> dict[str, Any]:
        """Compare performance across multiple rules."""
        comparisons = {}

        for rule_id in rule_ids:
            analysis = self.analyze_rule_performance(rule_id, days)
            if "error" not in analysis:
                comparisons[rule_id] = {
                    "override_rate": analysis["override_rate"],
                    "daily_average": analysis["daily_average"],
                    "trend": analysis["trend"],
                    "total_events": analysis["total_events"],
                }

        # Calculate rankings
        if comparisons:
            # Rank by override rate (lower is better)
            override_ranking = sorted(comparisons.items(), key=lambda x: x[1]["override_rate"])

            # Rank by event frequency (lower might be better)
            frequency_ranking = sorted(comparisons.items(), key=lambda x: x[1]["daily_average"], reverse=True)

            return {
                "comparisons": comparisons,
                "best_performing": override_ranking[0][0] if override_ranking else None,
                "most_active": frequency_ranking[0][0] if frequency_ranking else None,
                "rankings": {
                    "by_override_rate": [r[0] for r in override_ranking],
                    "by_frequency": [r[0] for r in frequency_ranking],
                },
            }

        return {"error": "No data available for comparison"}

    def generate_insights(self, days: int = 30) -> list[dict[str, Any]]:
        """Generate high-level insights across all rules."""
        all_events = self.tracker.get_recent_events(hours=days * 24)

        if not all_events:
            return []

        insights = []

        # Insight 1: Most problematic rules
        rule_overrides = defaultdict(int)
        rule_totals = defaultdict(int)

        for event in all_events:
            rule_totals[event.rule_id] += 1
            if event.outcome == "overridden":
                rule_overrides[event.rule_id] += 1

        problematic_rules = []
        for rule_id, total in rule_totals.items():
            override_rate = rule_overrides[rule_id] / total
            if override_rate > 0.3 and total > 10:
                problematic_rules.append((rule_id, override_rate, total))

        if problematic_rules:
            problematic_rules.sort(key=lambda x: x[1], reverse=True)
            insights.append(
                {
                    "type": "problematic_rules",
                    "title": "Rules with High Override Rates",
                    "description": "These rules are frequently overridden and may need adjustment",
                    "data": [
                        {"rule_id": rule_id, "override_rate": rate, "total_events": total}
                        for rule_id, rate, total in problematic_rules[:5]
                    ],
                }
            )

        # Insight 2: Time-based patterns
        hour_counts = defaultdict(int)
        for event in all_events:
            hour = datetime.fromtimestamp(event.timestamp).hour
            hour_counts[hour] += 1

        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if peak_hours:
            insights.append(
                {
                    "type": "time_patterns",
                    "title": "Peak Activity Hours",
                    "description": "Most rule events occur during these hours",
                    "data": [{"hour": f"{hour:02d}:00", "count": count} for hour, count in peak_hours],
                }
            )

        # Insight 3: Context correlations
        high_pressure_overrides = sum(
            1 for e in all_events if e.outcome == "overridden" and e.context.get("time_pressure", 0) > 0.7
        )

        if high_pressure_overrides > len(all_events) * 0.1:
            insights.append(
                {
                    "type": "context_correlation",
                    "title": "Time Pressure Correlation",
                    "description": "High time pressure correlates with override requests",
                    "data": {
                        "high_pressure_overrides": high_pressure_overrides,
                        "percentage": high_pressure_overrides / len(all_events),
                    },
                }
            )

        return insights
