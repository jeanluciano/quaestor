"""Adaptive rule enforcer that uses context-aware adaptation."""

from .context_factors import ContextFactorAnalyzer
from .enforcement_history import EnforcementHistory
from .enforcement_levels import EnforcementLevel
from .rule_adapter import AdaptationFactors, RuleAdapter
from .rule_enforcer import EnforcementContext, EnforcementResult, RuleEnforcer


class AdaptiveRuleEnforcer(RuleEnforcer):
    """Rule enforcer with adaptive capabilities based on context."""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        base_level: EnforcementLevel = EnforcementLevel.WARN,
        history: EnforcementHistory | None = None,
        adaptation_factors: AdaptationFactors | None = None,
    ):
        super().__init__(rule_id, rule_name, base_level, history)
        self.adapter = RuleAdapter(adaptation_factors)
        self.factor_analyzer = ContextFactorAnalyzer()

    def enforce(self, context: EnforcementContext) -> EnforcementResult:
        """Enforce with adaptive level based on context."""
        # Enrich context with additional analysis
        self._enrich_context(context)

        # Use parent class logic but with our enhanced level determination
        return super().enforce(context)

    def _determine_enforcement_level(self, context: EnforcementContext) -> EnforcementLevel:
        """Determine enforcement level using advanced adaptation."""
        # Get base adaptation from parent
        base_adapted_level = super()._determine_enforcement_level(context)

        # Apply rule adapter for more sophisticated adaptation
        adapted_level = self.adapter.adapt_enforcement_level(base_adapted_level, context)

        # Log adaptation decision
        if adapted_level != self.base_level:
            self.logger.info(
                f"Rule {self.rule_id}: Adapted from {self.base_level.name} to {adapted_level.name} "
                f"based on context (intent: {context.user_intent}, phase: {context.workflow_phase})"
            )

        return adapted_level

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get context-adapted suggestions."""
        # Get base suggestions from subclass
        base_suggestions = super().get_suggestions(context)

        # Adapt suggestions based on context
        return self.adapter.get_adapted_suggestions(base_suggestions, context)

    def _enrich_context(self, context: EnforcementContext) -> None:
        """Enrich context with additional analysis."""
        # Analyze context factors
        context_summary = self.factor_analyzer.get_context_summary(context.metadata)

        # Add analysis results to metadata
        context.metadata["context_analysis"] = context_summary

        # Calculate adaptation confidence
        confidence = self.adapter.calculate_confidence_score(context)
        context.metadata["adaptation_confidence"] = confidence

        # Determine if shortcuts allowed
        context.metadata["shortcuts_allowed"] = self.adapter.should_allow_shortcut(context)


class AdaptiveResearchRule(AdaptiveRuleEnforcer):
    """Research enforcement with adaptive behavior."""

    def __init__(self, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="adaptive_research",
            rule_name="Adaptive Research Enforcement",
            base_level=EnforcementLevel.JUSTIFY,
            history=history,
        )

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check research with context awareness."""
        if context.workflow_phase != "implementing":
            return True, "Not in implementation phase"

        files_examined = context.metadata.get("files_examined", 0)

        # Adapt requirement based on context
        required_files = 3  # Default

        # Reduce requirement for simple tasks
        if context.metadata.get("context_analysis", {}).get("intent_clarity", 0) > 0.8:
            required_files = 2

        # Reduce for experienced developers
        if context.developer_experience > 0.8:
            required_files = 2

        # Increase for critical files
        if context.metadata.get("context_analysis", {}).get("file_criticality", 0) > 0.8:
            required_files = 5

        # Allow shortcuts in certain contexts
        if context.metadata.get("shortcuts_allowed", False):
            required_files = 1

        if files_examined < required_files:
            msg = f"Only {files_examined} files examined. Need at least {required_files} files for this context."
            return False, msg

        return True, "Sufficient research completed"

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get adaptive suggestions."""
        base = ["Use Grep to search for patterns", "Read implementation files", "Check tests for examples"]

        # Add context-specific suggestions
        risk_score = context.metadata.get("context_analysis", {}).get("risk_score", 0.5)
        if risk_score > 0.7:
            base.insert(0, "⚠️ High-risk change detected - thorough research critical")

        return base


class AdaptiveComplexityRule(AdaptiveRuleEnforcer):
    """Complexity enforcement with adaptive thresholds."""

    def __init__(self, base_max_lines: int = 50, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="adaptive_complexity",
            rule_name="Adaptive Complexity Limits",
            base_level=EnforcementLevel.WARN,
            history=history,
        )
        self.base_max_lines = base_max_lines

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check complexity with adaptive limits."""
        if context.tool_name not in ["Write", "Edit", "MultiEdit"]:
            return True, "Not a code modification"

        # Adapt limit based on context
        max_lines = self.base_max_lines

        # Increase limit for test files
        if "test" in (context.file_path or "").lower():
            max_lines = int(max_lines * 1.5)

        # Increase for experienced developers
        if context.developer_experience > 0.8:
            max_lines = int(max_lines * 1.2)

        # Decrease for critical files
        criticality = context.metadata.get("context_analysis", {}).get("file_criticality", 0.5)
        if criticality > 0.8:
            max_lines = int(max_lines * 0.8)

        # Check actual complexity
        content = context.metadata.get("content", "")
        lines = content.split("\n")

        violations = []
        in_function = False
        function_lines = 0
        function_name = ""

        for line in lines:
            if line.strip().startswith(("def ", "async def ")):
                if in_function and function_lines > max_lines:
                    violations.append((function_name, function_lines))
                in_function = True
                function_lines = 0
                function_name = line.strip().split("(")[0].replace("def ", "").replace("async ", "")
            elif in_function:
                function_lines += 1

        # Check last function
        if in_function and function_lines > max_lines:
            violations.append((function_name, function_lines))

        if violations:
            worst = max(violations, key=lambda x: x[1])
            return False, f"Function '{worst[0]}' has {worst[1]} lines (adaptive limit: {max_lines})"

        return True, "Complexity within adaptive limits"
