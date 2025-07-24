"""Sequence mining algorithms for pattern extraction.

This module implements algorithms to discover frequent sequences and patterns
from event streams, including PrefixSpan and sequential pattern mining.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from a1.core.events import Event

from .patterns import CommandPattern, FilePattern, Pattern, WorkflowPattern


@dataclass
class Sequence:
    """Represents a sequence of events."""

    events: list[Event]
    support: int = 1
    confidence: float = 0.0


@dataclass
class SequenceDatabase:
    """Database of sequences for mining."""

    sequences: list[Sequence] = field(default_factory=list)
    min_support: int = 2
    max_gap: float = 300.0  # Max seconds between events in a sequence


class SequenceMiner:
    """Mines sequential patterns from event streams."""

    def __init__(self, min_support: int = 2, max_gap: float = 300.0):
        """Initialize sequence miner.

        Args:
            min_support: Minimum occurrences for a pattern
            max_gap: Maximum time gap (seconds) between sequential events
        """
        self.min_support = min_support
        self.max_gap = max_gap
        self.sequence_db = SequenceDatabase(min_support=min_support, max_gap=max_gap)
        self.pattern_cache: dict[str, Any] = {}

    def add_event(self, event: Event) -> None:
        """Add a new event to the sequence database."""
        # Find sequences this event could extend
        extended = False
        current_time = time.time()

        for sequence in self.sequence_db.sequences:
            last_event = sequence.events[-1]
            time_diff = current_time - getattr(last_event, "timestamp", current_time)

            if time_diff <= self.max_gap:
                # Event is within time window, could extend sequence
                if self._can_extend_sequence(sequence, event):
                    new_sequence = Sequence(events=sequence.events + [event], support=1)
                    self.sequence_db.sequences.append(new_sequence)
                    extended = True

        if not extended:
            # Start new sequence
            self.sequence_db.sequences.append(Sequence(events=[event]))

        # Prune old sequences
        self._prune_sequences(current_time)

    def mine_patterns(self) -> list[Pattern]:
        """Mine patterns from the sequence database."""
        patterns = []

        # Mine command sequences
        command_patterns = self._mine_command_patterns()
        patterns.extend(command_patterns)

        # Mine file access patterns
        file_patterns = self._mine_file_patterns()
        patterns.extend(file_patterns)

        # Mine workflow patterns
        workflow_patterns = self._mine_workflow_patterns()
        patterns.extend(workflow_patterns)

        return patterns

    def _mine_command_patterns(self) -> list[CommandPattern]:
        """Extract command sequence patterns."""
        # Group sequences by command types
        command_sequences = defaultdict(list)

        for sequence in self.sequence_db.sequences:
            commands = []
            for event in sequence.events:
                if hasattr(event, "tool") or hasattr(event, "command"):
                    cmd = getattr(event, "tool", getattr(event, "command", None))
                    if cmd:
                        commands.append(cmd)

            if len(commands) >= 2:
                # Create command sequence key
                seq_key = "->".join(commands)
                command_sequences[seq_key].append(sequence)

        # Create patterns from frequent sequences
        patterns = []
        for seq_key, sequences in command_sequences.items():
            if len(sequences) >= self.min_support:
                commands = seq_key.split("->")
                pattern = CommandPattern(
                    id=f"cmd_seq_{hash(seq_key)}",
                    command_sequence=commands,
                    frequency=len(sequences),
                    confidence=min(0.5 + len(sequences) * 0.1, 0.95),
                    first_seen=min(s.events[0].timestamp for s in sequences if hasattr(s.events[0], "timestamp")),
                    last_seen=max(s.events[-1].timestamp for s in sequences if hasattr(s.events[-1], "timestamp")),
                )

                # Extract common parameters
                param_counts = defaultdict(lambda: defaultdict(int))
                for sequence in sequences:
                    for event in sequence.events:
                        if hasattr(event, "parameters"):
                            for param, value in event.parameters.items():
                                param_counts[param][str(value)] += 1

                # Keep most common parameter values
                for param, values in param_counts.items():
                    sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
                    pattern.common_parameters[param] = [v[0] for v in sorted_values[:3]]

                patterns.append(pattern)

        return patterns

    def _mine_file_patterns(self) -> list[FilePattern]:
        """Extract file access patterns."""
        file_sequences = defaultdict(list)
        file_correlations = defaultdict(lambda: defaultdict(int))

        for sequence in self.sequence_db.sequences:
            files = []
            for event in sequence.events:
                if hasattr(event, "file_path"):
                    files.append(event.file_path)

            if len(files) >= 2:
                # Track file sequences
                seq_key = "->".join(files[-5:])  # Last 5 files
                file_sequences[seq_key].append(sequence)

                # Track file correlations
                for i in range(len(files) - 1):
                    file_correlations[files[i]][files[i + 1]] += 1

        # Create patterns
        patterns = []

        # File sequence patterns
        for seq_key, sequences in file_sequences.items():
            if len(sequences) >= self.min_support:
                files = seq_key.split("->")
                pattern = FilePattern(
                    id=f"file_seq_{hash(seq_key)}",
                    file_sequence=files,
                    frequency=len(sequences),
                    confidence=min(0.5 + len(sequences) * 0.1, 0.95),
                )

                # Add correlated files
                for file in files:
                    if file in file_correlations:
                        correlations = file_correlations[file]
                        total = sum(correlations.values())
                        for related, count in correlations.items():
                            if related != file:
                                pattern.related_files[related] = count / total

                patterns.append(pattern)

        # File group patterns (files often accessed together)
        file_groups = self._find_file_groups(file_correlations)
        for group in file_groups:
            if len(group) >= 2:
                pattern = FilePattern(
                    id=f"file_group_{hash(tuple(sorted(group)))}",
                    file_groups=[list(group)],
                    frequency=len(group),
                    confidence=0.7,
                )
                patterns.append(pattern)

        return patterns

    def _mine_workflow_patterns(self) -> list[WorkflowPattern]:
        """Extract workflow patterns from longer sequences."""
        # Group sequences by similar starts/ends
        workflow_candidates = defaultdict(list)

        for sequence in self.sequence_db.sequences:
            if len(sequence.events) >= 5:  # Minimum workflow length
                # Create workflow signature
                start_event = self._get_event_signature(sequence.events[0])
                end_event = self._get_event_signature(sequence.events[-1])
                signature = f"{start_event}...{end_event}"
                workflow_candidates[signature].append(sequence)

        # Create workflow patterns
        patterns = []
        for signature, sequences in workflow_candidates.items():
            if len(sequences) >= self.min_support:
                # Extract common steps
                common_steps = self._extract_common_steps(sequences)

                if len(common_steps) >= 3:
                    pattern = WorkflowPattern(
                        id=f"workflow_{hash(signature)}",
                        workflow_name=signature,
                        workflow_steps=common_steps,
                        frequency=len(sequences),
                        confidence=min(0.5 + len(sequences) * 0.1, 0.95),
                        completion_rate=self._calculate_completion_rate(sequences),
                    )

                    # Extract triggers
                    triggers = set()
                    for seq in sequences:
                        if hasattr(seq.events[0], "trigger"):
                            triggers.add(seq.events[0].trigger)
                    pattern.triggers = list(triggers)

                    patterns.append(pattern)

        return patterns

    def _can_extend_sequence(self, sequence: Sequence, event: Event) -> bool:
        """Check if an event can extend a sequence."""
        # Don't extend sequences that are too long
        if len(sequence.events) >= 20:
            return False

        # Check for meaningful continuation
        last_event = sequence.events[-1]

        # Same event type repetition is less interesting
        if self._get_event_signature(last_event) == self._get_event_signature(event):
            return False

        return True

    def _prune_sequences(self, current_time: float) -> None:
        """Remove old sequences from database."""
        active_sequences = []

        for sequence in self.sequence_db.sequences:
            last_time = getattr(sequence.events[-1], "timestamp", current_time)
            if current_time - last_time <= self.max_gap * 2:
                active_sequences.append(sequence)

        self.sequence_db.sequences = active_sequences

    def _get_event_signature(self, event: Event) -> str:
        """Get a signature string for an event."""
        event_type = event.__class__.__name__

        if hasattr(event, "tool"):
            return f"{event_type}:{event.tool}"
        elif hasattr(event, "command"):
            return f"{event_type}:{event.command}"
        elif hasattr(event, "file_path"):
            return f"{event_type}:file"
        else:
            return event_type

    def _find_file_groups(self, correlations: dict[str, dict[str, int]]) -> list[set[str]]:
        """Find groups of files that are often accessed together."""
        groups = []
        processed = set()

        for file1, related in correlations.items():
            if file1 in processed:
                continue

            group = {file1}
            for file2, count in related.items():
                # High correlation threshold
                total = sum(related.values())
                if count / total > 0.5:
                    group.add(file2)

            if len(group) >= 2:
                groups.append(group)
                processed.update(group)

        return groups

    def _extract_common_steps(self, sequences: list[Sequence]) -> list[dict[str, Any]]:
        """Extract common steps from multiple sequences."""
        if not sequences:
            return []

        # Count occurrences of each step
        step_counts = defaultdict(int)
        total_sequences = len(sequences)

        for sequence in sequences:
            seen_steps = set()
            for event in sequence.events:
                step_sig = self._get_event_signature(event)
                if step_sig not in seen_steps:
                    step_counts[step_sig] += 1
                    seen_steps.add(step_sig)

        # Keep steps that appear in at least 60% of sequences
        common_steps = []
        for step, count in step_counts.items():
            if count / total_sequences >= 0.6:
                common_steps.append(
                    {
                        "id": step,
                        "description": step,
                        "required": count == total_sequences,
                        "frequency": count / total_sequences,
                    }
                )

        return sorted(common_steps, key=lambda x: x["frequency"], reverse=True)

    def _calculate_completion_rate(self, sequences: list[Sequence]) -> float:
        """Calculate completion rate for workflow sequences."""
        if not sequences:
            return 0.0

        # Simple heuristic: sequences with success/completion events
        completed = 0
        for sequence in sequences:
            last_event = sequence.events[-1]
            if hasattr(last_event, "status"):
                if last_event.status in ["success", "completed", "done"]:
                    completed += 1
            elif hasattr(last_event, "result"):
                if last_event.result == "success":
                    completed += 1

        return completed / len(sequences) if sequences else 0.0
