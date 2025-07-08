"""Tests for the markdown conversion functions."""

from quaestor.cli import (
    convert_architecture_to_ai_format,
    convert_manifest_to_ai_format,
    convert_memory_to_ai_format,
)


class TestManifestToAIFormat:
    """Tests for the main conversion dispatcher."""

    def test_routes_architecture_file(self, sample_architecture_manifest):
        """Test that ARCHITECTURE.md is routed to correct converter."""
        result = convert_manifest_to_ai_format(sample_architecture_manifest, "ARCHITECTURE.md")

        # Should contain AI format markers
        assert "<!-- META:document:architecture -->" in result
        assert "<!-- META:version:1.0 -->" in result
        assert "<!-- META:ai-optimized:true -->" in result

    def test_routes_memory_file(self, sample_memory_manifest):
        """Test that MEMORY.md is routed to correct converter."""
        result = convert_manifest_to_ai_format(sample_memory_manifest, "MEMORY.md")

        # Should contain AI format markers
        assert "<!-- META:document:memory -->" in result
        assert "<!-- META:version:1.0 -->" in result
        assert "<!-- META:ai-optimized:true -->" in result

    def test_unknown_file_returns_unchanged(self):
        """Test that unknown files are returned unchanged."""
        content = "# Some other markdown file"
        result = convert_manifest_to_ai_format(content, "README.md")

        assert result == content


class TestArchitectureConverter:
    """Tests for architecture markdown conversion."""

    def test_basic_conversion_structure(self):
        """Test basic AI format structure is created."""
        content = "# Simple Architecture"
        result = convert_architecture_to_ai_format(content)

        # Check basic structure
        assert "<!-- META:document:architecture -->" in result
        assert "<!-- SECTION:architecture:overview:START -->" in result
        assert "<!-- SECTION:architecture:overview:END -->" in result
        assert "pattern:" in result
        assert 'selected: "[Choose: MVC, DDD, Microservices, Monolithic, etc.]"' in result

    def test_converts_layer_sections(self):
        """Test that sections with 'layer' are converted."""
        content = """# Architecture
## System Layers
Description of layers
## Database Layer
Database details"""

        result = convert_architecture_to_ai_format(content)

        # Should have organization section
        assert "<!-- SECTION:architecture:organization:START -->" in result
        assert "## Code Organization" in result
        assert "<!-- DATA:directory-structure:START -->" in result

    def test_converts_structure_sections(self):
        """Test that sections with 'structure' are converted."""
        content = """# Architecture
## Project Structure
How the project is organized"""

        result = convert_architecture_to_ai_format(content)

        assert "<!-- SECTION:architecture:organization:START -->" in result
        assert "structure:" in result
        assert 'path: "src/"' in result

    def test_converts_component_sections(self):
        """Test that sections with 'component' are converted."""
        content = """# Architecture
## Core Components
- Order Service
- Payment Service"""

        result = convert_architecture_to_ai_format(content)

        assert "<!-- SECTION:architecture:core-concepts:START -->" in result
        assert "## Core Concepts" in result
        assert "<!-- DATA:key-components:START -->" in result
        assert "components:" in result

    def test_converts_concept_sections(self):
        """Test that sections with 'concept' are converted."""
        content = """# Architecture
## Domain Concepts
Key business concepts"""

        result = convert_architecture_to_ai_format(content)

        assert "<!-- SECTION:architecture:core-concepts:START -->" in result
        assert "components:" in result
        assert 'name: "[Component Name]"' in result

    def test_handles_empty_content(self):
        """Test conversion of empty content."""
        result = convert_architecture_to_ai_format("")

        # Should still have basic structure
        assert "<!-- META:document:architecture -->" in result
        assert "# Project Architecture" in result

    def test_handles_sections_without_content(self):
        """Test sections that have no content after title."""
        content = """# Architecture
## Empty Layer Section
## Another Section
With content"""

        result = convert_architecture_to_ai_format(content)

        # Should not crash and should include organization section
        assert "<!-- SECTION:architecture:organization:START -->" in result


