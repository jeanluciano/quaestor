# Hooks Overview

Quaestor's hook system provides automated triggers that execute at specific points in your development workflow. Hooks enable automation, progress tracking, compliance enforcement, and seamless integration with external tools.

## What are Hooks?

Hooks are scripts or commands that execute automatically when specific events occur:

- **Git Events**: Commits, pushes, branch changes
- **Specification Events**: Creation, updates, completion
- **Development Events**: Tests running, builds completing
- **Agent Events**: Task completion, collaboration points
- **Custom Events**: User-defined triggers

## Built-in Hooks

### 🎯 Specification Tracking
Automatically tracks specification progress and lifecycle:

```python
# .quaestor/hooks/spec_tracker.py
def on_specification_complete(spec_id: str):
    """Triggered when a specification is marked complete."""
    update_specification_progress(spec_id)
    notify_stakeholders(spec_id)
    create_pull_request_if_ready(spec_id)
```

### 📊 Progress Monitoring
Monitors development progress and updates dashboards:

```python
# .quaestor/hooks/progress_monitor.py
def on_agent_task_complete(agent: str, task: str):
    """Triggered when any agent completes a task."""
    log_progress_metrics(agent, task)
    update_project_dashboard()
    check_specification_completion()
```

### 🔍 Quality Gates
Enforces code quality standards automatically:

```python
# .quaestor/hooks/quality_gate.py
def on_pre_commit():
    """Triggered before every commit."""
    run_linting()
    check_test_coverage()
    scan_security_vulnerabilities()
    validate_documentation()
```

### 🚀 Deployment Automation
Manages deployment workflows:

```python
# .quaestor/hooks/deployment.py
def on_specification_group_complete(spec_group_id: str):
    """Triggered when a specification group is completed."""
    create_release_candidate()
    run_integration_tests()
    prepare_deployment_artifacts()
```

## Hook Types

### 1. Event-Driven Hooks
Execute in response to specific events:

#### Git Hooks
- `pre-commit`: Before committing changes
- `post-commit`: After successful commit
- `pre-push`: Before pushing to remote
- `post-merge`: After merging branches

#### Specification Hooks
- `spec-created`: New specification created
- `spec-updated`: Specification modified
- `spec-completed`: Specification implementation finished
- `spec-approved`: Specification approved for implementation

#### Agent Hooks
- `agent-started`: Agent begins task execution
- `agent-completed`: Agent finishes task
- `agent-failed`: Agent encounters error
- `collaboration-point`: Multiple agents coordinate

### 2. Scheduled Hooks
Execute on time-based schedules:

```yaml
# .quaestor/hooks/scheduled.yml
daily_health_check:
  schedule: "0 9 * * *"  # 9 AM daily
  command: "quaestor health --report"

weekly_architecture_review:
  schedule: "0 10 * * 1"  # 10 AM Mondays
  command: "quaestor review --type=architecture --report"
```

### 3. Conditional Hooks
Execute based on conditions:

```python
# .quaestor/hooks/conditional.py
@hook.when(lambda ctx: ctx.complexity_score > 0.8)
def on_high_complexity_implementation(context):
    """Execute when implementing complex features."""
    request_architecture_review()
    require_additional_testing()
    add_documentation_requirements()
```

## Hook Configuration

### Global Configuration
```json
{
  "hooks": {
    "enabled": true,
    "timeout": 30,
    "parallel_execution": false,
    "failure_handling": "warn",
    "log_level": "info"
  }
}
```

### Hook-Specific Configuration
```json
{
  "hooks": {
    "spec_tracker": {
      "enabled": true,
      "auto_pr_creation": true,
      "notification_channels": ["slack", "email"]
    },
    "quality_gate": {
      "coverage_threshold": 80,
      "complexity_threshold": 10,
      "security_scan": true
    }
  }
}
```

## Hook Implementation

### Python Hooks
```python
# .quaestor/hooks/custom_hook.py
from quaestor.hooks import hook

@hook.on('specification-complete')
def handle_spec_completion(spec_id: str, metadata: dict):
    """Handle specification completion."""
    print(f"Specification {spec_id} completed!")
    
    # Update project metrics
    update_completion_metrics(spec_id)
    
    # Notify team
    send_notification({
        'event': 'spec-complete',
        'spec_id': spec_id,
        'timestamp': metadata['completed_at']
    })
    
    # Check if specification group is complete
    if check_specification_group_completion(spec_id):
        trigger_spec_group_complete_hooks(spec_id)

@hook.on('agent-collaboration')
def coordinate_agents(agents: list, context: dict):
    """Coordinate multi-agent workflows."""
    print(f"Coordinating {len(agents)} agents: {', '.join(agents)}")
    
    # Ensure context is shared
    share_context_between_agents(agents, context)
    
    # Log collaboration point
    log_collaboration_event(agents, context)
```

### Shell Script Hooks
```bash
#!/bin/bash
# .quaestor/hooks/pre-commit.sh

echo "Running pre-commit quality checks..."

# Run linting
echo "🔍 Running linter..."
ruff check . || exit 1

# Run tests
echo "🧪 Running tests..."
pytest tests/ || exit 1

# Check test coverage
echo "📊 Checking coverage..."
coverage run -m pytest tests/
coverage report --fail-under=80 || exit 1

# Security scan
echo "🔒 Security scan..."
bandit -r src/ || exit 1

echo "✅ All quality checks passed!"
```

### YAML Configuration Hooks
```yaml
# .quaestor/hooks/notifications.yml
name: "Slack Notifications"
events:
  - spec-completed
  - spec-group-completed
  - deployment-ready

actions:
  - type: slack
    webhook: "${SLACK_WEBHOOK_URL}"
    channel: "#development"
    template: |
      🎉 *{{event}}*
      Specification: {{spec_id}}
      Completed by: {{agent}}
      Time: {{timestamp}}
```

