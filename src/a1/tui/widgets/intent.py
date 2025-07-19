"""Intent Visualization Widget

Visual representation of A1's intent detection and confidence levels.
"""

from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar, Static


class IntentVisualizationWidget(Widget):
    """Widget for visualizing A1's detected intents and confidence levels.

    Shows:
    - Current detected intent
    - Confidence level with visual meter
    - Intent history
    - Evidence/reasoning for detection
    """

    DEFAULT_CSS = """
    IntentVisualizationWidget {
        height: 100%;
        padding: 1;
        border: solid $accent;
    }

    IntentVisualizationWidget .intent-header {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
        width: 100%;
    }

    IntentVisualizationWidget .current-intent {
        text-style: bold;
        text-align: center;
        padding: 1;
        margin: 1;
        border: solid;
        width: 100%;
    }

    IntentVisualizationWidget .current-intent.exploring {
        color: $primary;
        border-color: $primary;
    }

    IntentVisualizationWidget .current-intent.implementing {
        color: $success;
        border-color: $success;
    }

    IntentVisualizationWidget .current-intent.debugging {
        color: $error;
        border-color: $error;
    }

    IntentVisualizationWidget .current-intent.refactoring {
        color: $warning;
        border-color: $warning;
    }

    IntentVisualizationWidget .current-intent.testing {
        color: $accent;
        border-color: $accent;
    }

    IntentVisualizationWidget .current-intent.documenting {
        color: $secondary;
        border-color: $secondary;
    }

    IntentVisualizationWidget .current-intent.idle {
        color: $text-muted;
        border-color: $text-muted;
    }

    IntentVisualizationWidget .confidence-section {
        margin: 1;
        padding: 1;
    }

    IntentVisualizationWidget .evidence-section {
        margin: 1;
        padding: 1;
        background: $surface;
        border: solid $border;
    }

    IntentVisualizationWidget .history-section {
        margin: 1;
        padding: 1;
        height: 1fr;
        overflow-y: auto;
    }

    IntentVisualizationWidget .history-item {
        margin-bottom: 1;
        padding: 0 1;
    }

    IntentVisualizationWidget .timestamp {
        color: $text-muted;
        text-style: italic;
    }
    """

    # Reactive properties
    current_intent = reactive("IDLE")
    confidence = reactive(0.0)

    def __init__(self, **kwargs):
        """Initialize the intent visualization widget."""
        super().__init__(**kwargs)

        # Intent history
        self.intent_history: list[dict[str, Any]] = []
        self.max_history = 20

        # Current evidence
        self.current_evidence: list[str] = []

    def compose(self) -> ComposeResult:
        """Create the widget layout."""
        yield Vertical(
            Label("Intent Detection", classes="intent-header"),
            # Current intent display
            Label("IDLE", id="intent-display", classes="current-intent idle"),
            # Confidence meter
            Vertical(
                Label("Confidence Level", classes="confidence-label"),
                ProgressBar(total=100, id="confidence-bar"),
                Label("0%", id="confidence-value"),
                classes="confidence-section",
            ),
            # Evidence section
            Vertical(
                Label("Detection Evidence", classes="evidence-header"),
                Static("No evidence available", id="evidence-list"),
                classes="evidence-section",
            ),
            # History section
            Vertical(
                Label("Intent History", classes="history-header"),
                Vertical(id="history-container"),
                classes="history-section",
            ),
        )

    def update_intent(self, intent_data: dict[str, Any]) -> None:
        """Update the current intent display.

        Args:
            intent_data: Dictionary containing intent, confidence, evidence, etc.
        """
        new_intent = intent_data.get("intent", "IDLE")
        new_confidence = intent_data.get("confidence", 0.0)
        evidence = intent_data.get("evidence", [])

        # Check if intent changed
        if new_intent != self.current_intent:
            # Add to history
            self._add_to_history(self.current_intent, new_intent, new_confidence)

        # Update properties
        self.current_intent = new_intent
        self.confidence = new_confidence
        self.current_evidence = evidence

        # Refresh display
        self._refresh_display()

    def _add_to_history(self, old_intent: str, new_intent: str, confidence: float) -> None:
        """Add an intent change to history."""
        history_item = {
            "timestamp": datetime.now(),
            "old_intent": old_intent,
            "new_intent": new_intent,
            "confidence": confidence,
        }

        self.intent_history.append(history_item)

        # Trim history if too long
        if len(self.intent_history) > self.max_history:
            self.intent_history.pop(0)

        self._refresh_history()

    def _refresh_display(self) -> None:
        """Refresh the intent display."""
        # Update intent label
        intent_label = self.query_one("#intent-display", Label)
        intent_label.update(self.current_intent)

        # Update CSS class for color
        intent_label.remove_class(
            "exploring", "implementing", "debugging", "refactoring", "testing", "documenting", "idle"
        )
        intent_label.add_class(self.current_intent.lower())

        # Update confidence bar
        confidence_bar = self.query_one("#confidence-bar", ProgressBar)
        confidence_bar.progress = self.confidence * 100

        # Update confidence value
        confidence_value = self.query_one("#confidence-value", Label)
        confidence_value.update(f"{self.confidence:.0%}")

        # Update evidence
        self._refresh_evidence()

    def _refresh_evidence(self) -> None:
        """Refresh the evidence display."""
        evidence_list = self.query_one("#evidence-list", Static)

        if not self.current_evidence:
            evidence_list.update("No evidence available")
        else:
            # Format evidence as bullet points
            evidence_text = "\n".join(f"• {e}" for e in self.current_evidence[:5])
            evidence_list.update(evidence_text)

    def _refresh_history(self) -> None:
        """Refresh the history display."""
        history_container = self.query_one("#history-container", Vertical)
        history_container.remove_children()

        # Show most recent first
        for item in reversed(self.intent_history[-10:]):  # Show last 10
            history_container.mount(self._create_history_item(item))

    def _create_history_item(self, item: dict[str, Any]) -> Widget:
        """Create a widget for a history item."""
        timestamp = item["timestamp"].strftime("%H:%M:%S")
        old_intent = item["old_intent"]
        new_intent = item["new_intent"]
        confidence = item["confidence"]

        text = f"{timestamp} - {old_intent} → {new_intent} ({confidence:.0%})"

        return Label(text, classes="history-item timestamp")

    def get_intent_summary(self) -> dict[str, Any]:
        """Get a summary of current intent state."""
        return {
            "current_intent": self.current_intent,
            "confidence": self.confidence,
            "evidence_count": len(self.current_evidence),
            "history_length": len(self.intent_history),
            "recent_changes": [
                {
                    "time": item["timestamp"].isoformat(),
                    "change": f"{item['old_intent']} → {item['new_intent']}",
                    "confidence": item["confidence"],
                }
                for item in self.intent_history[-5:]
            ],
        }

    def clear_history(self) -> None:
        """Clear the intent history."""
        self.intent_history.clear()
        self._refresh_history()
