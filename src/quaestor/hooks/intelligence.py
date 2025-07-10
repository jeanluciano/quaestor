"""Intelligence hooks for context management and learning.

These hooks provide smart context management, pattern learning, and
intelligent assistance to Claude.
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from . import HookResult, get_project_root

# Context management constants
CONTEXT_CACHE_FILE = ".quaestor/.context_cache"
PATTERNS_FILE = ".quaestor/.learned_patterns.json"
MAX_CONTEXT_AGE = timedelta(hours=1)


class ContextManager:
    """Manage Claude's context intelligently."""

    def __init__(self):
        self.root = get_project_root()
        self.cache_file = self.root / CONTEXT_CACHE_FILE
        self.patterns_file = self.root / PATTERNS_FILE
        self.context_cache = self._load_cache()
        self.learned_patterns = self._load_patterns()

    def _load_cache(self) -> dict[str, Any]:
        """Load context cache."""
        if not self.cache_file.exists():
            return {"last_refresh": None, "focus_areas": [], "relevant_files": []}

        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except Exception:
            return {"last_refresh": None, "focus_areas": [], "relevant_files": []}

    def _save_cache(self):
        """Save context cache."""
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.context_cache, f, indent=2)
        except Exception:
            pass

    def _load_patterns(self) -> dict[str, Any]:
        """Load learned patterns."""
        if not self.patterns_file.exists():
            return {"imports": defaultdict(int), "structures": defaultdict(int), "conventions": {}}

        try:
            with open(self.patterns_file) as f:
                data = json.load(f)
                # Convert back to defaultdict
                data["imports"] = defaultdict(int, data.get("imports", {}))
                data["structures"] = defaultdict(int, data.get("structures", {}))
                return data
        except Exception:
            return {"imports": defaultdict(int), "structures": defaultdict(int), "conventions": {}}

    def _save_patterns(self):
        """Save learned patterns."""
        try:
            # Convert defaultdict to regular dict for JSON
            patterns = {
                "imports": dict(self.learned_patterns["imports"]),
                "structures": dict(self.learned_patterns["structures"]),
                "conventions": self.learned_patterns.get("conventions", {}),
            }
            self.patterns_file.parent.mkdir(exist_ok=True)
            with open(self.patterns_file, "w") as f:
                json.dump(patterns, f, indent=2)
        except Exception:
            pass

    def needs_refresh(self) -> bool:
        """Check if context needs refreshing."""
        if not self.context_cache.get("last_refresh"):
            return True

        try:
            last_refresh = datetime.fromisoformat(self.context_cache["last_refresh"])
            return datetime.now() - last_refresh > MAX_CONTEXT_AGE
        except Exception:
            return True

    def get_relevant_files(self, focus: str | None = None) -> list[str]:
        """Get files relevant to current focus."""
        relevant = set()

        # Always include core files
        core_files = [
            "CLAUDE.md",
            ".quaestor/CRITICAL_RULES.md",
            ".quaestor/ARCHITECTURE.md",
            ".quaestor/MEMORY.md",
        ]

        for file in core_files:
            if (self.root / file).exists():
                relevant.add(file)

        # Add focus-specific files
        if focus:
            focus_lower = focus.lower()

            # Map focus areas to file patterns
            focus_patterns = {
                "test": ["**/test_*.py", "**/*_test.py", "**/tests/**"],
                "api": ["**/api/**", "**/routes/**", "**/endpoints/**"],
                "model": ["**/models/**", "**/entities/**", "**/domain/**"],
                "frontend": ["**/components/**", "**/pages/**", "**/*.tsx", "**/*.jsx"],
                "backend": ["**/services/**", "**/controllers/**", "**/handlers/**"],
                "config": ["**/config/**", "**/*.config.*", "**/settings/**"],
            }

            # Find matching patterns
            for area, patterns in focus_patterns.items():
                if area in focus_lower:
                    # Would need to implement glob matching here
                    # For now, just add the pattern as a hint
                    relevant.add(f"[Focus: {area} - check {', '.join(patterns)}]")

        # Add recently modified files
        recent_files = self._get_recently_modified_files()
        relevant.update(recent_files[:5])  # Top 5 recent files

        return list(relevant)

    def _get_recently_modified_files(self) -> list[str]:
        """Get recently modified files."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:", "-10"],
                capture_output=True,
                text=True,
                cwd=self.root,
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                # Remove duplicates while preserving order
                seen = set()
                unique_files = []
                for f in files:
                    if f not in seen and (self.root / f).exists():
                        seen.add(f)
                        unique_files.append(f)
                return unique_files[:10]
        except Exception:
            pass

        return []

    def refresh_context(self, focus: str | None = None) -> dict[str, Any]:
        """Refresh Claude's context based on current needs."""
        relevant_files = self.get_relevant_files(focus)

        # Update cache
        self.context_cache["last_refresh"] = datetime.now().isoformat()
        self.context_cache["focus_areas"] = [focus] if focus else []
        self.context_cache["relevant_files"] = relevant_files
        self._save_cache()

        # Generate context summary
        summary = self._generate_context_summary(relevant_files, focus)

        return {
            "relevant_files": relevant_files,
            "summary": summary,
            "patterns": self._get_common_patterns(),
        }

    def _generate_context_summary(self, files: list[str], focus: str | None) -> str:
        """Generate a context summary."""
        summary_parts = []

        # Current focus
        if focus:
            summary_parts.append(f"🎯 Current Focus: {focus}")

        # Project status from MEMORY.md
        memory_path = self.root / ".quaestor" / "MEMORY.md"
        if memory_path.exists():
            try:
                with open(memory_path) as f:
                    content = f.read()
                    # Extract current status
                    status_match = re.search(r"current_phase:\s*\"([^\"]+)\"", content)
                    if status_match:
                        summary_parts.append(f"📊 Current Phase: {status_match.group(1)}")
            except Exception:
                pass

        # Key files to review
        if files:
            summary_parts.append(f"📁 Key Files: {', '.join(files[:5])}")

        # Common patterns
        patterns = self._get_common_patterns()
        if patterns:
            summary_parts.append(f"🔧 Common Patterns: {', '.join(patterns[:3])}")

        return "\n".join(summary_parts)

    def _get_common_patterns(self) -> list[str]:
        """Get commonly used patterns in the project."""
        patterns = []

        # Most common imports
        if self.learned_patterns["imports"]:
            top_imports = sorted(self.learned_patterns["imports"].items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.extend([imp[0] for imp in top_imports])

        # Common structures
        if self.learned_patterns["structures"]:
            top_structures = sorted(self.learned_patterns["structures"].items(), key=lambda x: x[1], reverse=True)[:2]
            patterns.extend([struct[0] for struct in top_structures])

        return patterns

    def learn_from_code(self, file_path: str, content: str):
        """Learn patterns from code."""
        # Learn imports
        import_matches = re.findall(r"(?:from|import)\s+([\w.]+)", content)
        for imp in import_matches:
            self.learned_patterns["imports"][imp] += 1

        # Learn class structures
        class_matches = re.findall(r"class\s+(\w+)", content)
        for cls in class_matches:
            self.learned_patterns["structures"][f"class:{cls}"] += 1

        # Learn function patterns
        func_matches = re.findall(r"def\s+(\w+)", content)
        for func in func_matches:
            # Track naming conventions
            if func.startswith("test_"):
                self.learned_patterns["structures"]["test_function"] += 1
            elif func.startswith("_"):
                self.learned_patterns["structures"]["private_function"] += 1

        self._save_patterns()


def run_intelligence_hook(hook_name: str, context: dict[str, Any]) -> HookResult:
    """Run an intelligence hook."""
    if hook_name == "intel_refresh_context":
        return refresh_claude_context(context.get("focus"))
    elif hook_name == "intel_learn_patterns":
        return learn_from_current_work(context)
    elif hook_name == "intel_suggest_next":
        return suggest_next_action(context)
    elif hook_name == "intel_complexity_analysis":
        return analyze_complexity(context)
    else:
        return HookResult(False, f"Unknown intelligence hook: {hook_name}")


def refresh_claude_context(focus: str | None = None) -> HookResult:
    """Refresh Claude's context intelligently."""
    manager = ContextManager()

    if not manager.needs_refresh() and not focus:
        return HookResult(
            True,
            "Context is fresh (< 1 hour old). Use --focus to force refresh with specific focus area.",
        )

    context_data = manager.refresh_context(focus)

    # Build context message
    message_parts = ["🔄 Context refreshed!"]

    if context_data["summary"]:
        message_parts.append(f"\n{context_data['summary']}")

    message_parts.append("\n📚 Next steps:")
    message_parts.append("1. Re-read CLAUDE.md for latest instructions")
    message_parts.append("2. Check MEMORY.md for current progress")

    if focus:
        message_parts.append(f"3. Focus on {focus}-related files")

    return HookResult(True, "\n".join(message_parts), context_data)


def learn_from_current_work(context: dict[str, Any]) -> HookResult:
    """Learn patterns from current work."""
    manager = ContextManager()

    file_path = context.get("file_path")
    content = context.get("content", "")

    if not file_path or not content:
        return HookResult(False, "No file content to learn from")

    manager.learn_from_code(file_path, content)

    return HookResult(
        True,
        f"✅ Learned patterns from {file_path}",
        {"patterns_updated": True},
    )


def suggest_next_action(context: dict[str, Any]) -> HookResult:
    """Suggest next action based on current state."""
    root = get_project_root()
    suggestions = []

    # Check workflow state
    state_file = root / ".quaestor" / ".workflow_state"
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)

            if state.get("phase") == "idle":
                suggestions.append("🔍 Start with research: Use Grep/Read to explore the codebase")
            elif state.get("phase") == "planning":
                suggestions.append("📋 Create implementation plan: Present structured approach for approval")
            elif state.get("phase") == "implementing":
                suggestions.append("🏗️ Continue implementation: Follow the approved plan")
        except Exception:
            pass

    # Check for incomplete TODOs
    memory_path = root / ".quaestor" / "MEMORY.md"
    if memory_path.exists():
        try:
            with open(memory_path) as f:
                content = f.read()

            # Count incomplete items
            incomplete = len(re.findall(r"[-*]\s*\[\s*\]", content))
            if incomplete > 0:
                suggestions.append(f"📝 {incomplete} incomplete TODO items in current milestone")
        except Exception:
            pass

    # Check quality status
    try:
        import subprocess

        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=root)
        if result.returncode == 0 and result.stdout.strip():
            suggestions.append("💾 Uncommitted changes detected - consider committing completed work")
    except Exception:
        pass

    if not suggestions:
        suggestions.append("✅ All systems go! Ready for next task.")

    return HookResult(
        True,
        "🤖 Intelligent Suggestions:\n" + "\n".join(suggestions),
        {"suggestions": suggestions},
    )