## Common Hook Patterns

### 1. Progress Tracking
```python
@hook.on(['spec-created', 'spec-completed', 'spec-updated'])
def track_specification_progress(event: str, spec_id: str, data: dict):
    """Track all specification lifecycle events."""
    progress_db.record_event(
        event_type=event,
        spec_id=spec_id,
        timestamp=datetime.now(),
        metadata=data
    )
    
    # Update dashboard
    dashboard.refresh_spec_metrics()
```

### 2. Quality Assurance
```python
@hook.on('pre-commit')
def quality_gate():
    """Comprehensive quality gate."""
    checks = [
        run_linting(),
        run_tests(),
        check_coverage(),
        security_scan(),
        documentation_check()
    ]
    
    failures = [check for check in checks if not check.passed]
    
    if failures:
        print("❌ Quality gate failed:")
        for failure in failures:
            print(f"  - {failure.name}: {failure.message}")
        return False
    
    print("✅ Quality gate passed!")
    return True
```

### 3. Automated Documentation
```python
@hook.on('spec-completed')
def update_documentation(spec_id: str):
    """Automatically update project documentation."""
    spec = load_specification(spec_id)
    
    # Update API documentation
    if spec.type == 'api':
        generate_api_docs(spec)
    
    # Update architecture diagrams
    if spec.affects_architecture:
        update_architecture_diagrams()
    
    # Update user documentation
    if spec.user_facing:
        update_user_guide(spec)
```

### 4. Deployment Preparation
```python
@hook.on('spec-group-completed')
def prepare_deployment(spec_group_id: str):
    """Prepare deployment when specification group completes."""
    spec_group = load_specification_group(spec_group_id)
    
    # Create release branch
    create_release_branch(spec_group.version)
    
    # Run full test suite
    if not run_integration_tests():
        raise HookError("Integration tests failed")
    
    # Generate release notes
    generate_release_notes(spec_group)
    
    # Create deployment artifacts
    build_deployment_artifacts(spec_group.version)
```

## Hook Development

### Creating Custom Hooks

1. **Create Hook File**
```python
# .quaestor/hooks/my_custom_hook.py
from quaestor.hooks import hook

@hook.on('custom-event')
def my_handler(data):
    # Hook implementation
    pass
```

2. **Register Hook**
```json
{
  "hooks": {
    "custom_hooks": [
      ".quaestor/hooks/my_custom_hook.py"
    ]
  }
}
```

3. **Test Hook**
```bash
quaestor hooks test my_custom_hook --event custom-event
```

### Hook Best Practices

#### 1. Keep Hooks Fast
```python
# Good: Fast, non-blocking
@hook.on('spec-completed')
def quick_notification(spec_id):
    async_notify.delay(spec_id)  # Use background task

# Avoid: Slow, blocking operations
@hook.on('spec-completed')
def slow_notification(spec_id):
    send_email_synchronously(spec_id)  # Blocks workflow
```

#### 2. Handle Errors Gracefully
```python
@hook.on('agent-completed')
def update_metrics(agent, task):
    try:
        metrics_service.record(agent, task)
    except MetricsServiceError as e:
        logger.warning(f"Metrics update failed: {e}")
        # Don't fail the entire workflow
```

#### 3. Use Idempotent Operations
```python
@hook.on('spec-completed')
def create_pr_if_needed(spec_id):
    # Check if PR already exists
    if not pr_exists(spec_id):
        create_pull_request(spec_id)
```

## Hook Debugging

### Logging Hook Execution
```bash
# Enable hook debugging
quaestor config set hooks.debug true

# View hook logs
quaestor hooks logs --tail -f

# Test specific hooks
quaestor hooks test spec_tracker --spec feat-auth-001
```

### Hook Monitoring
```python
# Monitor hook performance
@hook.on('*')  # Listen to all events
def monitor_hook_performance(event, duration, success):
    metrics.record({
        'event': event,
        'duration_ms': duration,
        'success': success,
        'timestamp': datetime.now()
    })
```

## Integration Examples

### Slack Integration
```python
@hook.on(['spec-completed', 'spec-group-completed'])
def slack_notification(event, data):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    message = {
        'text': f"🎉 {event}: {data['title']}",
        'channel': '#development',
        'username': 'Quaestor'
    }
    requests.post(webhook_url, json=message)
```

### Jira Integration
```python
@hook.on('spec-created')
def create_jira_ticket(spec_id, spec_data):
    jira = JIRA(server=JIRA_SERVER, basic_auth=JIRA_AUTH)
    
    issue = jira.create_issue(
        project='DEV',
        summary=spec_data['title'],
        description=spec_data['description'],
        issuetype={'name': 'Story'},
        customfield_10001=spec_id  # Quaestor spec ID
    )
    
    # Link back to specification
    update_spec_metadata(spec_id, {'jira_ticket': issue.key})
```

### GitHub Integration
```python
@hook.on('spec-group-completed')
def create_github_release(spec_group_id, spec_group_data):
    github = Github(os.getenv('GITHUB_TOKEN'))
    repo = github.get_repo('org/project')
    
    # Create release
    release = repo.create_git_release(
        tag=spec_group_data['version'],
        name=f"Release {spec_group_data['version']}",
        message=generate_release_notes(spec_group_data),
        draft=False,
        prerelease=False
    )
    
    # Attach artifacts
    for artifact in spec_group_data['artifacts']:
        release.upload_asset(artifact)
```

## Next Steps

- Learn about [Specification Tracking](spec-tracking.md)
- Explore [Specification Workflow](../specs/workflow.md)
- Understand [Custom Hook Development](custom.md)
- Read about [Agent Collaboration](../agents/overview.md)