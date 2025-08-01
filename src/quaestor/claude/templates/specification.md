---
spec_id: "{{ spec_id }}"
title: "{{ title }}"
type: "{{ type }}"  # feature|fix|enhancement|refactor
status: "{{ status }}"  # draft|approved|implementing|testing|complete
created: "{{ created_date }}"
author: "{{ author }}"
---

# Specification: {{ title }}

## Use Case Overview

**ID**: {{ spec_id }}  
**Primary Actor**: {{ primary_actor }}  
**Goal**: {{ goal }}  
**Priority**: {{ priority }}  # critical|high|medium|low

## Context & Background

{{ context_description }}

## Main Success Scenario

1. {{ step_1 }}
2. {{ step_2 }}
3. {{ step_3 }}
{{ additional_steps }}

## Contract Definition

### Inputs
```yaml
inputs:
{{ inputs_yaml }}
```

### Outputs
```yaml
outputs:
{{ outputs_yaml }}
```

### Behavior Rules
{{ behavior_rules }}

## Acceptance Criteria

{{ acceptance_criteria }}

## Business Rules

{{ business_rules }}

## Technical Constraints

{{ technical_constraints }}

## Non-Functional Requirements

### Performance
{{ performance_requirements }}

### Security
{{ security_requirements }}

### Scalability
{{ scalability_requirements }}

## Test Scenarios

### Happy Path
```yaml
scenario: "{{ happy_path_name }}"
given: {{ given_conditions }}
when: {{ when_actions }}
then: {{ then_expectations }}
```

### Edge Cases
{{ edge_cases }}

### Error Cases
{{ error_cases }}

## Implementation Notes

### Affected Components
{{ affected_components }}

### Dependencies
{{ dependencies }}

### Migration Considerations
{{ migration_notes }}

## References

- Related Specs: {{ related_specs }}
- Documentation: {{ documentation_links }}
- Design Decisions: {{ design_decisions }}

---
<!-- SPEC:VERSION:1.0 -->
<!-- SPEC:AI-OPTIMIZED:true -->