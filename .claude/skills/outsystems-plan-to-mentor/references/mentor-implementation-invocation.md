# Mentor Implementation Invocation

Invoke `outsystems-mentor-implementation` only after the coverage review is written and the patched plan passes `scripts/check_plan_handoff.py`.

Use this invocation payload:

```text
Invocation mode: outsystems-plan-to-mentor
Delivery mode: paste-prompts | outsystems-mcp
Source PRD: docs/superpowers/specs/approved-prd.md
Patched plan: docs/superpowers/plans/feature-patched.md
Output file: docs/superpowers/plans/feature-mentor-output.md
Mentor spec guardrails: references/mentor-spec-guardrails.md
```

When applying this template to another plan, replace the three file paths with the actual project-local source, patched plan, and output paths.

The invoked skill must:

- Treat the patched plan as the implementation source.
- Apply the relevant 10-section Mentor spec format and anti-failure guardrails from `references/mentor-spec-guardrails.md`.
- Preserve OutSystems implementation authority and evidence rules.
- Produce Studio-native, deterministic Mentor content. The 10-section Mentor spec is a summary layer; it does not replace the detailed pseudocode package.
- Include `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode`, and `Mentor Executable Sessions`.
- In `Studio-Native Pseudocode`, include `Data Model Pseudocode`, role, server action, client action, screen/UI, navigation, and verification pseudocode for every capability covered by the patched plan.
- Write the output file first.
- Use the selected delivery mode without asking unrelated execution questions.
