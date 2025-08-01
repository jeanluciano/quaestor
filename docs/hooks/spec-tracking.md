# Specification Tracking Hooks

Specification tracking hooks automatically monitor the lifecycle of specifications, from creation through completion. These hooks provide automated progress tracking, validation, and workflow orchestration for specification-driven development.

## Overview

Specification tracking hooks handle:
- **Lifecycle Management**: Track specifications from draft to completion
- **Progress Monitoring**: Monitor implementation progress and specification status
- **Validation**: Ensure specifications meet quality standards
- **Integration**: Connect specifications with external tools and workflows
- **Notifications**: Keep stakeholders informed of progress

## Built-in Specification Events

### Core Specification Events
```python
# Specification lifecycle events
@hook.on('spec-created')
def on_specification_created(spec_id: str, spec_data: dict):
    """Triggered when a new specification is created."""
    pass

@hook.on('spec-updated')
def on_specification_updated(spec_id: str, changes: dict):
    """Triggered when specification is modified."""
    pass

@hook.on('spec-approved')
def on_specification_approved(spec_id: str, approver: str):
    """Triggered when specification is approved for implementation."""
    pass

@hook.on('spec-started')
def on_specification_started(spec_id: str, assignee: str):
    """Triggered when implementation begins."""
    pass

@hook.on('spec-completed')
def on_specification_completed(spec_id: str, completion_data: dict):
    """Triggered when specification implementation is finished."""
    pass

@hook.on('spec-blocked')
def on_specification_blocked(spec_id: str, blocker: dict):
    """Triggered when specification is blocked by dependencies."""
    pass
```

### Implementation Events
```python
# Implementation progress events
@hook.on('spec-implementation-started')
def on_implementation_started(spec_id: str, agent: str):
    """Triggered when an agent starts implementing a specification."""
    pass

@hook.on('spec-tests-added')
def on_tests_added(spec_id: str, test_count: int):
    """Triggered when tests are added for a specification."""
    pass

@hook.on('spec-documentation-updated')
def on_documentation_updated(spec_id: str, doc_type: str):
    """Triggered when specification documentation is updated."""
    pass

@hook.on('spec-review-completed')
def on_review_completed(spec_id: str, review_result: dict):
    """Triggered when specification review is completed."""
    pass
```

## Default Specification Tracker

The built-in specification tracker provides comprehensive monitoring:

```python
# .quaestor/hooks/spec_tracker.py
import logging
from datetime import datetime
from typing import Dict, Any

from quaestor.hooks import hook
from quaestor.core.specs import SpecificationManager

logger = logging.getLogger(__name__)

class SpecificationTracker:
    """Tracks specification lifecycle and progress."""
    
    def __init__(self):
        self.spec_manager = SpecificationManager()
    
    @hook.on('spec-created')
    def track_creation(self, spec_id: str, spec_data: Dict[str, Any]):
        """Track specification creation."""
        logger.info(f"📋 New specification created: {spec_id}")
        
        # Record creation metrics
        self._record_event('created', spec_id, spec_data)
        
        # Check dependencies
        self._validate_dependencies(spec_id, spec_data)
        
        # Update specification metadata
        self._update_specification_metadata(spec_id, spec_data)
    
    @hook.on('spec-completed')
    def track_completion(self, spec_id: str, completion_data: Dict[str, Any]):
        """Track specification completion."""
        logger.info(f"✅ Specification completed: {spec_id}")
        
        # Record completion metrics
        self._record_event('completed', spec_id, completion_data)
        
        # Update specification status
        self.spec_manager.mark_completed(spec_id, completion_data)
        
        # Check related specifications
        self._check_related_specifications(spec_id)
        
        # Trigger dependent specifications
        self._trigger_dependent_specs(spec_id)
        
        # Create pull request if configured
        if self._should_create_pr(spec_id):
            self._create_pull_request(spec_id, completion_data)
    
    def _record_event(self, event_type: str, spec_id: str, data: Dict[str, Any]):
        """Record specification event for analytics."""
        event = {
            'event_type': event_type,
            'spec_id': spec_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Store in metrics database
        self.spec_manager.record_event(event)
        
        # Update dashboard
        self._update_dashboard_metrics()
    
    def _check_related_specifications(self, completed_spec_id: str):
        """Check related specifications after completion."""
        related_specs = self.spec_manager.get_related_specs(completed_spec_id)
        
        all_completed = all(
            self.spec_manager.is_completed(spec_id) 
            for spec_id in related_specs
        )
        
        if all_completed and len(related_specs) > 1:
            logger.info(f"🎯 Related specification group completed")
            
            # Trigger group completion hooks
            hook.trigger('spec-group-completed', {
                'completed_specs': related_specs,
                'completion_time': datetime.now()
            })
    
    def _trigger_dependent_specs(self, completed_spec_id: str):
        """Trigger specifications that depend on the completed one."""
        dependent_specs = self.spec_manager.get_dependent_specs(completed_spec_id)
        
        for dep_spec_id in dependent_specs:
            if self._all_dependencies_met(dep_spec_id):
                logger.info(f"🚀 Triggering dependent spec: {dep_spec_id}")
                
                hook.trigger('spec-ready-for-implementation', {
                    'spec_id': dep_spec_id,
                    'trigger_reason': f'dependency_completed:{completed_spec_id}'
                })
```

