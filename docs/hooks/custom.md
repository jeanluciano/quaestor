# Custom Hooks

Custom hooks allow you to extend Quaestor's automation capabilities with project-specific logic, integrations, and workflows. You can create hooks that execute at specific points in your development process to automate repetitive tasks and enforce project standards.

## Overview

Custom hooks enable:
- **Project-Specific Automation**: Automate tasks unique to your project or team
- **External Integrations**: Connect with tools like Slack, Jira, GitHub, or custom APIs
- **Quality Enforcement**: Implement custom validation and compliance checks
- **Workflow Orchestration**: Coordinate complex multi-step processes
- **Notification Systems**: Keep team members informed of important events

## Hook Types

### Event-Based Hooks
Execute in response to specific development events:

```python
# .quaestor/hooks/custom_notifications.py
from quaestor.hooks import hook

@hook.on('spec-completed')
def notify_team_on_completion(spec_id: str, completion_data: dict):
    """Send team notification when specification is completed."""
    spec = load_specification(spec_id)
    
    # Send Slack notification
    send_slack_message(
        channel="#development",
        message=f"🎉 Specification completed: {spec['title']}",
        details={
            "spec_id": spec_id,
            "completed_by": completion_data.get("completed_by"),
            "branch": completion_data.get("branch"),
            "pr_url": completion_data.get("pr_url")
        }
    )
    
    # Update project dashboard
    update_project_dashboard(spec_id, "completed")
    
    # Check if milestone should be promoted
    if should_create_release(spec_id):
        trigger_release_process(spec_id)
```

### Scheduled Hooks
Execute on time-based schedules:

```python
# .quaestor/hooks/daily_reports.py
from quaestor.hooks import scheduled_hook
from datetime import datetime, timedelta

@scheduled_hook(cron="0 9 * * 1-5")  # 9 AM weekdays
def generate_daily_standup_report():
    """Generate daily development progress report."""
    
    yesterday = datetime.now() - timedelta(days=1)
    
    # Gather progress data
    completed_specs = get_specs_completed_since(yesterday)
    active_specs = get_active_specifications()
    blocked_specs = get_blocked_specifications()
    
    # Generate report
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "completed": len(completed_specs),
        "active": len(active_specs), 
        "blocked": len(blocked_specs),
        "details": {
            "completed_specs": [spec["title"] for spec in completed_specs],
            "blocked_specs": [
                {"title": spec["title"], "blocked_by": spec["blocked_by"]} 
                for spec in blocked_specs
            ]
        }
    }
    
    # Send to team channels
    send_standup_report(report)
```

### Conditional Hooks
Execute based on specific conditions:

```python
# .quaestor/hooks/security_alerts.py
from quaestor.hooks import hook

@hook.on('spec-completed')
@hook.when(lambda spec_id, data: is_security_critical(spec_id))
def security_spec_completed(spec_id: str, completion_data: dict):
    """Handle completion of security-critical specifications."""
    
    # Require additional security review
    request_security_review(spec_id)
    
    # Run automated security tests
    run_security_test_suite(spec_id)
    
    # Notify security team
    notify_security_team(spec_id, completion_data)
    
    # Schedule penetration testing
    schedule_penetration_test(spec_id)

def is_security_critical(spec_id: str) -> bool:
    """Check if specification involves security-critical functionality."""
    spec = load_specification(spec_id)
    security_keywords = ["auth", "login", "password", "token", "crypto", "payment"]
    
    return any(keyword in spec["title"].lower() or 
              keyword in spec["description"].lower() 
              for keyword in security_keywords)
```

## Hook Development

### Basic Hook Structure

```python
# .quaestor/hooks/my_custom_hook.py
from quaestor.hooks import hook
import logging

logger = logging.getLogger(__name__)

@hook.on('spec-created')
def handle_new_specification(spec_id: str, spec_data: dict):
    """Custom logic when a new specification is created."""
    
    try:
        # Your custom logic here
        logger.info(f"Processing new specification: {spec_id}")
        
        # Example: Auto-assign based on spec type
        if spec_data.get("type") == "frontend":
            assign_to_frontend_team(spec_id)
        elif spec_data.get("type") == "backend":
            assign_to_backend_team(spec_id)
        
        # Example: Create related resources
        create_git_branch(spec_id)
        create_project_board_card(spec_id, spec_data)
        
    except Exception as e:
        logger.error(f"Error processing specification {spec_id}: {e}")
        # Don't fail the entire workflow for non-critical errors
```

