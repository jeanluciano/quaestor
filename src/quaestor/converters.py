"""Conversion utilities for transforming manifest formats to AI-optimized formats.

This module contains functions for converting human-readable markdown formats
to AI-optimized formats with enhanced structure and metadata.
"""


def convert_manifest_to_ai_format(content: str, filename: str) -> str:
    """Convert human-readable manifest markdown to AI-optimized format."""
    if filename == "ARCHITECTURE.md":
        return convert_architecture_to_ai_format(content)
    elif filename == "MEMORY.md":
        return convert_memory_to_ai_format(content)
    return content


def convert_architecture_to_ai_format(content: str) -> str:
    """Convert ARCHITECTURE.md from manifest to AI format."""
    ai_content = """<!-- META:document:architecture -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

# Project Architecture

"""

    # Parse the content more intelligently
    lines = content.split("\n")
    current_section = None
    section_content = []

    # Extract title if exists
    for line in lines:
        if line.startswith("# ") and "Architecture" in line:
            ai_content = ai_content.replace("# Project Architecture", line)
            break

    # Process sections
    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle main sections (##)
        if line.startswith("## "):
            # Save previous section if exists
            if current_section:
                ai_content += _format_section(current_section, section_content)

            current_section = line[3:].strip()
            section_content = []
            i += 1
            continue

        # Accumulate section content
        if current_section:
            section_content.append(line)

        i += 1

    # Don't forget the last section
    if current_section:
        ai_content += _format_section(current_section, section_content)

    ai_content += (
        "\n---\n"
        "*This document describes the technical architecture of the project. "
        "Update it as architectural decisions are made or changed.*"
    )

    return ai_content


def convert_memory_to_ai_format(content: str) -> str:
    """Convert MEMORY.md from manifest to AI format."""
    ai_content = """<!-- META:document:memory -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

# Project Memory & Progress Tracking

"""

    # Parse content intelligently
    lines = content.split("\n")
    current_section = None
    section_content = []

    # Extract title if exists
    for line in lines:
        if line.startswith("# ") and ("Memory" in line or "Progress" in line):
            ai_content = ai_content.replace("# Project Memory & Progress Tracking", line)
            break

    # Process sections
    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle main sections (##)
        if line.startswith("## "):
            # Save previous section if exists
            if current_section:
                ai_content += _format_memory_section(current_section, section_content)

            current_section = line[3:].strip()
            section_content = []
            i += 1
            continue

        # Accumulate section content
        if current_section:
            section_content.append(line)

        i += 1

    # Don't forget the last section
    if current_section:
        ai_content += _format_memory_section(current_section, section_content)

    ai_content += (
        "\n---\n"
        "*This document serves as the living memory of current progress. "
        "Update it regularly as you complete tasks and learn new insights.*"
    )

    return ai_content


def _section_wrapper(section_id: str, title: str) -> str:
    """Create section wrapper with title."""
    return f"\n<!-- SECTION:{section_id}:START -->\n## {title}\n\n"


def _yaml_block(block_id: str, data: dict) -> str:
    """Create a YAML data block."""
    result = f"<!-- DATA:{block_id}:START -->\n```yaml\n"

    def format_value(value, indent=""):
        if isinstance(value, list):
            output = ""
            for item in value:
                if isinstance(item, dict):
                    output += f"{indent}- "
                    first = True
                    for k, v in item.items():
                        if first:
                            if isinstance(v, list | dict):
                                output += f"{k}:\n"
                                output += format_value(v, indent + "  ")
                            else:
                                output += f'{k}: "{v}"\n'
                            first = False
                        else:
                            if isinstance(v, list | dict):
                                output += f"{indent}  {k}:\n"
                                output += format_value(v, indent + "    ")
                            else:
                                output += f'{indent}  {k}: "{v}"\n'
                else:
                    output += f'{indent}- "{item}"\n'
            return output
        elif isinstance(value, dict):
            output = ""
            for k, v in value.items():
                if isinstance(v, list | dict):
                    output += f"{indent}{k}:\n"
                    output += format_value(v, indent + "  ")
                else:
                    output += f'{indent}{k}: "{v}"\n'
            return output
        else:
            return f'"{value}"\n'

    for key, value in data.items():
        result += f"{key}:\n" if isinstance(value, list | dict) else f"{key}: "
        result += format_value(value, "  ")

    result += "```\n<!-- DATA:" + block_id + ":END -->\n"
    return result


def _format_section(title: str, content: list[str]) -> str:
    """Format a section with appropriate AI-optimized structure."""
    # Determine section type and format accordingly
    if "overview" in title.lower():
        return _format_overview_section(title, content)
    elif any(word in title.lower() for word in ["organization", "structure", "directory"]):
        return _format_organization_section(title, content)
    elif any(word in title.lower() for word in ["concept", "entities", "component", "domain"]):
        return _format_concepts_section(title, content)
    elif any(word in title.lower() for word in ["integration", "external", "api"]):
        return _format_integration_section(title, content)
    else:
        return _format_generic_section(title, content)


def _format_overview_section(title: str, content: list[str]) -> str:
    """Format architecture overview section."""
    result = _section_wrapper("architecture:overview", title)
    content_text = "\n".join(content)

    # Detect architecture pattern
    patterns = {
        "Domain-Driven Design (DDD)": ["Domain-Driven Design", "DDD"],
        "Microservices": ["Microservices"],
        "MVC": ["MVC"],
    }
    pattern = next(
        (name for name, keywords in patterns.items() if any(kw in content_text for kw in keywords)),
        "Custom Architecture",
    )

    # Extract principles
    principles = [
        line.strip()[2:].split(":")[0].strip() for line in content if line.strip().startswith("- ") and ":" in line
    ][:5]

    if pattern or principles:
        yaml_data = {"pattern": pattern} if pattern else {}
        if principles:
            yaml_data["principles"] = principles
        result += _yaml_block("architecture-pattern", yaml_data) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:architecture:overview:END -->\n"


def _format_organization_section(title: str, content: list[str]) -> str:
    """Format code organization section."""
    result = _section_wrapper("architecture:organization", title)

    # Extract directory structure from code blocks
    in_code_block = False
    structure = []
    for line in content:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        elif in_code_block and any(c in line for c in ["/", "├", "└", "│"]):
            clean = line.replace("├──", "").replace("└──", "").replace("│", "").strip()
            if clean and "/" in clean:
                structure.append(clean)

    if structure:
        result += _yaml_block("directory-structure", {"structure": structure}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:architecture:organization:END -->\n"


def _format_concepts_section(title: str, content: list[str]) -> str:
    """Format core concepts section."""
    result = _section_wrapper("architecture:core-concepts", title)

    # Extract components with descriptions
    components = []
    for line in content:
        if line.strip().startswith("- **") and "**:" in line:
            parts = line.strip()[2:].split(":", 1)
            name = parts[0].replace("**", "").strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            components.append({"name": name, "responsibility": desc})

    if components:
        result += _yaml_block("key-components", {"components": components}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:architecture:core-concepts:END -->\n"


def _format_integration_section(title: str, content: list[str]) -> str:
    """Format external integration section."""
    result = _section_wrapper("architecture:integrations", title)

    # Extract integration points
    integrations = [
        line.strip()[2:]
        for line in content
        if line.strip().startswith("- ") and any(w in line.lower() for w in ["integration", "api", "service"])
    ]

    if integrations:
        result += _yaml_block("external-integrations", {"integrations": integrations}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:architecture:integrations:END -->\n"


def _format_generic_section(title: str, content: list[str]) -> str:
    """Format a generic section."""
    section_id = title.lower().replace(" ", "-").replace("&", "and")
    result = _section_wrapper(f"architecture:{section_id}", title)
    return result + "\n".join(content) + f"\n<!-- SECTION:architecture:{section_id}:END -->\n"


# Memory-specific formatting functions
def _format_memory_section(title: str, content: list[str]) -> str:
    """Format a memory section with appropriate structure."""
    # Determine section type and format accordingly
    if any(word in title.lower() for word in ["purpose", "document purpose"]):
        return _format_purpose_section(title, content)
    elif any(word in title.lower() for word in ["status", "current status"]):
        return _format_status_section(title, content)
    elif any(word in title.lower() for word in ["timeline", "milestone", "phases"]):
        return _format_timeline_section(title, content)
    elif any(word in title.lower() for word in ["action", "next", "todo"]):
        return _format_actions_section(title, content)
    else:
        return _format_generic_memory_section(title, content)


def _format_purpose_section(title: str, content: list[str]) -> str:
    """Format document purpose section."""
    return _section_wrapper("memory:purpose", title) + "\n".join(content) + "\n<!-- SECTION:memory:purpose:END -->\n"


def _format_status_section(title: str, content: list[str]) -> str:
    """Format current status section."""
    result = _section_wrapper("memory:status", title)

    # Extract status information
    status_keys = {
        "**Last Updated**:": "last_updated",
        "**Current Phase**:": "current_phase",
        "**Current Week**:": "current_week",
        "**Overall Progress**:": "overall_progress",
        "**Current Milestone**:": "current_milestone",
    }

    status_data = {}
    for line in content:
        for prefix, key in status_keys.items():
            if prefix in line:
                status_data[key] = line.split(":", 1)[1].strip()
                break

    if status_data:
        result += _yaml_block("project-status", {"status": status_data}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:memory:status:END -->\n"


def _format_timeline_section(title: str, content: list[str]) -> str:
    """Format timeline/milestone section."""
    result = _section_wrapper("memory:timeline", title)

    # Look for milestone-like structures
    milestones = []
    current_milestone = None

    for line in content:
        if line.strip().startswith(("### Week", "### Phase")):
            if current_milestone:
                milestones.append(current_milestone)
            milestone_line = line.strip()[4:]
            status = "planned"
            if "CURRENT" in milestone_line:
                status = "current"
            elif "Complete" in milestone_line:
                status = "completed"
            current_milestone = {"name": milestone_line, "status": status}
        elif current_milestone:
            if "CURRENT" in line:
                current_milestone["status"] = "current"
            elif "✅" in line or "Complete" in line:
                current_milestone["status"] = "completed"
            elif "Goal:" in line:
                current_milestone["goal"] = line.split(":", 1)[1].strip()

    if current_milestone:
        milestones.append(current_milestone)

    if milestones:
        milestone_data = []
        for i, m in enumerate(milestones):
            data = {"id": f"milestone_{i + 1}", "name": m["name"], "status": m["status"]}
            if "goal" in m:
                data["goal"] = m["goal"]
            milestone_data.append(data)
        result += _yaml_block("milestones", {"milestones": milestone_data}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:memory:timeline:END -->\n"


def _format_actions_section(title: str, content: list[str]) -> str:
    """Format next actions section."""
    result = _section_wrapper("memory:actions", title)

    # Extract action items
    actions = {"immediate": [], "short_term": [], "long_term": []}
    current_timeframe = None
    timeframe_map = {"immediate": "This Week", "short_term": "Next 2 Weeks", "long_term": "Next Month"}

    for line in content:
        if any(term in line for term in ["Immediate", "This Week"]):
            current_timeframe = "immediate"
        elif any(term in line for term in ["Short Term", "Next 2 Weeks"]):
            current_timeframe = "short_term"
        elif any(term in line for term in ["Long Term", "Next Month"]):
            current_timeframe = "long_term"
        elif current_timeframe and line.strip():
            # Extract tasks that start with common prefixes
            task = line.strip()
            for prefix in ["1.", "2.", "3.", "-", "•", "⬜"]:
                if task.startswith(prefix):
                    task = task[len(prefix) :].strip()
                    break
            if task and not any(task.startswith(p) for p in ["1.", "2.", "3.", "-", "•", "⬜"]):
                actions[current_timeframe].append(task)

    if any(actions.values()):
        action_data = {}
        for tf, tasks in actions.items():
            if tasks:
                action_data[tf] = {
                    "timeframe": timeframe_map[tf],
                    "tasks": [{"id": f"{tf}_{i + 1}", "task": t} for i, t in enumerate(tasks)],
                }
        result += _yaml_block("next-actions", {"actions": action_data}) + "\n"

    return result + "\n".join(content) + "\n<!-- SECTION:memory:actions:END -->\n"


def _format_generic_memory_section(title: str, content: list[str]) -> str:
    """Format a generic memory section."""
    section_id = title.lower().replace(" ", "-").replace("&", "and")
    return (
        _section_wrapper(f"memory:{section_id}", title)
        + "\n".join(content)
        + f"\n<!-- SECTION:memory:{section_id}:END -->\n"
    )