## Progress Monitoring

### Implementation Progress Tracking
```python
@hook.on('agent-task-completed')
def track_implementation_progress(agent: str, task: str, spec_id: str):
    """Track progress of specification implementation."""
    
    # Calculate completion percentage
    progress = calculate_spec_progress(spec_id)
    
    # Update specification metadata
    update_spec_progress(spec_id, progress)
    
    # Notify stakeholders of progress
    if progress in [25, 50, 75]:  # Progress percentages
        notify_progress_update(spec_id, progress)

def calculate_spec_progress(spec_id: str) -> float:
    """Calculate implementation progress percentage."""
    spec = load_specification(spec_id)
    
    # Check implementation components
    components_done = 0
    total_components = 0
    
    # Code implementation
    if spec.requires_code:
        total_components += 1
        if implementation_exists(spec_id):
            components_done += 1
    
    # Tests
    if spec.requires_tests:
        total_components += 1
        if tests_exist(spec_id):
            components_done += 1
    
    # Documentation
    if spec.requires_docs:
        total_components += 1
        if documentation_exists(spec_id):
            components_done += 1
    
    # Acceptance criteria validation
    total_components += len(spec.acceptance_criteria)
    components_done += count_satisfied_criteria(spec_id)
    
    return (components_done / total_components) * 100 if total_components > 0 else 0
```

### Quality Gate Integration
```python
@hook.on('spec-implementation-completed')
def quality_gate_validation(spec_id: str):
    """Validate specification meets quality gates before marking complete."""
    
    quality_checks = [
        check_test_coverage(spec_id),
        check_code_quality(spec_id),
        check_security_compliance(spec_id),
        check_performance_requirements(spec_id),
        validate_acceptance_criteria(spec_id)
    ]
    
    failed_checks = [check for check in quality_checks if not check.passed]
    
    if failed_checks:
        # Mark specification as needs revision
        mark_spec_status(spec_id, 'needs_revision')
        
        # Create improvement tasks
        for check in failed_checks:
            create_improvement_task(spec_id, check)
        
        logger.warning(f"❌ Quality gate failed for {spec_id}: {failed_checks}")
        
        # Notify about quality issues
        hook.trigger('spec-quality-gate-failed', {
            'spec_id': spec_id,
            'failed_checks': failed_checks
        })
    else:
        # Mark specification as completed
        mark_spec_status(spec_id, 'completed')
        
        logger.info(f"✅ Quality gate passed for {spec_id}")
        
        # Trigger completion hooks
        hook.trigger('spec-completed', {
            'spec_id': spec_id,
            'completion_time': datetime.now()
        })
```

## Validation Hooks

### Specification Validation
```python
@hook.on('spec-created')
def validate_new_specification(spec_id: str, spec_data: dict):
    """Validate new specifications meet standards."""
    
    validation_errors = []
    
    # Required fields validation
    required_fields = ['title', 'description', 'acceptance_criteria']
    for field in required_fields:
        if not spec_data.get(field):
            validation_errors.append(f"Missing required field: {field}")
    
    # Acceptance criteria validation
    criteria = spec_data.get('acceptance_criteria', [])
    if len(criteria) < 1:
        validation_errors.append("At least one acceptance criterion required")
    
    # Dependency validation
    dependencies = spec_data.get('dependencies', [])
    for dep_id in dependencies:
        if not specification_exists(dep_id):
            validation_errors.append(f"Invalid dependency: {dep_id}")
    
    # Complexity validation
    complexity = spec_data.get('complexity', 'medium')
    if complexity not in ['simple', 'medium', 'complex']:
        validation_errors.append(f"Invalid complexity level: {complexity}")
    
    if validation_errors:
        logger.error(f"❌ Specification validation failed for {spec_id}")
        for error in validation_errors:
            logger.error(f"  - {error}")
        
        # Mark specification as invalid
        mark_spec_status(spec_id, 'invalid')
        
        # Notify about validation failure
        hook.trigger('spec-validation-failed', {
            'spec_id': spec_id,
            'errors': validation_errors
        })
    else:
        logger.info(f"✅ Specification validated: {spec_id}")
        mark_spec_status(spec_id, 'draft')
```

