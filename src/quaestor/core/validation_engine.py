"""Rule engine for generating contextual CLAUDE.md files based on project complexity."""

from pathlib import Path
from typing import Any

from .project_analysis import ProjectAnalyzer


class RuleEngine:
    """Generate appropriate CLAUDE.md content based on project analysis."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.analyzer = ProjectAnalyzer(project_dir)

    def generate_claude_md(self, mode: str = "personal") -> str:
        """Generate CLAUDE.md with appropriate rule strictness."""
        project_analysis = self.analyzer.analyze()

        if mode == "team" or project_analysis.get("team_markers"):
            return self._strict_rules(project_analysis)
        elif project_analysis.get("complexity_score", 0) > 0.7:
            return self._standard_rules(project_analysis)
        else:
            return self._minimal_rules(project_analysis)

    def _minimal_rules(self, analysis: dict[str, Any]) -> str:
        """For simple scripts/tools - just quality basics."""
        project_type = analysis.get("project_type", "unknown")

        return f"""# Project AI Assistant Configuration

This project uses Quaestor for AI context management.

## 🧠 THINKING PATTERNS

Before responding, I'll consider:

1. **Code Quality**:
   - Follow {project_type} idioms and best practices
   - Write clear, maintainable code
   - Add helpful comments for complex logic

2. **Testing**:
   - Write tests for new functionality
   - Ensure existing tests pass

3. **Documentation**:
   - Update docs when changing APIs
   - Keep README current

## Project Context
Check `.quaestor/ARCHITECTURE.md` and `.quaestor/MEMORY.md` for project details.

## Getting Started
This is a simple project. Focus on clean code and clear documentation.
"""

    def _standard_rules(self, analysis: dict[str, Any]) -> str:
        """For typical projects - progressive enforcement."""
        project_type = analysis.get("project_type", "unknown")
        has_tests = analysis.get("has_tests", False)

        return f"""# Project AI Assistant Configuration

This project uses Quaestor for AI context management.

## 🧠 THINKING PATTERNS

Before EVERY response, I'll consider:

1. **Complexity Check**:
   - Simple request? → Direct implementation
   - Multiple components? → "Let me research and plan this"
   - Unclear requirements? → "I need clarification on..."

2. **Quality Gates**:
   - About to write code? → Consider tests first
   - Touching existing code? → Research patterns first
   - Making claims? → Verify with checks

3. **Delegation Triggers**:
   ```
   if (files_to_modify > 3 || parallel_tasks_possible) {{
     say("I'll spawn agents to handle this efficiently")
   }}
   ```

## 🎯 PROGRESSIVE WORKFLOW

### For New Features:
1. **Research Phase** (when touching existing code):
   - "Let me understand the current implementation..."
   - Examine patterns, conventions, dependencies
   - Document findings

2. **Planning Phase** (for non-trivial changes):
   - "Here's my implementation plan..."
   - Break down into steps
   - Identify risks and edge cases

3. **Implementation**:
   - Follow the plan
   - Validate continuously
   - {self._get_quality_commands(project_type)}

### For Bug Fixes:
1. Reproduce and understand the issue
2. Research related code
3. Fix with minimal changes
4. Add regression tests

## Project Context
- **Type**: {project_type} project
- **Testing**: {"Enabled" if has_tests else "Add tests for new features"}
- **Architecture**: See `.quaestor/ARCHITECTURE.md`
- **Progress**: See `.quaestor/MEMORY.md`

## Quality Standards
{self._get_quality_standards(project_type)}

<!-- This runs OUTSIDE of /task commands -->
"""

    def _strict_rules(self, analysis: dict[str, Any]) -> str:
        """Full strict rules for team projects."""
        project_type = analysis.get("project_type", "unknown")

        return f"""# Project AI Assistant Configuration

This project uses Quaestor for AI context management in **TEAM MODE**.

## ⚠️ CRITICAL RULES - MANDATORY COMPLIANCE

## 🧠 THINKING PATTERNS

Before EVERY response, I MUST consider:

1. **Workflow Compliance**:
   - ANY implementation → "I need to research first"
   - Multiple files → "I'll spawn agents"
   - Uncertainty → "Let me clarify..."

2. **Mandatory Research Phase**:
   - Scan codebase for patterns
   - Identify dependencies
   - Document findings
   - NO SHORTCUTS

3. **Mandatory Planning Phase**:
   - Present detailed plan
   - Get approval before implementing
   - NO ASSUMPTIONS

4. **Quality Gates**:
   - Tests MUST pass
   - Linting MUST be clean
   - Documentation MUST be updated
   - NO EXCEPTIONS

## 🎯 IRON-CLAD WORKFLOW

### EVERY Task MUST Follow:

1. **RESEARCH** (Mandatory):
   ```
   "I'll research the codebase and create a plan before implementing."
   ```
   - Minimum 5 files examined
   - Patterns documented
   - Dependencies mapped

2. **PLAN** (Mandatory):
   ```
   "Here's my implementation plan: [DETAILED PLAN]"
   ```
   - Step-by-step approach
   - Risk assessment
   - User approval required

3. **IMPLEMENT** (With Validation):
   - Follow plan exactly
   - Validate every 3 edits
   - {self._get_quality_commands(project_type)}

## 🤖 MANDATORY AGENT USAGE

**MUST spawn agents for:**
- Multi-file analysis (3+ files)
- Complex refactoring
- Parallel implementation tasks
- Test writing while implementing

## 🚨 COMPLEXITY TRIGGERS

**STOP and ask when:**
- Function > 50 lines
- Nesting depth > 3
- Multiple valid approaches
- Performance implications unclear
- Security concerns possible

## Project Context
- **Type**: {project_type} team project
- **Critical Files**: See `.quaestor/CRITICAL_RULES.md`
- **Architecture**: See `.quaestor/ARCHITECTURE.md`
- **Progress**: See `.quaestor/MEMORY.md`

## Quality Standards
{self._get_quality_standards(project_type)}

## ENFORCEMENT
These rules are MANDATORY and IMMUTABLE. They cannot be overridden.
Validate compliance before EVERY action.

<!-- This runs BOTH inside and outside of /task commands -->
"""

    def _get_quality_commands(self, project_type: str) -> str:
        """Get quality check commands for project type."""
        commands = {
            "python": "Run `ruff check .` and `pytest`",
            "rust": "Run `cargo clippy` and `cargo test`",
            "javascript": "Run `npm run lint` and `npm test`",
            "typescript": "Run `npm run lint` and `npm test`",
        }
        return commands.get(project_type, "Run linting and tests")

    def _get_quality_standards(self, project_type: str) -> str:
        """Get quality standards for project type."""
        standards = {
            "python": """- Type hints for all functions
- Comprehensive docstrings
- Error handling with proper exceptions
- Test coverage > 80%
- Ruff-clean code""",
            "rust": """- Comprehensive documentation
- Proper error handling with Result
- No unwrap() in production code
- All Clippy warnings resolved
- Test coverage > 80%""",
            "javascript": """- ESLint-clean code
- Proper async/await usage
- Error boundaries where appropriate
- JSDoc for public APIs
- Test coverage > 80%""",
            "typescript": """- Strict TypeScript mode
- No `any` types without justification
- Comprehensive interfaces
- ESLint-clean code
- Test coverage > 80%""",
        }
        return standards.get(
            project_type,
            """- Clean, maintainable code
- Comprehensive error handling
- Clear documentation
- Adequate test coverage""",
        )