### Hook Configuration

```yaml
# .quaestor/hooks/config.yaml
hooks:
  custom_notifications:
    enabled: true
    events: ["spec-completed", "spec-blocked"]
    config:
      slack_webhook: "${SLACK_WEBHOOK_URL}"
      channels:
        default: "#development"
        urgent: "#alerts"
  
  daily_reports:
    enabled: true
    schedule: "0 9 * * 1-5"
    config:
      recipients: ["team@company.com"]
      dashboard_url: "https://dashboard.company.com"
  
  security_alerts:
    enabled: true
    events: ["spec-completed"]
    config:
      security_team: ["security@company.com"]
      auto_testing: true
```

### Environment Configuration

```bash
# .env file for hook configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
JIRA_API_TOKEN=your_jira_token
GITHUB_TOKEN=your_github_token
DASHBOARD_API_KEY=your_dashboard_key
```

## Common Hook Patterns

### Team Notification Hooks

```python
# .quaestor/hooks/team_notifications.py
@hook.on(['spec-completed', 'spec-blocked', 'spec-approved'])
def send_team_notifications(event: str, spec_id: str, data: dict):
    """Send appropriate notifications based on event type."""
    
    spec = load_specification(spec_id)
    
    notification_config = {
        'spec-completed': {
            'emoji': '🎉',
            'channel': '#development',
            'template': 'spec_completed.md'
        },
        'spec-blocked': {
            'emoji': '🚫', 
            'channel': '#alerts',
            'template': 'spec_blocked.md'
        },
        'spec-approved': {
            'emoji': '✅',
            'channel': '#development', 
            'template': 'spec_approved.md'
        }
    }
    
    config = notification_config[event]
    message = render_template(
        config['template'],
        spec=spec,
        event=event,
        data=data
    )
    
    send_slack_notification(
        channel=config['channel'],
        message=f"{config['emoji']} {message}"
    )
```

### External Tool Integration

```python
# .quaestor/hooks/jira_integration.py
from jira import JIRA

@hook.on('spec-created')
def create_jira_ticket(spec_id: str, spec_data: dict):
    """Create corresponding JIRA ticket for new specifications."""
    
    jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_TOKEN))
    
    # Create JIRA ticket
    issue_data = {
        'project': {'key': 'DEV'},
        'summary': spec_data['title'],
        'description': spec_data['description'],
        'issuetype': {'name': 'Story'},
        'priority': {'name': map_priority(spec_data.get('priority', 'medium'))},
        'customfield_10001': spec_id  # Link back to specification
    }
    
    issue = jira.create_issue(fields=issue_data)
    
    # Update specification with JIRA link
    update_spec_metadata(spec_id, {
        'jira_ticket': issue.key,
        'jira_url': f"{JIRA_SERVER}/browse/{issue.key}"
    })
    
    logger.info(f"Created JIRA ticket {issue.key} for specification {spec_id}")

@hook.on('spec-completed')
def close_jira_ticket(spec_id: str, completion_data: dict):
    """Close JIRA ticket when specification is completed."""
    
    spec = load_specification(spec_id)
    jira_ticket = spec.get('metadata', {}).get('jira_ticket')
    
    if jira_ticket:
        jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_TOKEN))
        
        # Transition ticket to "Done"
        jira.transition_issue(jira_ticket, transition='Done')
        
        # Add completion comment
        jira.add_comment(
            jira_ticket,
            f"Specification completed and merged in branch: {completion_data.get('branch')}"
        )
```

### Quality Gate Hooks