### Dependency Validation
```python
@hook.on('spec-approved')
def validate_dependencies_ready(spec_id: str):
    """Ensure all dependencies are completed before starting implementation."""
    
    spec = load_specification(spec_id)
    dependencies = spec.get('dependencies', [])
    
    unmet_dependencies = []
    for dep_id in dependencies:
        dep_spec = load_specification(dep_id)
        if dep_spec.status != 'completed':
            unmet_dependencies.append(dep_id)
    
    if unmet_dependencies:
        # Block specification until dependencies complete
        mark_spec_status(spec_id, 'blocked')
        update_spec_metadata(spec_id, {
            'blocked_by': unmet_dependencies,
            'blocked_at': datetime.now().isoformat()
        })
        
        logger.warning(f"🚫 Specification {spec_id} blocked by: {unmet_dependencies}")
        
        # Notify about blocking
        hook.trigger('spec-blocked', {
            'spec_id': spec_id,
            'blocked_by': unmet_dependencies
        })
    else:
        # All dependencies met, ready for implementation
        mark_spec_status(spec_id, 'ready')
        
        logger.info(f"🚀 Specification {spec_id} ready for implementation")
        
        # Trigger implementation readiness
        hook.trigger('spec-ready-for-implementation', {
            'spec_id': spec_id
        })
```

## Integration Hooks

### External Tool Integration
```python
@hook.on('spec-created')
def integrate_with_external_tools(spec_id: str, spec_data: dict):
    """Integrate new specifications with external project management tools."""
    
    # Create Jira ticket
    if config.get('integrations.jira.enabled'):
        jira_ticket = create_jira_ticket(spec_data)
        update_spec_metadata(spec_id, {'jira_ticket': jira_ticket.key})
    
    # Create GitHub issue
    if config.get('integrations.github.enabled'):
        github_issue = create_github_issue(spec_data)
        update_spec_metadata(spec_id, {'github_issue': github_issue.number})
    
    # Add to project board
    if config.get('integrations.project_board.enabled'):
        add_to_project_board(spec_id, spec_data, column='Backlog')

@hook.on('spec-completed')
def update_external_tools_completion(spec_id: str, completion_data: dict):
    """Update external tools when specification is completed."""
    
    spec = load_specification(spec_id)
    
    # Close Jira ticket
    if spec.metadata.get('jira_ticket'):
        close_jira_ticket(spec.metadata['jira_ticket'])
    
    # Close GitHub issue
    if spec.metadata.get('github_issue'):
        close_github_issue(spec.metadata['github_issue'])
    
    # Move project board card
    if config.get('integrations.project_board.enabled'):
        move_project_board_card(spec_id, 'Done')
```

### Notification Integration
```python
@hook.on(['spec-completed', 'spec-blocked', 'spec-approved'])
def send_notifications(event: str, spec_id: str, data: dict):
    """Send notifications for important specification events."""
    
    spec = load_specification(spec_id)
    
    # Slack notification
    if config.get('notifications.slack.enabled'):
        send_slack_notification(event, spec, data)
    
    # Email notification
    if config.get('notifications.email.enabled'):
        send_email_notification(event, spec, data)
    
    # Discord notification
    if config.get('notifications.discord.enabled'):
        send_discord_notification(event, spec, data)

def send_slack_notification(event: str, spec: dict, data: dict):
    """Send Slack notification for specification events."""
    
    emoji_map = {
        'spec-completed': '✅',
        'spec-blocked': '🚫',
        'spec-approved': '👍',
        'spec-created': '📋'
    }
    
    message = {
        'text': f"{emoji_map.get(event, '📋')} **{event.replace('-', ' ').title()}**",
        'attachments': [{
            'color': 'good' if 'completed' in event else 'warning' if 'blocked' in event else 'normal',
            'fields': [
                {'title': 'Specification', 'value': spec['title'], 'short': True},
                {'title': 'ID', 'value': spec['id'], 'short': True},
                {'title': 'Priority', 'value': spec.get('priority', 'medium'), 'short': True},
                {'title': 'Assignee', 'value': spec.get('assignee', 'unassigned'), 'short': True}
            ]
        }]
    }
    
    # Add event-specific fields
    if event == 'spec-completed':
        message['attachments'][0]['fields'].append({
            'title': 'Completion Time',
            'value': data.get('completion_time', 'now'),
            'short': True
        })
    elif event == 'spec-blocked':
        message['attachments'][0]['fields'].append({
            'title': 'Blocked By',
            'value': ', '.join(data.get('blocked_by', [])),
            'short': False
        })
    
    send_to_slack(message)
```

