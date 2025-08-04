#!/usr/bin/env python3
"""Specification progress tracking and validation hook.

This hook monitors specification progress and ensures work is properly
tracked in specifications.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root


class SpecTrackerHook(BaseHook):
    """Specification tracking hook."""

    def __init__(self):
        super().__init__("spec_tracker")
        self.project_root = get_project_root()

    def execute(self):
        """Execute specification tracking."""
        # Check specification status
        spec_status = self.check_spec_progress()

        # Check for recent work
        work_done = self.get_recent_work()

        # Check for specification updates
        spec_updates = self.check_spec_updates() if work_done else {"spec_files": []}

        # Validate tracking
        issues = self.validate_tracking(work_done, spec_updates) if work_done else []

        # Check for completed specs in active folder
        completed_active_specs = self._check_for_completed_active_specs()
        if completed_active_specs:
            spec_names = ", ".join([s.stem for s in completed_active_specs])
            message = f"""✅ Completed specifications detected in active folder!

Specs ready for archiving: {spec_names}

These specifications appear to be complete. To archive them:
Run: /review --archive-spec {completed_active_specs[0].stem}

This will move them to the completed/ folder and free up active slots."""
            self.output_suggestion(message)
            return

        # Generate suggestions based on issues
        if issues:
            high_severity = [i for i in issues if i["severity"] == "high"]
            if high_severity:
                # Show the first high severity issue
                issue = high_severity[0]
                message = f"⚠️ {issue['message']}\n→ {issue['fix']}"
                self.output_success(message)
            else:
                # Show medium severity issues as hints
                issue = issues[0]
                message = f"💡 {issue['message']}"
                self.output_success(message)
        else:
            # Provide status update if no issues
            if spec_status.get("status") == "active":
                progress = spec_status.get("progress", 0)
                total = spec_status.get("total_specs", 0)
                completed = spec_status.get("completed_specs", 0)
                status_msg = f"📊 Specifications: {completed}/{total} complete ({progress}%)"
                self.output_success(status_msg)
            else:
                self.output_success("Specification tracking up to date")

    def check_spec_progress(self) -> dict[str, Any]:
        """Check specification progress."""
        try:
            from quaestor.core.specifications import SpecificationManager, SpecStatus

            manager = SpecificationManager(self.project_root)
            all_specs = manager.list_specifications()

            if not all_specs:
                return {"status": "no_specs", "message": "No specifications found"}

            # Count specs by status
            status_counts = {}
            for status in SpecStatus:
                status_counts[status.value] = sum(1 for s in all_specs if s.status == status)

            completed = sum(1 for s in all_specs if s.status == SpecStatus.COMPLETED)

            progress = int((completed / len(all_specs)) * 100) if all_specs else 0

            return {
                "status": "active",
                "total_specs": len(all_specs),
                "completed_specs": completed,
                "progress": progress,
                "status_counts": status_counts,
                "complete": progress >= 100,
            }

        except ImportError:
            return {"status": "no_spec_system", "message": "Specification system not available"}
        except Exception as e:
            return {"status": "error", "message": f"Error checking specs: {e}"}

    def _check_for_completed_active_specs(self) -> list[Path]:
        """Check for completed specifications in the active folder."""
        active_dir = self.project_root / ".quaestor" / "specs" / "active"
        completed_specs = []
        
        if not active_dir.exists():
            return completed_specs
            
        for spec_file in active_dir.glob("*.yaml"):
            try:
                with open(spec_file) as f:
                    content = f.read()
                    
                # Check for explicit completion status
                has_completed_status = "status: completed" in content or "status: 'completed'" in content
                
                # Only consider it complete if explicitly marked as completed
                if has_completed_status:
                    completed_specs.append(spec_file)
                    continue
                    
                # Additional check: if status is 'implemented' and has high completion
                has_implemented_status = "status: implemented" in content or "status: 'implemented'" in content
                
                if has_implemented_status:
                    # Check for task completion markers
                    has_all_done = "- [x]" in content and "- [ ]" not in content
                    
                    # Check acceptance criteria completion
                    import yaml
                    try:
                        spec_data = yaml.safe_load(content)
                        acceptance_criteria = spec_data.get("acceptance_criteria", [])
                        test_scenarios = spec_data.get("test_scenarios", [])
                        
                        # If we have acceptance criteria or test scenarios, check if they're marked complete
                        if acceptance_criteria or test_scenarios:
                            # Look for completion indicators in the content
                            if "✓" in content or "✅" in content or has_all_done:
                                completed_specs.append(spec_file)
                    except:
                        pass
                        
            except Exception:
                continue
                
        return completed_specs

    def get_recent_work(self, hours: int = 6) -> dict[str, Any] | None:
        """Detect recent implementation work."""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=hours)

        work_detected = {
            "src_files": [],
            "test_files": [],
            "config_files": [],
            "doc_files": [],
            "timestamp": now.isoformat(),
        }

        # Define patterns to check
        patterns = {
            "src": ["src/**/*.py", "src/**/*.js", "src/**/*.ts", "src/**/*.go", "src/**/*.rs"],
            "test": ["tests/**/*.py", "test/**/*.js", "**/*_test.go", "**/*.test.ts"],
            "config": ["*.json", "*.yaml", "*.yml", "*.toml"],
            "docs": ["**/*.md", "docs/**/*"],
        }

        # Check for recent files
        for category, file_patterns in patterns.items():
            for pattern in file_patterns:
                for f in self.project_root.glob(pattern):
                    # Skip .quaestor directory
                    if ".quaestor" in str(f):
                        continue

                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime > recent_cutoff:
                            relative_path = str(f.relative_to(self.project_root))

                            if category == "src":
                                work_detected["src_files"].append(relative_path)
                            elif category == "test":
                                work_detected["test_files"].append(relative_path)
                            elif category == "config":
                                work_detected["config_files"].append(relative_path)
                            elif category == "docs":
                                work_detected["doc_files"].append(relative_path)
                    except OSError:
                        continue

        # Check if any work was detected
        has_work = any(
            [
                work_detected["src_files"],
                work_detected["test_files"],
                work_detected["config_files"],
                work_detected["doc_files"],
            ]
        )

        return work_detected if has_work else None

    def check_spec_updates(self, hours: int = 6) -> dict[str, Any]:
        """Check for recent specification updates."""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=hours)

        specs_dir = self.project_root / ".quaestor" / "specs"

        updates = {"spec_files": [], "timestamp": now.isoformat()}

        # Check specification files in all folders (draft, active, completed)
        if specs_dir.exists():
            for folder in ["draft", "active", "completed"]:
                folder_path = specs_dir / folder
                if folder_path.exists():
                    for f in folder_path.glob("*.yaml"):
                        try:
                            mtime = datetime.fromtimestamp(f.stat().st_mtime)
                            if mtime > recent_cutoff:
                                updates["spec_files"].append(str(f.relative_to(self.project_root)))
                        except OSError:
                            continue

        return updates

    def validate_tracking(self, work_done: dict[str, Any], spec_updates: dict[str, Any]) -> list[dict[str, Any]]:
        """Validate that tracking matches work done."""
        issues = []

        # Determine work type
        has_implementation = bool(work_done["src_files"])
        has_tests = bool(work_done["test_files"])

        # Check spec updates for implementation work
        if has_implementation and not spec_updates["spec_files"]:
            issues.append(
                {
                    "type": "missing_spec_update",
                    "severity": "high",
                    "message": f"Implementation work detected ({len(work_done['src_files'])} files) - no spec update",
                    "fix": "Update relevant specifications with progress or status changes",
                }
            )

        # Check for active specifications
        if has_implementation:
            active_specs = list((self.project_root / ".quaestor" / "specs" / "active").glob("*.yaml"))
            if not active_specs:
                issues.append(
                    {
                        "type": "no_active_spec",
                        "severity": "high",
                        "message": "Implementation work detected but no active specifications",
                        "fix": "Move a specification to active/ folder or create a new spec",
                    }
                )

        return issues


def main():
    """Main hook entry point."""
    hook = SpecTrackerHook()
    hook.run()


if __name__ == "__main__":
    main()