```python
# .quaestor/hooks/quality_gates.py
@hook.on('spec-implementation-completed')
def quality_gate_validation(spec_id: str, implementation_data: dict):
    """Validate specification meets quality gates before marking complete."""
    
    quality_results = []
    
    # Test coverage check
    coverage = get_test_coverage(spec_id)
    if coverage < 80:
        quality_results.append({
            'type': 'test_coverage',
            'status': 'failed',
            'actual': coverage,
            'required': 80,
            'message': f"Test coverage {coverage}% below required 80%"
        })
    
    # Security scan
    security_issues = run_security_scan(spec_id)
    if security_issues['critical'] > 0:
        quality_results.append({
            'type': 'security_scan',
            'status': 'failed',
            'critical_issues': security_issues['critical'],
            'message': f"Found {security_issues['critical']} critical security issues"
        })
    
    # Performance benchmarks
    performance_results = run_performance_tests(spec_id)
    if performance_results['avg_response_time'] > 200:
        quality_results.append({
            'type': 'performance',
            'status': 'failed', 
            'actual': performance_results['avg_response_time'],
            'required': 200,
            'message': f"Average response time {performance_results['avg_response_time']}ms exceeds 200ms limit"
        })
    
    # Process results
    if any(result['status'] == 'failed' for result in quality_results):
        # Mark specification as needs revision
        update_spec_status(spec_id, 'needs_revision')
        
        # Create improvement tasks
        for result in quality_results:
            if result['status'] == 'failed':
                create_improvement_task(spec_id, result)
        
        # Notify team of quality gate failure
        notify_quality_gate_failure(spec_id, quality_results)
        
    else:
        # Mark specification as completed
        update_spec_status(spec_id, 'completed')
        
        # Trigger completion hooks
        hook.trigger('spec-completed', {
            'spec_id': spec_id,
            'quality_results': quality_results
        })
```

### Deployment Automation

```python
# .quaestor/hooks/deployment_automation.py
@hook.on('spec-group-completed')
def trigger_deployment_pipeline(spec_group_id: str, completion_data: dict):
    """Trigger deployment when a group of related specifications is completed."""
    
    spec_group = load_specification_group(spec_group_id)
    
    # Check if this is a releasable group
    if spec_group.get('deployment_trigger', False):
        
        # Create release branch
        release_branch = f"release/{spec_group['version']}"
        create_git_branch(release_branch)
        
        # Run pre-deployment tests
        test_results = run_integration_tests(spec_group_id)
        if not test_results['passed']:
            notify_deployment_failure(spec_group_id, test_results)
            return
        
        # Build deployment artifacts
        build_artifacts(spec_group['version'])
        
        # Deploy to staging
        deploy_to_staging(spec_group['version'])
        
        # Run smoke tests
        smoke_test_results = run_smoke_tests()
        if smoke_test_results['passed']:
            # Notify ready for production
            notify_ready_for_production(spec_group_id, spec_group['version'])
        else:
            notify_staging_issues(spec_group_id, smoke_test_results)
```

## Hook Testing

### Unit Testing Hooks

```python
# tests/test_custom_hooks.py
import pytest
from unittest.mock import Mock, patch
from quaestor.hooks.custom_notifications import notify_team_on_completion

def test_notify_team_on_completion():
    """Test team notification hook functionality."""
    
    # Mock dependencies
    with patch('quaestor.hooks.custom_notifications.send_slack_message') as mock_slack, \
         patch('quaestor.hooks.custom_notifications.load_specification') as mock_load:
        
        # Setup test data
        mock_load.return_value = {
            'title': 'User Authentication System',
            'type': 'feature'
        }
        
        completion_data = {
            'completed_by': 'john.doe',
            'branch': 'feature/auth-system',
            'pr_url': 'https://github.com/company/repo/pull/123'
        }
        
        # Execute hook
        notify_team_on_completion('spec-auth-001', completion_data)
        
        # Verify Slack notification was sent
        mock_slack.assert_called_once()
        call_args = mock_slack.call_args
        
        assert call_args[1]['channel'] == '#development'
        assert 'User Authentication System' in call_args[1]['message']
        assert call_args[1]['details']['spec_id'] == 'spec-auth-001'
```

### Integration Testing

