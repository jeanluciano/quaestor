"""Test file to demonstrate context-aware adaptation."""

from .context_factors import ContextFactorAnalyzer
from .enforcement_levels import EnforcementLevel
from .rule_adapter import RuleAdapter
from .rule_enforcer import EnforcementContext


def test_adaptation_examples():
    """Test various adaptation scenarios."""
    adapter = RuleAdapter()
    analyzer = ContextFactorAnalyzer()

    # Test scenarios
    scenarios = [
        {
            "name": "Junior developer implementing critical auth",
            "context": EnforcementContext(
                user_intent="implement authentication",
                workflow_phase="implementing",
                file_path="/src/auth/login.py",
                developer_experience=0.2,
                time_pressure=0.3,
                previous_violations=0,
            ),
            "base_level": EnforcementLevel.WARN,
        },
        {
            "name": "Senior developer doing hotfix",
            "context": EnforcementContext(
                user_intent="urgent hotfix for login bug",
                workflow_phase="implementing",
                file_path="/src/auth/login.py",
                developer_experience=0.9,
                time_pressure=0.9,
                previous_violations=0,
            ),
            "base_level": EnforcementLevel.WARN,
        },
        {
            "name": "Testing new feature",
            "context": EnforcementContext(
                user_intent="add tests for user registration",
                workflow_phase="implementing",
                file_path="/tests/test_registration.py",
                developer_experience=0.5,
                time_pressure=0.3,
                previous_violations=1,
            ),
            "base_level": EnforcementLevel.JUSTIFY,
        },
        {
            "name": "Documentation update",
            "context": EnforcementContext(
                user_intent="update API documentation",
                workflow_phase="implementing",
                file_path="/docs/api.md",
                developer_experience=0.6,
                time_pressure=0.2,
                previous_violations=0,
            ),
            "base_level": EnforcementLevel.JUSTIFY,
        },
    ]

    print("Context-Aware Adaptation Examples\n" + "=" * 40)

    for scenario in scenarios:
        context = scenario["context"]
        base_level = scenario["base_level"]

        # Detect strategy
        strategy = adapter.detect_strategy(context)

        # Adapt enforcement level
        adapted_level = adapter.adapt_enforcement_level(base_level, context)

        # Analyze context factors
        context.metadata = {
            "user_intent": context.user_intent,
            "file_path": context.file_path,
            "developer_experience": context.developer_experience,
        }
        context_summary = analyzer.get_context_summary(context.metadata)

        print(f"\nScenario: {scenario['name']}")
        print(f"  Intent: {context.user_intent}")
        print(f"  File: {context.file_path}")
        print(f"  Developer Experience: {context.developer_experience}")
        print(f"  Time Pressure: {context.time_pressure}")
        print(f"  Detected Strategy: {strategy.value}")
        print(f"  Base Level: {base_level.name}")
        print(f"  Adapted Level: {adapted_level.name}")
        print(f"  Risk Score: {context_summary['risk_score']:.2f}")
        print(f"  Intent Clarity: {context_summary['intent_clarity']:.2f}")

        # Show the adaptation reasoning
        if adapted_level != base_level:
            diff = adapted_level.value - base_level.value
            direction = "relaxed" if diff < 0 else "tightened"
            print(f"  → Enforcement {direction} by {abs(diff)} level(s)")


if __name__ == "__main__":
    test_adaptation_examples()
