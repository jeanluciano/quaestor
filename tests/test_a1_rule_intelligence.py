"""Tests for A1 Phase 3 Rule Intelligence features."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.a1.analytics import ExceptionTracker
from src.a1.enforcement import (
    AdaptiveComplexityRule,
    AdaptiveResearchRule,
    AdaptiveRuleEnforcer,
    EnforcementContext,
    EnforcementHistory,
    EnforcementLevel,
    OverrideSystem,
    RuleAdapter,
)
from src.a1.learning import PatternRecognizer
from src.quaestor.automation import HookResult


class TestGraduatedEnforcement:
    """Test graduated enforcement system."""

    def test_enforcement_levels(self):
        """Test enforcement level hierarchy."""
        assert EnforcementLevel.INFORM < EnforcementLevel.WARN
        assert EnforcementLevel.WARN < EnforcementLevel.JUSTIFY
        assert EnforcementLevel.JUSTIFY < EnforcementLevel.BLOCK

        assert EnforcementLevel.INFORM.allows_continuation
        assert EnforcementLevel.WARN.allows_continuation
        assert not EnforcementLevel.JUSTIFY.allows_continuation
        assert not EnforcementLevel.BLOCK.allows_continuation

    def test_adaptive_research_rule(self):
        """Test adaptive research enforcement."""
        rule = AdaptiveResearchRule()

        # Low-risk context should be lenient
        context = EnforcementContext(
            user_intent="explore code",
            workflow_phase="research",
            developer_experience=0.9,
            time_pressure=0.2,
            metadata={"files_examined": 1},
        )
        result = rule.enforce(context)
        assert result.allowed
        assert result.level == EnforcementLevel.INFORM

        # High-risk context should be strict
        context = EnforcementContext(
            user_intent="implement payment processing",
            workflow_phase="implementing",
            developer_experience=0.2,
            time_pressure=0.1,
            metadata={"files_examined": 0, "context_analysis": {"file_criticality": 0.9}},
        )
        result = rule.enforce(context)
        assert not result.allowed
        assert result.level == EnforcementLevel.JUSTIFY
        assert "5 files" in result.message  # High criticality requirement

    def test_adaptive_complexity_rule(self):
        """Test adaptive complexity limits."""
        rule = AdaptiveComplexityRule(base_max_lines=50)

        # Test file should allow higher complexity
        context = EnforcementContext(
            user_intent="add test",
            workflow_phase="implementing",
            tool_name="Write",
            file_path="/path/to/test_something.py",
            developer_experience=0.5,
            metadata={"content": "def test_function():\n" + "\n".join(["    pass"] * 60)},
        )
        result = rule.enforce(context)
        assert result.allowed  # 75 lines allowed for test files

        # Critical file should have lower limit
        context.file_path = "/path/to/auth.py"
        context.metadata["context_analysis"] = {"file_criticality": 0.9}
        result = rule.enforce(context)
        assert not result.allowed
        assert "40" in result.message  # Reduced limit for critical files


class TestContextAwareAdaptation:
    """Test context-aware rule adaptation."""

    def test_rule_adapter(self):
        """Test rule adaptation based on context."""
        adapter = RuleAdapter()

        # Research phase should reduce enforcement
        context = EnforcementContext(
            user_intent="explore patterns", workflow_phase="research", developer_experience=0.5
        )
        adapted = adapter.adapt_enforcement_level(EnforcementLevel.BLOCK, context)
        assert adapted == EnforcementLevel.WARN

        # Hotfix should reduce enforcement
        context.user_intent = "hotfix production issue"
        context.workflow_phase = "implementing"
        adapted = adapter.adapt_enforcement_level(EnforcementLevel.BLOCK, context)
        assert adapted == EnforcementLevel.WARN

        # Low experience should increase enforcement
        context = EnforcementContext(
            user_intent="implement feature", workflow_phase="implementing", developer_experience=0.1
        )
        adapted = adapter.adapt_enforcement_level(EnforcementLevel.WARN, context)
        assert adapted == EnforcementLevel.JUSTIFY

    def test_context_factor_analysis(self):
        """Test context factor analyzer."""
        from src.a1.enforcement.context_factors import ContextFactorAnalyzer

        analyzer = ContextFactorAnalyzer()

        # Test intent clarity
        clarity = analyzer.analyze_intent_clarity(
            "implement user authentication system", {"tool_name": "Write", "file_path": "/auth.py"}
        )
        assert clarity > 0.5  # Clear intent

        # Test time pressure
        pressure = analyzer.analyze_time_pressure({"user_intent": "urgent hotfix needed asap", "workflow_velocity": 15})
        assert pressure > 0.8  # High pressure

        # Test file criticality
        criticality = analyzer.analyze_file_criticality("/src/auth/security.py")
        assert criticality > 0.8  # High criticality

    def test_enforcement_history_influence(self):
        """Test how history influences enforcement."""
        history = EnforcementHistory()
        rule = AdaptiveRuleEnforcer(
            rule_id="test_rule", rule_name="Test Rule", base_level=EnforcementLevel.JUSTIFY, history=history
        )

        # Mock check_rule to always fail
        rule.check_rule = lambda ctx: (False, "Test violation")
        rule.get_suggestions = lambda ctx: []

        context = EnforcementContext(user_intent="test action", workflow_phase="implementing")

        # First violation
        result1 = rule.enforce(context)
        assert result1.level == EnforcementLevel.JUSTIFY

        # Record override
        rule.record_override(context, "Testing override")

        # Same context should now be more lenient
        result2 = rule.enforce(context)
        assert result2.level == EnforcementLevel.INFORM  # Reduced due to recent override


class TestRuleLearningSystem:
    """Test rule learning and pattern recognition."""

    def test_pattern_recognition(self):
        """Test pattern recognizer identifies patterns."""
        recognizer = PatternRecognizer()

        # Add similar exceptions
        for i in range(5):
            exception = {
                "rule_id": "research_rule",
                "user_intent": "quick fix",
                "workflow_phase": "implementing",
                "file_path": f"/src/utils/helper{i}.py",
                "developer_experience": 0.9,
                "override_reason": "Simple utility change",
            }
            recognizer.add_exception(exception)

        # Should recognize pattern
        patterns = recognizer.get_patterns_for_rule("research_rule")
        assert len(patterns) > 0

        pattern = patterns[0]
        assert pattern["pattern_criteria"]["user_intent"] == "quick fix"
        assert pattern["pattern_criteria"]["workflow_phase"] == "implementing"
        assert pattern["confidence"] > 0.5

    def test_pattern_learning_integration(self):
        """Test integration of learned patterns with enforcement."""
        from src.a1.hooks import IntelligentHook
        from src.a1.learning import LearningSystem

        # Setup learning system
        learning_system = LearningSystem()

        # Create intelligent hook
        class TestIntelligentHook(IntelligentHook):
            def check_conditions(self, input_data, workflow_state):
                # Simulate rule check
                context = self.build_context(input_data, workflow_state, Path("."))
                if context.user_intent == "routine update":
                    return HookResult(allow=False, message="Test rule violated", suggestions=["Do more research"])
                return HookResult(allow=True)

        hook = TestIntelligentHook(hook_id="test_hook", name="Test Hook", learning_system=learning_system)

        # Simulate multiple overrides for same pattern
        for i in range(5):
            input_data = {"toolName": "Write", "filePath": f"/src/routine{i}.py", "args": ["routine update"]}
            workflow_state = MagicMock()
            workflow_state.state = {"phase": "implementing"}

            # First check should fail
            result = hook.run(input_data, workflow_state)
            assert not result.allow

            # Override with justification
            hook.record_override(input_data, workflow_state, "Routine updates don't need extensive research")

        # Now similar actions should be allowed
        new_input = {"toolName": "Write", "filePath": "/src/routine_new.py", "args": ["routine update"]}
        result = hook.run(new_input, workflow_state)
        # Should be more lenient due to learned pattern
        assert result.allow or result.message.startswith("ℹ️")  # INFORM level

    def test_confidence_scoring(self):
        """Test confidence scoring for patterns."""
        from src.a1.learning import ConfidenceScorer

        scorer = ConfidenceScorer()

        # High confidence pattern
        pattern_data = {
            "frequency": 20,
            "last_seen": time.time() - 3600,  # 1 hour ago
            "applications": [
                {"successful": True, "timestamp": time.time() - 7200},
                {"successful": True, "timestamp": time.time() - 3600},
                {"successful": True, "timestamp": time.time() - 1800},
            ],
            "pattern_criteria": {"user_intent": "refactor", "workflow_phase": "implementing"},
        }

        context = {"user_intent": "refactor", "workflow_phase": "implementing"}
        confidence = scorer.score_pattern(pattern_data, context)
        assert confidence > 0.7  # High confidence

        # Low confidence pattern
        pattern_data["frequency"] = 2
        pattern_data["last_seen"] = time.time() - 86400 * 30  # 30 days ago
        confidence = scorer.score_pattern(pattern_data, context)
        assert confidence < 0.5  # Low confidence


class TestExceptionTracking:
    """Test exception tracking and analytics."""

    def test_exception_tracker(self):
        """Test exception tracking functionality."""
        tracker = ExceptionTracker()

        # Track some events
        events = [
            {
                "rule_id": "complexity_rule",
                "level": "BLOCK",
                "context": {
                    "user_intent": "add feature",
                    "workflow_phase": "implementing",
                    "file_path": "/src/feature.py",
                },
                "override": True,
                "reason": "Feature requires complex logic",
            },
            {
                "rule_id": "research_rule",
                "level": "JUSTIFY",
                "context": {"user_intent": "fix bug", "workflow_phase": "implementing", "file_path": "/src/bugfix.py"},
                "override": False,
            },
        ]

        for event in events:
            tracker.track_event(event)

        # Get summary
        summary = tracker.get_summary(hours=24)
        assert summary["total_events"] == 2
        assert summary["override_rate"] == 0.5
        assert "complexity_rule" in summary["by_rule"]
        assert summary["by_rule"]["complexity_rule"]["override_rate"] == 1.0

    def test_pattern_detection(self):
        """Test pattern detection in exceptions."""
        tracker = ExceptionTracker()

        # Add multiple similar overrides
        for _i in range(5):
            event = {
                "rule_id": "test_rule",
                "level": "BLOCK",
                "context": {"user_intent": "quick fix", "workflow_phase": "hotfix", "developer_experience": 0.9},
                "override": True,
                "reason": "Emergency fix",
            }
            tracker.track_event(event)

        patterns = tracker.detect_patterns("test_rule")
        assert len(patterns) > 0
        assert patterns[0]["count"] == 5
        assert "quick fix" in str(patterns[0]["common_context"])

    def test_exception_clustering(self):
        """Test exception clustering."""
        from src.a1.learning import ExceptionClusterer

        clusterer = ExceptionClusterer()

        # Add diverse exceptions
        exceptions = [
            # Cluster 1: Quick fixes
            {"user_intent": "quick fix", "workflow_phase": "hotfix", "file_path": "/src/a.py"},
            {"user_intent": "quick fix", "workflow_phase": "hotfix", "file_path": "/src/b.py"},
            {"user_intent": "quick patch", "workflow_phase": "hotfix", "file_path": "/src/c.py"},
            # Cluster 2: Test updates
            {"user_intent": "update test", "workflow_phase": "testing", "file_path": "/test/a.py"},
            {"user_intent": "fix test", "workflow_phase": "testing", "file_path": "/test/b.py"},
        ]

        for exc in exceptions:
            clusterer.add_exception(exc)

        clusters = clusterer.get_clusters()
        assert len(clusters) >= 2  # Should identify at least 2 patterns

        # Check cluster quality
        for cluster in clusters:
            assert cluster["member_count"] >= 2
            assert "pattern" in cluster


class TestIntegration:
    """Test integration with Quaestor hook system."""

    def test_hook_result_mapping(self):
        """Test mapping between A1 enforcement and Quaestor HookResult."""
        from src.a1.hooks import map_enforcement_to_hook_result

        # INFORM/WARN should allow
        result = map_enforcement_to_hook_result(EnforcementLevel.INFORM, "Info message", ["suggestion1"])
        assert result.allow
        assert result.message == "Info message"

        # JUSTIFY/BLOCK should not allow
        result = map_enforcement_to_hook_result(EnforcementLevel.BLOCK, "Blocked message", ["fix1", "fix2"])
        assert not result.allow
        assert "fix1" in result.suggestions

    def test_override_system(self):
        """Test override system functionality."""
        override_system = OverrideSystem()

        # Add override
        override_system.add_override(
            rule_id="test_rule",
            context={"user_intent": "test", "workflow_phase": "implementing"},
            justification="Testing override",
            duration_hours=2,
        )

        # Check if override is active
        assert override_system.has_active_override(
            "test_rule", {"user_intent": "test", "workflow_phase": "implementing"}
        )

        # Different context should not match
        assert not override_system.has_active_override(
            "test_rule", {"user_intent": "other", "workflow_phase": "implementing"}
        )

        # Test expiration
        with patch("time.time", return_value=time.time() + 7300):  # 2+ hours later
            assert not override_system.has_active_override(
                "test_rule", {"user_intent": "test", "workflow_phase": "implementing"}
            )


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_workflow(self):
        """Test complete workflow with all components."""
        from src.a1.hooks import IntelligentResearchHook
        from src.a1.learning import LearningSystem

        # Setup components
        learning_system = LearningSystem()
        hook = IntelligentResearchHook(learning_system=learning_system)

        # Simulate workflow
        input_data = {"toolName": "Write", "filePath": "/src/critical/auth.py", "args": ["implement OAuth"]}

        workflow_state = MagicMock()
        workflow_state.state = {
            "phase": "implementing",
            "research_files": [],  # No research done
        }

        # First attempt should fail
        result = hook.run(input_data, workflow_state)
        assert not result.allow
        assert "research" in result.message.lower()

        # Do some research
        workflow_state.state["research_files"] = [
            "/src/auth/base.py",
            "/src/auth/oauth_provider.py",
            "/tests/test_auth.py",
        ]

        # Should now pass
        result = hook.run(input_data, workflow_state)
        assert result.allow

    def test_adaptive_behavior_over_time(self):
        """Test how system adapts over time."""
        from src.a1.enforcement import AdaptiveRuleEnforcer, EnforcementHistory
        from src.a1.learning import LearningSystem

        history = EnforcementHistory()
        learning = LearningSystem()

        class TestRule(AdaptiveRuleEnforcer):
            def check_rule(self, context):
                # Fail for "risky" actions
                if "risky" in context.user_intent:
                    return False, "Risky action detected"
                return True, "Safe action"

            def get_suggestions(self, context):
                return ["Be more careful", "Review the code"]

        rule = TestRule(
            rule_id="safety_rule", rule_name="Safety Check", base_level=EnforcementLevel.BLOCK, history=history
        )

        # Simulate experienced developer repeatedly overriding
        context = EnforcementContext(
            user_intent="risky refactor", workflow_phase="implementing", developer_experience=0.9
        )

        # First few times should be strict
        for i in range(3):
            result = rule.enforce(context)
            assert result.level >= EnforcementLevel.WARN

            # Override with good reason
            rule.record_override(context, f"Safe refactor pattern #{i + 1}")
            learning.record_exception("safety_rule", context, f"Safe refactor pattern #{i + 1}")

        # After pattern recognition, should be more lenient
        time.sleep(0.1)  # Ensure different timestamps
        result = rule.enforce(context)
        # Should adapt based on history and experience
        assert result.level <= EnforcementLevel.WARN
