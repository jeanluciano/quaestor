"""Subprocess-based skill executor for Claude CLI.

This module provides Level 2 integration - invoking Quaestor skills via
Claude Code CLI and capturing results asynchronously.
"""

import asyncio
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import SpecificationInput


@dataclass
class ExecutionResult:
    """Result from skill execution."""

    success: bool
    spec_id: str | None = None
    spec_path: Path | None = None
    output: str = ""
    error: str = ""
    duration_seconds: float = 0.0
    metadata: dict[str, Any] | None = None


class SkillExecutionError(Exception):
    """Raised when skill execution fails."""

    pass


class SkillExecutor:
    """Executes Quaestor skills via Claude CLI subprocess.

    Supports async execution with polling for completion.
    """

    def __init__(
        self,
        claude_command: str = "claude",
        timeout_seconds: int = 300,
        poll_interval_seconds: float = 2.0,
        project_dir: Path | None = None,
    ):
        """Initialize skill executor.

        Args:
            claude_command: Command to invoke Claude CLI (default: "claude")
            timeout_seconds: Maximum time to wait for skill completion
            poll_interval_seconds: How often to check for completion
            project_dir: Working directory for Claude (default: temp dir)
        """
        self.claude_command = claude_command
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.project_dir = project_dir or Path(tempfile.mkdtemp(prefix="quaestor-eval-"))

        # Ensure .quaestor structure exists
        self._init_project_structure()

    def _init_project_structure(self):
        """Initialize .quaestor directory structure in project."""
        specs_dir = self.project_dir / ".quaestor" / "specs"
        for folder in ["draft", "active", "completed", "archived"]:
            (specs_dir / folder).mkdir(parents=True, exist_ok=True)

    async def execute_plan_command(self, spec_input: SpecificationInput) -> ExecutionResult:
        """Execute /plan command to create a specification.

        Args:
            spec_input: Specification input with request and context

        Returns:
            ExecutionResult with spec_id and path if successful

        Raises:
            SkillExecutionError: If execution fails or times out
        """
        start_time = time.time()

        # Prepare input for Claude
        prompt = self._build_plan_prompt(spec_input)

        # Execute Claude CLI
        try:
            result = await self._execute_claude_async(prompt, command="/plan")
            duration = time.time() - start_time

            # Parse output to find spec ID
            spec_id = self._extract_spec_id(result.output)

            if spec_id:
                spec_path = self.project_dir / ".quaestor/specs/draft" / f"{spec_id}.md"
                return ExecutionResult(
                    success=True,
                    spec_id=spec_id,
                    spec_path=spec_path if spec_path.exists() else None,
                    output=result.output,
                    error=result.error,
                    duration_seconds=duration,
                    metadata={"request": spec_input.request},
                )
            else:
                return ExecutionResult(
                    success=False,
                    output=result.output,
                    error="Failed to extract spec ID from output",
                    duration_seconds=duration,
                )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_seconds=duration,
            )

    def _build_plan_prompt(self, spec_input: SpecificationInput) -> str:
        """Build prompt for /plan command.

        Args:
            spec_input: Specification input

        Returns:
            Formatted prompt string
        """
        prompt = f"/plan {spec_input.request}"

        if spec_input.context:
            prompt += f"\n\nContext: {spec_input.context}"

        if spec_input.priority:
            prompt += f"\nPriority: {spec_input.priority}"

        return prompt

    async def _execute_claude_async(
        self,
        prompt: str,
        command: str | None = None,
    ) -> ExecutionResult:
        """Execute Claude CLI command asynchronously with polling.

        Args:
            prompt: Input prompt/command for Claude
            command: Optional command prefix (e.g., "/plan")

        Returns:
            ExecutionResult with output and status
        """
        # Create input file for Claude
        input_file = self.project_dir / ".eval-input.txt"
        input_file.write_text(prompt)

        # Build Claude command
        cmd = [
            self.claude_command,
            "--project-dir",
            str(self.project_dir),
        ]

        # Note: Claude CLI may not support these flags - this is a prototype
        # You may need to adjust based on actual Claude CLI capabilities
        if command:
            cmd.extend(["--command", command])

        # Start Claude process
        start_time = time.time()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_dir,
        )

        # Send prompt
        stdout_data, stderr_data = await process.communicate(input=prompt.encode())

        # Wait for completion with timeout
        try:
            await asyncio.wait_for(process.wait(), timeout=self.timeout_seconds)
        except TimeoutError:
            process.kill()
            raise SkillExecutionError(f"Claude execution timed out after {self.timeout_seconds}s") from None

        duration = time.time() - start_time

        return ExecutionResult(
            success=process.returncode == 0,
            output=stdout_data.decode() if stdout_data else "",
            error=stderr_data.decode() if stderr_data else "",
            duration_seconds=duration,
        )

    def _extract_spec_id(self, output: str) -> str | None:
        """Extract specification ID from Claude output.

        Args:
            output: Claude CLI output text

        Returns:
            Spec ID if found, None otherwise
        """
        # Look for spec ID pattern: spec-YYYYMMDD-HHMMSS
        pattern = r"spec-\d{8}-\d{6}"
        matches = re.findall(pattern, output)

        if matches:
            # Return the last match (most recent)
            return matches[-1]

        return None

    async def wait_for_spec_file(
        self,
        spec_id: str,
        max_wait_seconds: float | None = None,
    ) -> Path | None:
        """Wait for specification file to appear in .quaestor/specs/draft/.

        Args:
            spec_id: Specification ID to wait for
            max_wait_seconds: Maximum time to wait (default: uses timeout_seconds)

        Returns:
            Path to spec file if found, None if timeout
        """
        max_wait = max_wait_seconds or self.timeout_seconds
        start_time = time.time()

        spec_path = self.project_dir / ".quaestor/specs/draft" / f"{spec_id}.md"

        while time.time() - start_time < max_wait:
            if spec_path.exists():
                # Wait a bit more to ensure file is fully written
                await asyncio.sleep(0.5)
                return spec_path

            await asyncio.sleep(self.poll_interval_seconds)

        return None

    def cleanup(self):
        """Clean up temporary project directory."""
        if self.project_dir and self.project_dir.exists():
            import contextlib
            import shutil

            with contextlib.suppress(Exception):
                shutil.rmtree(self.project_dir)


# Convenience function for synchronous use
def execute_plan_sync(
    spec_input: SpecificationInput,
    **kwargs,
) -> ExecutionResult:
    """Execute /plan command synchronously.

    Args:
        spec_input: Specification input
        **kwargs: Additional arguments for SkillExecutor

    Returns:
        ExecutionResult
    """
    executor = SkillExecutor(**kwargs)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(executor.execute_plan_command(spec_input))
        return result
    finally:
        executor.cleanup()
