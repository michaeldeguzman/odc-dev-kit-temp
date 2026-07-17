---
name: outsystems-plan-to-mentor
description: Coverage-review and patch an EXISTING saved OutSystems implementation plan file before Mentor conversion. The plan generator is interchangeable — accepts plans from `superpowers:writing-plans`, `outsystems-spec-driven-build`'s output, or hand-written plans. Audits the plan against the source PRD using a required coverage matrix, writes a patched plan to disk, and produces Mentor-ready prompts. Optional OutSystems MCP delivery via `outsystems-mentor-implementation` (companion in PauloACRibeiro/portable-agent-skills repo). EXPERIMENTAL — Mentor-for-greenfield is not an officially supported workflow; treat outputs as draft scaffolds for human review. Use when the user has a saved plan file in hand and asks for "review my plan", "patch my plan against the PRD", "coverage check my plan", "make this plan Mentor-ready", "plan-to-Mentor", or "convert this plan for Mentor". For greenfield builds with no saved plan yet, use `outsystems-spec-driven-build` (interview mode) or `outsystems-design-to-app` (with a visual source) first to produce the plan.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — MCP responses auto-save to disk). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. Mentor must be enabled on the tenant for MCP-delivery mode. Paste-delivery mode (the default) works without MCP.
allowed-tools: AskUserQuestion Read Write Edit Bash mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_info mcp__outsystems__mentor_start mcp__outsystems__mentor_get_run mcp__outsystems__mentor_cancel
metadata:
  version: "1.1.0"
  author: outsystems-r-and-d
---

# OutSystems Plan To Mentor

Coverage-review any saved OutSystems implementation plan before Mentor conversion. The plan generator is interchangeable; this skill owns the post-plan gate.

This skill works for both Codex and Claude, writes a patched plan before Mentor conversion, and keeps durable artifacts in the active project.