class TestMemoryConverter:
    """Tests for memory markdown conversion."""

    def test_basic_conversion_structure(self):
        """Test basic AI format structure is created."""
        content = "# Simple Memory"
        result = convert_memory_to_ai_format(content)

        # Check basic structure
        assert "<!-- META:document:memory -->" in result
        assert "<!-- SECTION:memory:purpose:START -->" in result
        assert "<!-- SECTION:memory:status:START -->" in result
        assert "<!-- DATA:project-status:START -->" in result
        assert 'last_updated: "[Date]"' in result

    def test_converts_timeline_sections(self):
        """Test that sections with 'timeline' are converted."""
        content = """# Memory
## Project Timeline
- Phase 1: Complete
- Phase 2: In Progress"""

        result = convert_memory_to_ai_format(content)

        assert "<!-- SECTION:memory:timeline:START -->" in result
        assert "## Project Timeline" in result
        assert "<!-- DATA:milestones:START -->" in result
        assert "milestones:" in result

    def test_converts_milestone_sections(self):
        """Test that sections with 'milestone' are converted."""
        content = """# Memory
## Milestone 1: Core Features
Completed successfully"""

        result = convert_memory_to_ai_format(content)

        assert "<!-- SECTION:memory:timeline:START -->" in result
        assert 'name: "[Name]"' in result
        assert 'status: "[Status]"' in result

    def test_converts_action_sections(self):
        """Test that sections with 'action' are converted."""
        content = """# Memory
## Action Items
- Fix bug in payment
- Add tests"""

        result = convert_memory_to_ai_format(content)

        assert "<!-- SECTION:memory:actions:START -->" in result
        assert "## Next Actions" in result
        assert "<!-- DATA:next-actions:START -->" in result
        assert "actions:" in result

    def test_converts_next_sections(self):
        """Test that sections with 'next' are converted."""
        content = """# Memory
## Next Steps
1. Deploy to staging
2. Run integration tests"""

        result = convert_memory_to_ai_format(content)

        assert "<!-- SECTION:memory:actions:START -->" in result
        assert "immediate:" in result
        assert 'timeframe: "This Week"' in result

    def test_handles_empty_content(self):
        """Test conversion of empty content."""
        result = convert_memory_to_ai_format("")

        # Should still have basic structure
        assert "<!-- META:document:memory -->" in result
        assert "# Project Memory & Progress Tracking" in result

    def test_preserves_document_footer(self):
        """Test that document footer is preserved."""
        content = "# Memory\n## Status\nActive"
        result = convert_memory_to_ai_format(content)

        assert result.endswith(
            "---\n*This document serves as the living memory of current progress. "
            "Update it regularly as you complete tasks and learn new insights.*"
        )


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handles_malformed_sections(self):
        """Test handling of malformed markdown sections."""
        content = """###No space after hashes
##
## Title with ### nested headers"""

        # Should not crash
        arch_result = convert_architecture_to_ai_format(content)
        mem_result = convert_memory_to_ai_format(content)

        assert "<!-- META:document:architecture -->" in arch_result
        assert "<!-- META:document:memory -->" in mem_result

    def test_handles_unicode_content(self):
        """Test handling of unicode characters."""
        content = """# Architecture 架构
## Components 组件
- Service 服务 🚀
- Database 数据库 📊"""

        result = convert_architecture_to_ai_format(content)

        # Should preserve structure without crashing
        assert "<!-- SECTION:architecture:core-concepts:START -->" in result

    def test_handles_very_long_lines(self):
        """Test handling of very long lines."""
        long_line = "A" * 1000
        content = f"""# Architecture
## Components
{long_line}"""

        result = convert_architecture_to_ai_format(content)

        # Should handle without issues
        assert "<!-- SECTION:architecture:core-concepts:START -->" in result