def analyze_complexity(context: dict[str, Any]) -> HookResult:
    """Analyze code complexity and suggest improvements."""
    content = context.get("content", "")
    file_path = context.get("file_path", "unknown")

    if not content:
        return HookResult(False, "No content to analyze")

    complexity_issues = []

    # Check function length
    functions = re.findall(r"def\s+\w+.*?:\n((?:.*\n)*?)(?=\n(?:def|class|\Z))", content, re.MULTILINE)
    for i, func_body in enumerate(functions):
        lines = func_body.strip().split("\n")
        if len(lines) > 30:
            complexity_issues.append(f"Function {i + 1}: {len(lines)} lines (limit: 30)")

    # Check nesting depth
    max_indent = 0
    for line in content.split("\n"):
        if line.strip():
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent // 4)  # Assuming 4-space indent

    if max_indent > 3:
        complexity_issues.append(f"Max nesting depth: {max_indent} (limit: 3)")

    # Check class size
    classes = re.findall(r"class\s+\w+.*?:\n((?:.*\n)*?)(?=\nclass|\Z)", content, re.MULTILINE)
    for i, class_body in enumerate(classes):
        lines = class_body.strip().split("\n")
        if len(lines) > 200:
            complexity_issues.append(f"Class {i + 1}: {len(lines)} lines (limit: 200)")

    if complexity_issues:
        suggestions = [
            "Consider refactoring:",
            "- Extract helper functions",
            "- Use composition over deep nesting",
            "- Split large classes into smaller, focused ones",
        ]

        return HookResult(
            False,
            f"⚠️ Complexity Issues in {file_path}:\n" + "\n".join(complexity_issues) + "\n\n" + "\n".join(suggestions),
            {"issues": complexity_issues},
        )

    return HookResult(True, "✅ Code complexity within acceptable limits")
