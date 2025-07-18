---
allowed-tools: [Read, Grep, Glob, Bash, TodoWrite, Task]
description: "Multi-dimensional code analysis with intelligent tool selection"
performance-profile: "complex"
complexity-threshold: 0.8
auto-activation: ["systematic-analysis", "evidence-gathering", "tool-orchestration"]
intelligence-features: ["domain-detection", "parallel-analysis", "priority-scoring"]
---

# /analyze - Intelligent Code Analysis

## Purpose
Execute comprehensive code analysis across quality, security, performance, and architecture domains with intelligent tool orchestration and evidence-based insights.

## Usage
```
/analyze [target] [--focus quality|security|performance|architecture|all]
/analyze [files|modules|system] [--depth quick|deep|comprehensive]
```

**Differentiation from /status:**
- **status**: Project progress, milestones, completion tracking
- **analyze**: Code quality, technical debt, architectural insights, performance bottlenecks

## Auto-Intelligence

### Domain Detection & Tool Selection
```yaml
Auto-Detection:
  - Scope: files|modules|system → tool strategy
  - Language: Python|Rust|JS → specific analysis patterns  
  - Focus: keywords → quality|security|performance|architecture
  - Complexity: assess → Agent delegation strategy
```

### Intelligent Tool Orchestration
- **<10 files** → Direct Read + Grep analysis
- **10-50 files** → Parallel Agent coordination  
- **>50 files** → Systematic Agent delegation
- **System-wide** → Multi-domain Agent specialization

## Execution: Discover → Analyze → Prioritize → Report

### Phase 1: Scope Discovery 🔍
**Target Assessment:**
```yaml
File Discovery:
  - Auto-detect: project structure & complexity
  - Categorize: core|tests|docs|config
  - Prioritize: critical paths & dependencies
  - Strategy: direct|parallel|systematic analysis
```

### Phase 2: Multi-Domain Analysis ⚡

**Parallel Analysis Strategy:**
```yaml
Agent Specialization:
  - quality_agent: Technical debt, maintainability, patterns
  - security_agent: Vulnerabilities, compliance, threats  
  - performance_agent: Bottlenecks, optimizations, scaling
  - architecture_agent: Structure, dependencies, design
```

**Intelligence Patterns:**
- **Quality Focus** → Code complexity, maintainability index, test coverage
- **Security Focus** → Vulnerability scanning, input validation, auth patterns
- **Performance Focus** → Algorithm complexity, resource usage, bottlenecks
- **Architecture Focus** → Dependency analysis, pattern compliance, modularity

### Phase 3: Evidence Gathering & Prioritization 📊

**Analysis Framework:**
```yaml
Code Quality Metrics:
  - Complexity: cyclomatic, cognitive, nesting depth
  - Maintainability: readability, documentation, consistency
  - Technical Debt: TODO/FIXME count, deprecated usage
  - Test Coverage: unit, integration, e2e coverage %

Security Assessment:
  - Vulnerability Scan: known CVEs, security patterns  
  - Input Validation: sanitization, escaping, validation
  - Authentication: auth flows, session management
  - Data Protection: encryption, secrets management

Performance Analysis:
  - Algorithm Efficiency: O(n) complexity analysis
  - Resource Usage: memory, CPU, I/O patterns
  - Bottleneck Detection: slow queries, heavy operations
  - Scaling Patterns: caching, concurrency, optimization

Architecture Review:
  - Dependency Analysis: coupling, cohesion, circular deps
  - Pattern Compliance: SOLID, design patterns, conventions
  - Modularity: separation of concerns, boundaries
  - Evolution: extensibility, maintainability, flexibility
```

### Phase 4: Insights & Recommendations 💡

**Priority Scoring Matrix:**
```yaml
Critical (P0): Security vulnerabilities, system failures
High (P1): Performance bottlenecks, major technical debt  
Medium (P2): Code quality issues, minor optimizations
Low (P3): Style inconsistencies, documentation gaps
```

**Evidence-Based Reporting:**
- **Findings**: Specific issues with file:line references
- **Impact**: Business/technical impact assessment  
- **Recommendations**: Actionable improvement suggestions
- **Metrics**: Quantified evidence and success criteria

## Analysis Modes

### Quick Analysis (~5min)
- Surface-level quality scan
- Basic security check
- Performance hotspot identification
- High-level architecture overview

### Deep Analysis (~15min)
- Comprehensive code quality assessment
- Detailed security vulnerability scan  
- Performance profiling and optimization opportunities
- Architecture pattern analysis and recommendations

### Comprehensive Analysis (~30min)
- Full-system quality audit
- Enterprise security assessment
- Performance benchmarking and scaling analysis
- Complete architecture review and modernization roadmap

## Language-Specific Analysis

### Python Analysis
```yaml
Quality:
  - Complexity: radon, mccabe analysis
  - Style: ruff compliance, PEP 8 adherence
  - Types: mypy coverage, annotation quality
Security:
  - Vulnerabilities: bandit security scan
  - Dependencies: safety check, known CVEs
Performance:
  - Profiling: cProfile hotspots, memory usage
  - Optimization: algorithm efficiency, pandas usage
```

### Rust Analysis  
```yaml
Quality:
  - Clippy: lint analysis, best practices
  - Documentation: rustdoc coverage, examples
  - Testing: test coverage, benchmark presence
Security:
  - Unsafe: unsafe block audit, justification
  - Dependencies: cargo audit, vulnerability scan
Performance:
  - Profiling: criterion benchmarks, flamegraph
  - Memory: allocation patterns, zero-copy opportunities
```

### JavaScript/TypeScript Analysis
```yaml
Quality:
  - ESLint: rule compliance, best practices
  - TypeScript: type coverage, strict mode usage
  - Testing: Jest coverage, test quality
Security:
  - Dependencies: npm audit, known vulnerabilities
  - XSS/CSRF: input sanitization, security headers
Performance:
  - Bundle: webpack-bundle-analyzer, size optimization
  - Runtime: Chrome DevTools insights, Core Web Vitals
```

## Success Criteria

**Analysis Completeness:**
- ✅ All target files/modules examined
- ✅ Evidence gathered with quantified metrics
- ✅ Priority-scored recommendations provided
- ✅ Actionable next steps identified

**Intelligence Quality:**
- ✅ Domain-appropriate analysis depth
- ✅ Tool selection optimized for target scope
- ✅ Parallel execution for efficiency
- ✅ Evidence-based insights with clear rationale

## Example Output Structure
```
🔍 Analysis Report: [Target Scope]

📊 Summary:
- Quality Score: 85/100 (Good)
- Security Score: 92/100 (Excellent)  
- Performance Score: 73/100 (Needs Attention)
- Architecture Score: 88/100 (Good)

⚠️ Critical Issues (P0): 0
🔴 High Priority (P1): 3
🟡 Medium Priority (P2): 12  
🟢 Low Priority (P3): 8

🎯 Top Recommendations:
1. [P1] Optimize database queries in user.py:45-67 (45% performance impact)
2. [P1] Fix input validation in auth.py:123 (security vulnerability)
3. [P1] Reduce cyclomatic complexity in processor.py:89-156 (maintainability)

📈 Metrics & Evidence: [Detailed findings with file:line references]
```

---
*Systematic code analysis with evidence-based insights for continuous improvement*