**Source attribution.** Vendored into this catalog from [`PauloACRibeiro/portable-agent-skills`](https://github.com/PauloACRibeiro/portable-agent-skills) (Paulo Ribeiro, OutSystems R&D). Paulo's repo remains the upstream source-of-truth for the agentic-coding-track skills; this catalog vendor maintains a copy adapted to our CONVENTIONS §3 frontmatter + Routing Boundary aligned with `docs/TRIGGER-MAP.md`. The companion skill `outsystems-mentor-implementation` is NOT vendored (1+ MB of curated knowledge content); install it directly from Paulo's repo if you want the full agentic-coding flow. See README's "Complementary tools" section.

## Catalog positioning

This skill belongs in the BUILD group and sits between any **planner** and Mentor. In trigger-map terms (`docs/TRIGGER-MAP.md`):

| Input | Skill that handles it |
|---|---|
| Markdown spec OR willingness to interview | `outsystems-spec-driven-build` |
| Figma URL / screenshot / HTML mockup | `outsystems-design-to-app` |
| **Existing saved plan file from any planner** | **this skill** |
| Studio-native pseudocode for one block | `outsystems-mentor-implementation` (Paulo's repo) |
| Curated task on an existing app (audit, refactor, test-gen…) | `outsystems-mentor-copilot` |

This skill **never** competes with the planners. It runs AFTER one of them has produced a plan file, audits the file's coverage against the source PRD, and patches gaps.

## Routing Boundary

Use this skill when the user has a saved OutSystems plan and asks to review it for coverage, patch gaps, produce Mentor-ready prompts, or optionally send the prepared prompt through OutSystems MCP.

Do not use this skill to write the original PRD, create the first implementation plan, or produce low-level Studio pseudocode directly. Use the relevant planner first, then use this skill. Delegate Studio-native conversion to `outsystems-mentor-implementation` after the patched plan is written.

Do not execute the plan with generic development skills. OutSystems Mentor delivery must go through this coverage gate and then `outsystems-mentor-implementation`.

Do not publish, deploy, rollback, promote, package, push, or create pull requests from this skill. Those actions require separate explicit approval outside the plan-to-Mentor gate.

## Inputs

Require both inputs before proceeding:

- Source PRD or original request: conversation context or file path.
- Saved plan file: project-local path to the plan being reviewed.

If either input is missing, stop and ask for the missing source. If the plan targets a live app and the user may choose MCP mode, also collect the target app name or app key before MCP delivery.

If the saved plan file is missing, do not continue coverage review and do not suggest `write-and-review-plan`. Offer to create the saved plan with `superpowers:writing-plans` or another explicit plan generator. After the plan is written, restart this workflow from step 1 with the new saved plan path.

### Missing Plan Generator Boundary

The first saved plan must be a business/capability implementation plan, not an ODC Studio element recipe. Do not adapt `superpowers:writing-plans` by mapping tasks directly to ODC elements.

Do not include Studio-native pseudocode, Server Action logic flows, entity attribute recipes, TrueChange steps, publish steps, or browser verification as the primary plan content. The first plan should describe capabilities, user workflows, acceptance criteria, scope boundaries, dependencies, and open decisions.

Do not create sections named `ODC Element Map`, `ODC Elements`, `Business Logic`, or `Screen Aggregates` in the first saved plan.

Do not list entity attributes, server action inputs, client actions, aggregates, screen widgets, role folders, TrueChange checks, publish checks, or browser checks in the first saved plan.

Use capability headings such as users and goals, workflows, business rules, acceptance criteria, dependencies, open decisions, and scope boundaries.

If the first plan seems to need an ODC element map to feel complete, stop at capability intent and let `outsystems-mentor-implementation` create the Studio-native element map later.

Leave Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen And UI Pseudocode, Navigation Pseudocode, and Verification Pseudocode to `outsystems-mentor-implementation`.

The first saved plan must not include a generic Superpowers execution header. Do not copy scanner-forbidden token strings into the generated plan, even inside negative wording.

Refer to those forbidden strings only as generic execution skills in generated plan text.

Use an OutSystems-specific handoff header that points to `outsystems-plan-to-mentor` for coverage review and `outsystems-mentor-implementation` for Mentor conversion.

## Workflow

1. Read the saved plan and the source PRD or original request.
2. Load `references/coverage-review-prompt.md`.
3. Audit the plan against the source of truth using the required coverage matrix.
4. If coverage ambiguity would change requirements, stop and ask before patching.
5. Write the coverage review to `docs/superpowers/plans/{plan-stem}-coverage-review.md`.
6. Write a minimally patched plan to `docs/superpowers/plans/{plan-stem}-patched.md`. The patched plan artifact must be a complete executable plan, not a change summary or wrapper. Copy the full patched plan content into `docs/superpowers/plans/{plan-stem}-patched.md`. Do not patch only the original plan in place and leave `-patched.md` as a short summary. Before writing the patched file, rewrite any generic Superpowers execution header to the OutSystems-specific handoff header.
7. Run at least two coverage passes before delivery mode. Pass 2 audits the patched plan against the same source of truth, writes `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`, and patches the plan again if any row is Missing, Partial without accepted platform/runtime uncertainty, unsupported by evidence, or invalid for ODC/Mentor implementation.
8. Repeat the coverage loop until convergence or max 3 passes. Convergence means no Missing rows, no Partial except explicitly accepted platform/runtime uncertainty, coverage >= 98, and all top gaps are closed or documented as accepted runtime risk. If a third pass is needed, write `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`.
9. Write each coverage pass to a versioned review artifact and show the final `Coverage Audit -- Patched Plan vs Spec` table before asking how to deliver.
10. Run `scripts/check_plan_handoff.py` against the same full patched plan file that will be sent to `outsystems-mentor-implementation`.
11. If the scanner reports a forbidden generic handoff, patch the plan again and rerun the scanner.
12. Load `references/delivery-modes.md`.
13. Do not ask the delivery mode question until the final coverage matrix is written and the patched plan passes the handoff scanner.
14. Ask the delivery mode question exactly once:

```text
1 - Create prompts ready to paste sequentially in Mentor in ODC Studio
2 - Send to Mentor using the OutSystems MCP
```

15. Load `references/mentor-spec-guardrails.md`.
16. Load `references/mentor-implementation-invocation.md`.
17. Invoke `outsystems-mentor-implementation` with that same full patched plan path, source PRD or request, selected delivery mode, output file path, and relevant Mentor spec guardrails.
18. Require `outsystems-mentor-implementation` to write the Mentor-ready output file before any MCP send.

## Artifact Rules

Use project-local artifacts:

- Coverage review: `docs/superpowers/plans/{plan-stem}-coverage-review.md`
- Coverage review v2: `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`
- Final coverage review, when needed: `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`
- Patched plan: `docs/superpowers/plans/{plan-stem}-patched.md`
- Mentor output: `docs/superpowers/plans/{plan-stem}-mentor-output.md`
- MCP result, when used: `docs/superpowers/reviews/{plan-stem}-mentor-result.json`

The patched plan file is the source of truth for downstream Mentor conversion.
It must contain the full final plan text after all coverage patches. A separate
change-summary section may be included inside the full file, but a summary-only
artifact is invalid.

Do not write to Claude-private cache/config, Codex-private config, plugin caches, or agent-private runtime folders.

## Compatibility

Keep the canonical workflow compatible with both Codex and Claude:

- Use plain skill and capability names in durable instructions.
- Keep Codex-only tool discovery notes out of the core workflow.
- Keep Claude-only tool names and cache paths out of the core workflow.
- Treat OutSystems MCP delivery as conditional on tools being available in the active agent.
- If MCP mode is selected but tools are unavailable, say so explicitly and fall back to paste mode unless the user chooses to stop.

## Final Response

Report:

- Coverage score and rationale.
- Final `Coverage Audit -- Patched Plan vs Spec` table.
- Top gaps closed.
- Coverage review paths.
- Patched plan path.
- Mentor output path.
- MCP result path when MCP mode was used.
- Remaining user decisions.
