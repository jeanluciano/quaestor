"""Tests for the converter functions."""

from quaestor.converters import (
    convert_architecture_to_ai_format,
    convert_manifest_to_ai_format,
    convert_memory_to_ai_format,
)


class TestArchitectureConverter:
    """Tests for ARCHITECTURE.md conversion."""

    def test_convert_basic_architecture(self, sample_architecture_manifest):
        """Test conversion of basic architecture content."""
        result = convert_architecture_to_ai_format(sample_architecture_manifest)

        # Check metadata headers
        assert "<!-- META:document:architecture -->" in result
        assert "<!-- META:version:1.0 -->" in result
        assert "<!-- META:ai-optimized:true -->" in result

        # Check section markers
        assert "<!-- SECTION:architecture:overview:START -->" in result
        assert "<!-- SECTION:architecture:overview:END -->" in result

        # Check content preservation
        assert "Project Architecture" in result
        assert "Domain-Driven Design" in result
        assert "clean separation of concerns" in result

        # Check YAML data blocks
        assert "<!-- DATA:architecture-pattern:START -->" in result
        assert 'pattern: "Domain-Driven Design (DDD)"' in result
        assert "<!-- DATA:architecture-pattern:END -->" in result

    def test_convert_architecture_with_components(self):
        """Test conversion with component descriptions."""
        content = """# System Architecture

## Core Components
- **Auth Service**: Handles user authentication and authorization
- **Payment Gateway**: Processes payment transactions
- **Notification Engine**: Manages email and SMS notifications
"""
        result = convert_architecture_to_ai_format(content)

        # Check components section
        assert "<!-- SECTION:architecture:core-concepts:START -->" in result
        assert "<!-- DATA:key-components:START -->" in result
        assert 'name: "Auth Service"' in result
        assert 'responsibility: "Handles user authentication and authorization"' in result
        assert 'name: "Payment Gateway"' in result
        assert 'responsibility: "Processes payment transactions"' in result

    def test_convert_architecture_with_directory_structure(self):
        """Test conversion with directory structure."""
        content = """# Architecture

## Project Organization
```
src/
├── domain/
│   ├── entities/
│   └── value_objects/
├── application/
│   └── services/
└── infrastructure/
    └── repositories/
```
"""
        result = convert_architecture_to_ai_format(content)

        # Check organization section
        assert "<!-- SECTION:architecture:organization:START -->" in result
        assert "<!-- DATA:directory-structure:START -->" in result
        assert "structure:" in result
        assert '"src/"' in result or "'src/'" in result
        assert '"domain/"' in result or "'domain/'" in result

    def test_convert_architecture_empty_content(self):
        """Test conversion of empty content."""
        result = convert_architecture_to_ai_format("")

        # Should still have basic structure
        assert "<!-- META:document:architecture -->" in result
        assert "# Project Architecture" in result
        assert "This document describes the technical architecture" in result

    def test_convert_architecture_with_integrations(self):
        """Test conversion with external integrations."""
        content = """# Architecture

## External Integrations
- Stripe API for payment processing
- SendGrid for email delivery
- AWS S3 for file storage
- Redis for caching
"""
        result = convert_architecture_to_ai_format(content)

        # Check integrations section
        assert "<!-- SECTION:architecture:integrations:START -->" in result
        assert "<!-- DATA:external-integrations:START -->" in result
        assert "Stripe API for payment processing" in result
        assert "SendGrid for email delivery" in result


