"""A1 Rule Intelligence - Enforcement Module.

Provides graduated enforcement system with context-aware rule adaptation.
"""

from .adaptive_enforcer import AdaptiveComplexityRule, AdaptiveResearchRule, AdaptiveRuleEnforcer
from .context_factors import ContextFactorAnalyzer
from .enforcement_history import EnforcementEvent, EnforcementHistory
from .enforcement_levels import EnforcementConfig, EnforcementLevel
from .override_system import Override, OverrideSystem
from .rule_adapter import AdaptationFactors, AdaptationStrategy, RuleAdapter
from .rule_enforcer import EnforcementContext, EnforcementResult, RuleEnforcer
from .rules import ComplexityLimitRule, DocumentationRule, ResearchBeforeImplementationRule, TestCoverageRule

__all__ = [
    # Levels and Configuration
    "EnforcementLevel",
    "EnforcementConfig",
    # Core Enforcement
    "RuleEnforcer",
    "EnforcementResult",
    "EnforcementContext",
    "EnforcementHistory",
    "EnforcementEvent",
    # Override System
    "OverrideSystem",
    "Override",
    # Adaptation System
    "RuleAdapter",
    "AdaptationStrategy",
    "AdaptationFactors",
    "ContextFactorAnalyzer",
    # Adaptive Enforcers
    "AdaptiveRuleEnforcer",
    "AdaptiveResearchRule",
    "AdaptiveComplexityRule",
    # Concrete Rules
    "ResearchBeforeImplementationRule",
    "ComplexityLimitRule",
    "TestCoverageRule",
    "DocumentationRule",
]