```python
# tests/test_hook_integration.py
import pytest
from quaestor.hooks import trigger_hook

def test_spec_completion_hook_chain():
    """Test complete hook chain when specification is completed."""
    
    with patch_multiple_hooks() as mocks:
        # Trigger spec completion
        trigger_hook('spec-completed', {
            'spec_id': 'spec-test-001',
            'completion_data': {'completed_by': 'test_user'}
        })
        
        # Verify all expected hooks were called
        assert mocks['team_notification'].called
        assert mocks['jira_integration'].called  
        assert mocks['quality_gate'].called
        assert mocks['deployment_check'].called
```

## Best Practices

### 1. Keep Hooks Lightweight
```python
# Good: Fast, non-blocking hook
@hook.on('spec-completed')
def quick_notification(spec_id):
    # Use background task for heavy operations
    background_task.delay(process_completion, spec_id)

# Avoid: Heavy, blocking operations
@hook.on('spec-completed') 
def slow_processing(spec_id):
    # This blocks the entire workflow
    generate_comprehensive_report(spec_id)  # Takes 30 seconds
```

### 2. Handle Errors Gracefully
```python
@hook.on('spec-completed')
def resilient_hook(spec_id: str, data: dict):
    try:
        # Main hook logic
        process_specification_completion(spec_id, data)
    except ExternalServiceError as e:
        # Log error but don't fail workflow
        logger.warning(f"External service unavailable: {e}")
        # Queue for retry
        retry_queue.add(spec_id, 'completion_processing')
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in completion hook: {e}")
        # Continue workflow execution
```

### 3. Use Configuration for Flexibility
```python 
# Make hooks configurable
@hook.on('spec-completed')
def configurable_notification(spec_id: str, data: dict):
    config = get_hook_config('notifications')
    
    if config.get('slack_enabled', False):
        send_slack_notification(spec_id, data)
    
    if config.get('email_enabled', False):
        send_email_notification(spec_id, data)
    
    if config.get('dashboard_enabled', False):
        update_dashboard(spec_id, data)
```

### 4. Document Hook Behavior
```python
@hook.on('spec-completed')
def document_hook_example(spec_id: str, completion_data: dict):
    """
    Handle specification completion with team notifications and quality checks.
    
    Args:
        spec_id: Unique identifier for the completed specification
        completion_data: Dictionary containing completion metadata
            - completed_by: Username of the person who completed the spec
            - branch: Git branch containing the implementation
            - pr_url: URL of the associated pull request
            - completion_time: ISO timestamp of completion
    
    Side Effects:
        - Sends Slack notification to #development channel
        - Updates project dashboard with completion status
        - Triggers quality gate validation
        - Creates JIRA ticket transition if configured
        
    Configuration:
        - SLACK_WEBHOOK_URL: Required for Slack notifications
        - JIRA_ENABLED: Set to true to enable JIRA integration
        - QUALITY_GATES_ENABLED: Set to true to run quality validation
    
    Raises:
        - Does not raise exceptions; errors are logged and workflows continue
    """
```

## Debugging Hooks

### Hook Execution Logging
```python
# Enable detailed hook logging
import logging

logging.getLogger('quaestor.hooks').setLevel(logging.DEBUG)

@hook.on('spec-completed')
def debug_example_hook(spec_id: str, data: dict):
    logger = logging.getLogger(__name__)
    logger.debug(f"Hook triggered for spec {spec_id} with data: {data}")
    
    try:
        # Hook logic
        result = process_specification(spec_id, data)
        logger.debug(f"Hook completed successfully: {result}")
    except Exception as e:
        logger.error(f"Hook failed: {e}", exc_info=True)
        raise
```

### Hook Testing and Validation
```bash
# Test specific hooks
quaestor hooks test custom_notifications --spec-id=test-001

# Validate hook configuration
quaestor hooks validate

# Monitor hook execution
quaestor hooks monitor --tail -f
```

## Next Steps

- Learn about [Specification Tracking](spec-tracking.md) for built-in hook patterns
- Explore [Hook System Overview](overview.md) for core concepts
- Understand [Agent Integration](../agents/overview.md) for agent-hook coordination
- Read about [External Integrations](../advanced/integrations.md) for connecting with external tools