## Analytics and Reporting

### Specification Metrics
```python
@hook.on('*')  # Listen to all specification events
def collect_specification_metrics(event: str, spec_id: str, data: dict):
    """Collect metrics for specification analytics."""
    
    metrics = {
        'event': event,
        'spec_id': spec_id,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    # Store in time-series database
    store_metrics(metrics)
    
    # Update real-time dashboard
    update_dashboard_metrics(metrics)

def generate_specification_report():
    """Generate periodic specification progress report."""
    
    # Collect metrics
    specs_created_this_week = count_specs_by_timeframe('created', days=7)
    specs_completed_this_week = count_specs_by_timeframe('completed', days=7)
    average_completion_time = calculate_average_completion_time()
    blocked_specs = get_blocked_specifications()
    
    # Generate report
    report = {
        'period': 'weekly',
        'created': specs_created_this_week,
        'completed': specs_completed_this_week,
        'avg_completion_time_hours': average_completion_time,
        'blocked_count': len(blocked_specs),
        'blocked_specs': blocked_specs,
        'completion_rate': specs_completed_this_week / max(specs_created_this_week, 1)
    }
    
    # Send report to stakeholders
    send_progress_report(report)
```

## Configuration

### Specification Tracking Configuration
```json
{
  "specification_tracking": {
    "enabled": true,
    "auto_progress_updates": true,
    "quality_gates": {
      "test_coverage_threshold": 80,
      "code_quality_threshold": 8.0,
      "security_scan": true
    },
    "notifications": {
      "on_completion": true,
      "on_blocking": true,
      "on_progress_updates": true
    },
    "integrations": {
      "jira": {
        "enabled": true,
        "auto_create_tickets": true,
        "project_key": "DEV"
      },
      "github": {
        "enabled": true,
        "auto_create_issues": false
      },
      "slack": {
        "enabled": true,
        "channel": "#development",
        "events": ["spec-completed", "spec-blocked"]
      }
    }
  }
}
```

### Event Filtering
```python
# Filter events by specification type
@hook.on('spec-completed')
@hook.filter(lambda spec_id, data: data.get('type') == 'feature')
def handle_feature_completion(spec_id: str, data: dict):
    """Handle completion of feature specifications only."""
    pass

# Filter events by priority
@hook.on('spec-blocked')
@hook.filter(lambda spec_id, data: data.get('priority') in ['high', 'critical'])
def handle_high_priority_blocking(spec_id: str, data: dict):
    """Handle blocking of high-priority specifications."""
    escalate_blocking_issue(spec_id, data)
```

## Best Practices

### 1. Efficient Event Handling
```python
# Good: Async processing for non-critical updates
@hook.on('spec-completed')
async def update_metrics_async(spec_id: str, data: dict):
    await async_update_metrics(spec_id, data)

# Avoid: Blocking operations in critical path
@hook.on('spec-completed')
def slow_processing(spec_id: str, data: dict):
    send_email_synchronously()  # Blocks specification completion
```

### 2. Error Resilience
```python
@hook.on('spec-completed')
def resilient_completion_handler(spec_id: str, data: dict):
    try:
        update_external_systems(spec_id, data)
    except ExternalSystemError as e:
        logger.warning(f"External system update failed: {e}")
        # Queue for retry instead of failing
        queue_for_retry(spec_id, 'external_update', data)
```

### 3. Idempotent Operations
```python
@hook.on('spec-completed')
def idempotent_pr_creation(spec_id: str, data: dict):
    # Check if PR already exists
    if not pr_exists_for_spec(spec_id):
        create_pull_request(spec_id, data)
    else:
        logger.info(f"PR already exists for {spec_id}")
```

## Next Steps

- Learn about [Specification Workflow](../specs/workflow.md)
- Explore [Custom Hook Development](custom.md)
- Understand [Agent Collaboration](../agents/overview.md)
- Read about [Specification-Driven Development](../specs/overview.md)