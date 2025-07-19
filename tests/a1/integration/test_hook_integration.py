"""Integration tests for A1 hook system."""

import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from a1.core.events import ClaudeEvent
from a1.hooks.claude_receiver import ClaudeHookReceiver
from a1.service.client import A1ServiceClient
from a1.service.core import A1Service


class TestHookIntegration:
    """Test hook receiver integration."""

    def test_claude_receiver_creation(self):
        """Test creating Claude hook receiver."""
        receiver = ClaudeHookReceiver()
        assert receiver.service_client is not None
        assert isinstance(receiver.service_client, A1ServiceClient)

    def test_hook_processing(self):
        """Test processing hook data."""
        receiver = ClaudeHookReceiver()

        # Mock the service client to handle sync call
        async def mock_send_event(event):
            return True
        
        with patch.object(receiver.service_client, 'send_event', new=mock_send_event):
            # Test data
            hook_data = {"tool": "Read", "file_path": "/test.py", "timestamp": datetime.now().isoformat()}

            # Process hook
            result = receiver.process_hook("post_tool_use", hook_data)

            assert result["status"] == "received"
            assert result["a1"] == "processing"

    def test_hook_error_handling(self):
        """Test hook error handling."""
        receiver = ClaudeHookReceiver()

        # Mock service client to raise error
        receiver.service_client.send_event = Mock(side_effect=Exception("Test error"))

        # Should not fail Claude operation
        result = receiver.process_hook("test_hook", {})

        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert result["a1"] == "failed"

    def test_all_hook_handlers(self):
        """Test all hook handler methods."""
        receiver = ClaudeHookReceiver()

        # Mock send_event
        mock_send = AsyncMock(return_value=True)
        receiver.service_client.send_event = mock_send

        test_data = {"test": "data"}

        # Test each handler
        handlers = [
            ("handle_pre_stop", "pre_stop"),
            ("handle_stop", "stop"),
            ("handle_pre_tool_use", "pre_tool_use"),
            ("handle_post_tool_use", "post_tool_use"),
            ("handle_pre_file_edit", "pre_file_edit"),
            ("handle_post_file_edit", "post_file_edit"),
            ("handle_pre_user_prompt", "pre_user_prompt_submit"),
            ("handle_pre_text_gen", "pre_process_text_generation"),
            ("handle_file_change", "file_change"),
            ("handle_test_run", "test_run"),
        ]

        for handler_name, _expected_type in handlers:
            handler = getattr(receiver, handler_name)
            result = handler(test_data)

            assert result["status"] == "received"
            assert result["a1"] == "processing"


class TestServiceIntegration:
    """Test A1 service integration."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service start/stop lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Configure with temp socket
            config = {
                "socket_path": str(Path(tmpdir) / "test.sock"),
                "components": {"analysis_engine": {"enabled": False}, "learning_manager": {"enabled": False}},
            }

            service = A1Service(config)

            # Initialize
            await service.initialize()

            # Start
            await service.start()
            assert service.running is True

            # Stop
            await service.stop()
            assert service.running is False

    @pytest.mark.asyncio
    async def test_event_processing_pipeline(self):
        """Test full event processing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "socket_path": str(Path(tmpdir) / "test.sock"),
                "components": {"analysis_engine": {"enabled": False}, "learning_manager": {"enabled": False}},
                "hooks": {"receive_from_a1": False},
            }

            service = A1Service(config)
            await service.initialize()
            await service.start()

            # Create test event
            event = ClaudeEvent(type="post_tool_use", data={"tool": "Read", "file": "test.py"})

            # Process event
            await service.process_event(event)

            # Give time to process
            await asyncio.sleep(0.1)

            # Check intent was detected
            assert service.intent_detector.current_intent is not None

            await service.stop()

    @pytest.mark.asyncio
    async def test_client_service_communication(self):
        """Test client-service communication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "test.sock"

            # Start service
            service = A1Service({"socket_path": str(socket_path)})
            await service.initialize()
            await service.start()

            # Create client
            client = A1ServiceClient(socket_path)

            # Send event
            event = ClaudeEvent(type="test_event", data={"message": "hello"})

            result = await client.send_event(event)
            assert result is True

            # Check if running
            is_running = await client.is_service_running()
            assert is_running is True

            await service.stop()


class TestHookScript:
    """Test the hook script entry point."""

    def test_main_no_args(self, capsys):
        """Test main with no arguments."""
        with patch.object(sys, "argv", ["claude_receiver.py"]), pytest.raises(SystemExit) as exc_info:
            from a1.hooks.claude_receiver import main

            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Hook type not specified" in captured.out

    def test_main_invalid_json(self, capsys):
        """Test main with invalid JSON input."""
        with (
            patch.object(sys, "argv", ["claude_receiver.py", "test_hook"]),
            patch("sys.stdin", MockStdin("invalid json")),
            pytest.raises(SystemExit) as exc_info,
        ):
            from a1.hooks.claude_receiver import main

            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Failed to parse input" in captured.out

    def test_main_unknown_hook(self, capsys):
        """Test main with unknown hook type."""
        with (
            patch.object(sys, "argv", ["claude_receiver.py", "unknown_hook"]),
            patch("sys.stdin", MockStdin('{"test": "data"}')),
            pytest.raises(SystemExit) as exc_info,
        ):
            from a1.hooks.claude_receiver import main

            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown hook type: unknown_hook" in captured.out

    def test_main_successful_processing(self, capsys):
        """Test main with successful processing."""
        with (
            patch.object(sys, "argv", ["claude_receiver.py", "post_tool_use"]),
            patch("sys.stdin", MockStdin('{"tool": "Read", "file": "test.py"}')),
            patch("a1.hooks.claude_receiver.ClaudeHookReceiver") as MockReceiver,
        ):
            mock_instance = Mock()
            mock_instance.handle_post_tool_use.return_value = {"status": "received", "a1": "processing"}
            MockReceiver.return_value = mock_instance

            from a1.hooks.claude_receiver import main

            main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["status"] == "received"
        assert result["a1"] == "processing"


class MockStdin:
    """Mock stdin for testing."""

    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data
