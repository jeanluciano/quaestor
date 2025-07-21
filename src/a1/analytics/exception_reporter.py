"""Generate reports for exception tracking and analytics."""

import json
from datetime import datetime
from pathlib import Path

from .exception_analytics import ExceptionAnalytics
from .exception_tracker import ExceptionTracker


class ExceptionReporter:
    """Generate various reports from exception data."""

    def __init__(self, tracker: ExceptionTracker):
        self.tracker = tracker
        self.analytics = ExceptionAnalytics(tracker)

    def generate_summary_report(self, days: int = 7, output_path: Path | None = None) -> str:
        """Generate a summary report for the specified period."""
        report_lines = []

        # Header
        report_lines.append("# A1 Rule Intelligence - Exception Summary Report")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Period: Last {days} days\n")

        # Overall statistics
        summary = self.tracker.get_event_summary(hours=days * 24)
        report_lines.append("## Overall Statistics")
        report_lines.append(f"- Total Events: {summary['total_events']}")
        report_lines.append(f"- Override Rate: {summary['override_rate']:.1%}")
        report_lines.append("")

        # Events by type
        report_lines.append("### Events by Type")
        for event_type, count in summary["by_type"].items():
            percentage = (count / summary["total_events"] * 100) if summary["total_events"] > 0 else 0
            report_lines.append(f"- {event_type}: {count} ({percentage:.1f}%)")
        report_lines.append("")

        # Events by enforcement level
        report_lines.append("### Events by Enforcement Level")
        for level, count in summary["by_level"].items():
            percentage = (count / summary["total_events"] * 100) if summary["total_events"] > 0 else 0
            report_lines.append(f"- {level}: {count} ({percentage:.1f}%)")
        report_lines.append("")

        # Top rules by activity
        report_lines.append("## Top Rules by Activity")
        top_rules = sorted(summary["by_rule"].items(), key=lambda x: x[1], reverse=True)[:10]

        for i, (rule_id, count) in enumerate(top_rules, 1):
            report_lines.append(f"{i}. {rule_id}: {count} events")
        report_lines.append("")

        # Insights
        insights = self.analytics.generate_insights(days)
        if insights:
            report_lines.append("## Key Insights")
            for insight in insights:
                report_lines.append(f"\n### {insight['title']}")
                report_lines.append(insight["description"])

                if insight["type"] == "problematic_rules":
                    for rule in insight["data"]:
                        report_lines.append(
                            f"- {rule['rule_id']}: {rule['override_rate']:.1%} override rate "
                            f"({rule['total_events']} events)"
                        )
                elif insight["type"] == "time_patterns":
                    for hour_data in insight["data"]:
                        report_lines.append(f"- {hour_data['hour']}: {hour_data['count']} events")
                elif insight["type"] == "context_correlation":
                    data = insight["data"]
                    report_lines.append(
                        f"- {data['high_pressure_overrides']} overrides under high pressure "
                        f"({data['percentage']:.1%} of all events)"
                    )

        report_text = "\n".join(report_lines)

        # Save if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_text)

        return report_text

    def generate_rule_report(self, rule_id: str, days: int = 30, output_path: Path | None = None) -> str:
        """Generate detailed report for a specific rule."""
        analysis = self.analytics.analyze_rule_performance(rule_id, days)

        if "error" in analysis:
            return f"Error: {analysis['error']}"

        report_lines = []

        # Header
        report_lines.append(f"# Rule Report: {rule_id}")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Period: Last {days} days\n")

        # Key metrics
        report_lines.append("## Key Metrics")
        report_lines.append(f"- Total Events: {analysis['total_events']}")
        report_lines.append(f"- Override Rate: {analysis['override_rate']:.1%}")
        report_lines.append(f"- Daily Average: {analysis['daily_average']:.1f}")
        report_lines.append(f"- Trend: {analysis['trend']}")
        report_lines.append("")

        # Context patterns
        report_lines.append("## Context Analysis")
        context = analysis["context_patterns"]

        report_lines.append("\n### Workflow Phases")
        for phase, count in context["workflow_phases"].items():
            report_lines.append(f"- {phase}: {count}")

        report_lines.append("\n### Developer Experience Distribution")
        for level, count in context["developer_experience"].items():
            report_lines.append(f"- {level}: {count}")

        report_lines.append("\n### Time Pressure Distribution")
        for level, count in context["time_pressure"].items():
            report_lines.append(f"- {level}: {count}")

        # Level effectiveness
        report_lines.append("\n## Enforcement Level Effectiveness")
        for level, stats in analysis["level_effectiveness"].items():
            report_lines.append(f"\n### {level}")
            report_lines.append(f"- Total Enforcements: {stats['total_enforcements']}")
            report_lines.append(f"- Overrides: {stats['overrides']}")
            report_lines.append(f"- Override Rate: {stats['override_rate']:.1%}")
            report_lines.append(f"- Effectiveness: {stats['effectiveness']:.1%}")

        # Recommendations
        if analysis["recommendations"]:
            report_lines.append("\n## Recommendations")
            for rec in analysis["recommendations"]:
                report_lines.append(f"- {rec}")

        # Pattern detection
        patterns = self.tracker.find_patterns(rule_id)
        if patterns:
            report_lines.append("\n## Detected Patterns")
            for pattern in patterns[:5]:
                report_lines.append(
                    f"- {pattern['type']}: {pattern['pattern']} "
                    f"({pattern['frequency']} occurrences, {pattern['percentage']:.1%})"
                )

        report_text = "\n".join(report_lines)

        # Save if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_text)

        return report_text

    def generate_comparison_report(self, rule_ids: list[str], days: int = 30, output_path: Path | None = None) -> str:
        """Generate comparison report for multiple rules."""
        comparison = self.analytics.compare_rules(rule_ids, days)

        if "error" in comparison:
            return f"Error: {comparison['error']}"

        report_lines = []

        # Header
        report_lines.append("# Rule Comparison Report")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Period: Last {days} days")
        report_lines.append(f"Rules Compared: {', '.join(rule_ids)}\n")

        # Best performing
        if comparison["best_performing"]:
            report_lines.append(f"## Best Performing Rule: {comparison['best_performing']}")
            report_lines.append("(Lowest override rate)\n")

        # Most active
        if comparison["most_active"]:
            report_lines.append(f"## Most Active Rule: {comparison['most_active']}")
            report_lines.append("(Highest event frequency)\n")

        # Detailed comparison
        report_lines.append("## Detailed Comparison")
        report_lines.append("| Rule ID | Override Rate | Daily Average | Trend | Total Events |")
        report_lines.append("|---------|---------------|---------------|-------|--------------|")

        for rule_id, metrics in comparison["comparisons"].items():
            report_lines.append(
                f"| {rule_id} | {metrics['override_rate']:.1%} | "
                f"{metrics['daily_average']:.1f} | {metrics['trend']} | "
                f"{metrics['total_events']} |"
            )

        # Rankings
        report_lines.append("\n## Rankings")
        report_lines.append("\n### By Override Rate (Best to Worst)")
        for i, rule_id in enumerate(comparison["rankings"]["by_override_rate"], 1):
            rate = comparison["comparisons"][rule_id]["override_rate"]
            report_lines.append(f"{i}. {rule_id} ({rate:.1%})")

        report_lines.append("\n### By Frequency (Most to Least)")
        for i, rule_id in enumerate(comparison["rankings"]["by_frequency"], 1):
            freq = comparison["comparisons"][rule_id]["daily_average"]
            report_lines.append(f"{i}. {rule_id} ({freq:.1f} per day)")

        report_text = "\n".join(report_lines)

        # Save if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_text)

        return report_text

    def export_data(self, output_path: Path, format: str = "json", days: int = 30) -> None:
        """Export raw event data for external analysis."""
        events = self.tracker.get_recent_events(hours=days * 24)

        if format == "json":
            data = {
                "export_date": datetime.now().isoformat(),
                "period_days": days,
                "total_events": len(events),
                "events": [e.to_dict() for e in events],
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

        elif format == "csv":
            import csv

            with open(output_path, "w", newline="") as f:
                if events:
                    # Get all possible fields from events
                    fieldnames = [
                        "id",
                        "timestamp",
                        "datetime",
                        "rule_id",
                        "event_type",
                        "outcome",
                        "enforcement_level",
                        "justification",
                    ]

                    # Add context fields
                    context_fields = set()
                    for event in events:
                        context_fields.update(event.context.keys())

                    fieldnames.extend([f"context_{field}" for field in sorted(context_fields)])

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for event in events:
                        row = {
                            "id": event.id,
                            "timestamp": event.timestamp,
                            "datetime": event.datetime.isoformat(),
                            "rule_id": event.rule_id,
                            "event_type": event.event_type,
                            "outcome": event.outcome,
                            "enforcement_level": event.enforcement_level,
                            "justification": event.justification or "",
                        }

                        # Add context fields
                        for field, value in event.context.items():
                            row[f"context_{field}"] = str(value)

                        writer.writerow(row)
