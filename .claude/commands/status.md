---
allowed-tools: [Read, LS, Grep, Bash]
description: "Intelligent project progress overview with visual indicators and actionable insights"
performance-profile: "standard"
complexity-threshold: 0.2
auto-activation: ["progress-visualization", "insight-generation", "next-action-detection"]
intelligence-features: ["milestone-analysis", "velocity-tracking", "bottleneck-detection"]
---

# /status - Intelligent Progress Overview

## Purpose
Analyze project progress with visual indicators, velocity tracking, and actionable insights for next steps.

## Usage
```
/status
/status --verbose
/status --milestone current
```

## Auto-Intelligence

### Progress Analysis
```yaml
Data Sources:
  - MEMORY.md → milestone tracking + task completion
  - Git history → commit velocity + activity patterns
  - Quality metrics → test coverage + lint status
  - Project health → dependencies + documentation
```

### Visual Indicators
- **Progress bars**: [████████░░] 80% with emoji status
- **Velocity tracking**: Commits/week, tasks/milestone trends
- **Bottleneck detection**: Stalled tasks, failing quality gates

## Execution: Scan → Analyze → Visualize → Recommend

### Phase 1: Data Collection 🔍
**Multi-Source Analysis:**
```yaml
Progress Data:
  - Current milestone status + completion %
  - Task breakdown: completed|in_progress|planned
  - Recent activity: commits, updates, changes
  
Quality Metrics:
  - Test coverage: % + trend
  - Linting status: ✅ clean | ⚠️ warnings | ❌ errors
  - Build health: last successful build
  
Velocity Tracking:
  - Commits per week: trend analysis
  - Tasks completed per milestone: average
  - Time to completion: milestone duration patterns
```

### Phase 2: Progress Visualization 📊
**Status Report Format:**
```
🎯 [Project Name] • [Current Phase]

📈 Progress: [████████░░] 80% • Velocity: +15% this week

✅ Completed (5): 
  • user authentication system (a1b2c3d)
  • payment processing integration (e4f5g6h)
  • responsive UI components (i7j8k9l)

🔄 In Progress (2):
  • API documentation → 60% complete
  • performance optimization → started 3d ago

📋 Planned (3):
  • deployment pipeline setup
  • monitoring & alerting
  • user feedback integration

⚡ Quality Dashboard:
  Tests: ✅ 87% coverage • Linting: ✅ clean • Build: ✅ passing

🎢 Velocity: 8 commits this week • 2.3 tasks/milestone avg

💡 Next Action: Complete API docs → ready for /milestone-pr
```

### Phase 3: Intelligent Insights 💡
**Smart Recommendations:**
```yaml
Bottleneck Detection:
  - Stalled tasks → suggest /task to continue
  - Failing tests → suggest /check to fix
  - Low velocity → identify blockers
  
Next Actions:
  - Milestone near completion → suggest /milestone-pr
  - Quality issues → prioritize /check fixes
  - Documentation gaps → highlight missing docs
  
Trend Analysis:
  - Velocity increasing → celebrate progress
  - Tasks accumulating → suggest focus areas
  - Quality declining → recommend cleanup
```

### Phase 4: Actionable Guidance 🚀
**Context-Aware Suggestions:**
```yaml
Action Triggers:
  Milestone 90%+ complete:
    → "🎉 Almost done! Run /milestone-pr when ready"
  
  Tests failing:
    → "⚠️ Quality gate failing. Run /check to fix issues"
  
  No activity 3+ days:
    → "📋 Ready to continue? Run /task for next steps"
  
  High velocity + clean quality:
    → "🚀 Great momentum! Consider next milestone planning"
```

## Verbose Mode Features

**Extended Analysis:**
- Detailed task breakdowns with time estimates
- Complete commit history with impact analysis
- Technical debt tracking and prioritization
- Performance metrics and benchmark comparisons
- Dependency health and security status

## Success Criteria

**Status Analysis:**
- ✅ All data sources scanned and analyzed
- ✅ Progress accurately calculated and visualized
- ✅ Quality metrics current and actionable
- ✅ Velocity trends identified and explained

**Intelligence Quality:**
- ✅ Bottlenecks detected with specific suggestions
- ✅ Next actions prioritized by impact
- ✅ Trends analyzed with context-aware insights
- ✅ Visual indicators clear and informative

---
*Intelligent progress tracking with actionable insights and visual velocity analysis*