class TestMemoryConverter:
    """Tests for MEMORY.md conversion."""

    def test_convert_basic_memory(self, sample_memory_manifest):
        """Test conversion of basic memory content."""
        result = convert_memory_to_ai_format(sample_memory_manifest)

        # Check metadata headers
        assert "<!-- META:document:memory -->" in result
        assert "<!-- META:version:1.0 -->" in result
        assert "<!-- META:ai-optimized:true -->" in result

        # Check section markers
        assert "<!-- SECTION:memory:status:START -->" in result
        assert "<!-- SECTION:memory:status:END -->" in result
        assert "<!-- SECTION:memory:timeline:START -->" in result
        assert "<!-- SECTION:memory:timeline:END -->" in result

        # Check content preservation
        assert "Project Memory & Progress Tracking" in result
        assert "Current Status" in result
        assert "Project Timeline" in result

        # Check YAML data blocks
        assert "<!-- DATA:project-status:START -->" in result
        assert 'last_updated: "2024-01-15"' in result
        assert 'current_phase: "Development"' in result
        assert 'overall_progress: "60%"' in result

    def test_convert_memory_with_milestones(self):
        """Test conversion with milestone tracking."""
        content = """# Memory

## Project Timeline
### Phase 1: Core Features (Complete)
- ✅ Basic order processing
- ✅ User authentication

### Week 2: Advanced Features (CURRENT)
Goal: Add advanced features
- 🚧 Payment integration
- ⬜ Inventory tracking
"""
        result = convert_memory_to_ai_format(content)

        # Check milestones section
        assert "<!-- DATA:milestones:START -->" in result
        assert 'name: "Phase 1: Core Features (Complete)"' in result
        assert 'status: "completed"' in result
        assert 'name: "Week 2: Advanced Features (CURRENT)"' in result
        assert 'status: "current"' in result
        assert 'goal: "Add advanced features"' in result

    def test_convert_memory_with_actions(self):
        """Test conversion with next actions."""
        content = """# Memory

## Next Actions
### Immediate (This Week)
1. Complete payment gateway integration
2. Add unit tests for order service
3. Fix authentication bug

### Short Term (Next 2 Weeks)
- Implement inventory tracking
- Set up CI/CD pipeline

### Long Term (Next Month)
- Performance optimization
- Documentation update
"""
        result = convert_memory_to_ai_format(content)

        # Check actions section
        assert "<!-- SECTION:memory:actions:START -->" in result
        assert "<!-- DATA:next-actions:START -->" in result
        assert "immediate:" in result
        assert 'timeframe: "This Week"' in result
        assert 'task: "Complete payment gateway integration"' in result
        assert 'task: "Add unit tests for order service"' in result
        assert "short_term:" in result
        assert 'task: "Implement inventory tracking"' in result

    def test_convert_memory_empty_content(self):
        """Test conversion of empty content."""
        result = convert_memory_to_ai_format("")

        # Should still have basic structure
        assert "<!-- META:document:memory -->" in result
        assert "# Project Memory & Progress Tracking" in result
        assert "This document serves as the living memory" in result

    def test_convert_memory_with_custom_sections(self):
        """Test conversion with custom section names."""
        content = """# Project Progress

## Active Work
Current focus on authentication system

## Completed Tasks
- Database schema design
- API structure

## Upcoming Work
- Frontend implementation
- Testing suite
"""
        result = convert_memory_to_ai_format(content)

        # Should handle generic sections
        assert "<!-- SECTION:memory:active-work:START -->" in result
        assert "<!-- SECTION:memory:completed-tasks:START -->" in result
        assert "<!-- SECTION:memory:upcoming-work:START -->" in result


class TestManifestConverter:
    """Tests for the main converter function."""

    def test_convert_manifest_routes_architecture(self, sample_architecture_manifest):
        """Test that manifest converter routes to architecture converter."""
        result = convert_manifest_to_ai_format(sample_architecture_manifest, "ARCHITECTURE.md")

        # Should have architecture-specific markers
        assert "<!-- META:document:architecture -->" in result
        assert "<!-- SECTION:architecture:" in result

    def test_convert_manifest_routes_memory(self, sample_memory_manifest):
        """Test that manifest converter routes to memory converter."""
        result = convert_manifest_to_ai_format(sample_memory_manifest, "MEMORY.md")

        # Should have memory-specific markers
        assert "<!-- META:document:memory -->" in result
        assert "<!-- SECTION:memory:" in result

    def test_convert_manifest_unknown_file(self):
        """Test that unknown files are returned as-is."""
        content = "# Unknown File\n\nSome content here."
        result = convert_manifest_to_ai_format(content, "UNKNOWN.md")

        # Should return content unchanged
        assert result == content


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_malformed_yaml_characters(self):
        """Test handling of special characters in YAML."""
        content = """# Architecture

## Core Concepts
- **Service: Name**: Has colons in name
- **Component "Quoted"**: Has quotes
"""
        result = convert_architecture_to_ai_format(content)

        # Should handle special characters properly
        assert "```yaml" in result
        assert "name:" in result
        # Content should be properly escaped/quoted

    def test_nested_lists_and_structures(self):
        """Test handling of nested content."""
        content = """# Memory

## Current Status
- **Phase**: Development
  - Subphase: Testing
  - Progress: 80%
- **Team**:
  - Frontend: 2 developers
  - Backend: 3 developers
"""
        result = convert_memory_to_ai_format(content)

        # Should preserve structure
        assert "Development" in result

    def test_very_long_section_names(self):
        """Test handling of very long section names."""
        content = """# Architecture

## This Is A Very Long Section Name That Should Be Handled Properly Without Breaking The Format

Some content here.
"""
        result = convert_architecture_to_ai_format(content)

        # Should create valid section ID
        assert "<!-- SECTION:architecture:" in result
        assert ":START -->" in result
        assert ":END -->" in result

    def test_unicode_and_emojis(self):
        """Test handling of unicode and emojis."""
        content = """# Memory 🧠

## Current Status 📊
- ✅ Task completed
- 🚧 Work in progress
- ❌ Failed task
- 📝 Documentation needed
"""
        result = convert_memory_to_ai_format(content)

        # Should preserve unicode/emojis
        assert "🧠" in result
        assert "✅" in result
        assert "🚧" in result
