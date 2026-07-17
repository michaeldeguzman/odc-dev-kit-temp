---
name: outsystems-spec-driven-build
description: Drive ODC Mentor to bootstrap an OutSystems app from a TEXT-ONLY structured spec — no design source needed. For Figma/image/HTML inputs, use `outsystems-design-to-app` instead. EXPERIMENTAL — Mentor is officially positioned for in-flow edits to existing apps; using it for end-to-end greenfield builds is a pattern this skill layers on top, and output quality varies with spec detail. Treat results as draft scaffolds for human review and iteration, NOT ship-ready apps. Pre-flight validates the spec for things Mentor commonly fumbles (RBAC roles per screen, entity relationships, integration points), then drives mentor_start with anti-failure guardrails. Three entry modes — provide your own markdown spec file, walk through an interview, or clone from an example template. Use when the user asks to "build a new app from spec", "generate an app from requirements", "create a new app", "build app from scratch", "have Mentor build [app] from this spec", "build an app from this written description", or similar greenfield-build asks with NO design artifact.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. Mentor must be enabled on the tenant.
allowed-tools: AskUserQuestion Bash Read Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_create mcp__outsystems__mentor_start mcp__outsystems__mentor_get_run mcp__outsystems__mentor_cancel
metadata:
  version: "1.1.0"
  author: outsystems-r-and-d
---

# OutSystems Spec-Driven Build

Generate a new OutSystems app from a structured spec via ODC Mentor.
The skill's job is **the prep step that makes Mentor succeed on the
first try** — not "have Mentor build an app for me" (that's just
`mentor_start` with a prompt).

**Why this exists:** field testing showed that under-specified Mentor
calls cost 5–10× more than tight ones. Peter R. spent $10 adding 7
form fields to an under-specified app. Vasco E.'s ambitious RFP spec
hit Mentor's known RBAC weakness in Claude. Donnie P. independently
demonstrated that disciplined upfront spec engineering keeps Mentor
builds clean — he used his own
[Spec-First TDD (SFTDD)](https://github.com/donnieprakoso/spec-first-tdd)
template to build
[`donnieprakoso/mcp-outsystems-docs`](https://github.com/donnieprakoso/mcp-outsystems-docs)
(an OutSystems docs MCP server, complementary to our catalog — see
README) and reports the discipline kept token cost predictable.

This skill's shape (interview → assemble → validate → fire) is **our
own** — designed for greenfield OutSystems-app builds in a single
Mentor invocation — distinct from SFTDD's iterative
Red → Green → Enhancement → Refactor cycle. But the underlying
conviction is the same: **agree on the spec before you fire the
expensive call.** That conviction is what Donnie's work surfaced as
real, field-tested signal; the OutSystems-specific guardrails below
are what we add on top.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b — **plus Mentor
enabled on the tenant.** Shared rules: §7b (API quirks), §8
(token-efficiency).

**One platform constraint to know:** Mentor edits existing app shells;
it does not create apps from scratch via the MCP. The user needs an
empty/template app shell in ODC Portal as the target. The skill's
Step 1 handles this.

## When NOT to use

- **Adding features to an existing app** → use `outsystems-mentor-copilot`'s
  `add-feature` task. Mentor preserves more context with an alive session.
- **Building an app via free-form conversation** → call `mentor_start`
  directly with your prompt. This skill's value-add is only meaningful
  when there's a spec to be disciplined about.
- **Quick prototyping where you don't care about RBAC / quality** →
  this skill's overhead doesn't pay off. Direct `mentor_start` is fine.

## Procedure

### Step 1 — Identify or create the app shell

Mentor needs an app key to edit. Three paths in order of preference:

- **User has a fresh empty app already** → capture `APP_KEY` from
  their prompt or `mcp__outsystems__app_list` with their app name
  search.
- **Mint a fresh shell programmatically (recommended for clean tests)** →
  call `mcp__outsystems__app_create` with `name=<their-app-name>`
  and `kind=CrossDevice` (or `Mobile`, `AIAgent`, etc. matching the
  spec's intent). Returns `{assetKey, revision, name, assetType}` —
  use that `assetKey` as the `APP_KEY`. One MCP call (~$0.01).
- **User creates one in ODC Portal** → if they prefer the GUI path,
  ask them to create an empty app, then come back with the key.

**Do NOT use Template_* / template_* apps as the shell.** They are
System modules and Mentor's Model API refuses to load them with:
*"System modules cannot be loaded with the Model API. Consider using
the Clone method instead."* Use `app_create` (above) or have the user
clone via ODC Portal first. Confirmed via live test 2026-05-31 —
`Template Web App`, `Template_TestAgent`, `template_Agent`, and
`OutSystems Sample Data` all hit this error.

```
APP_KEY      = <asset key>
APP_NAME     = <human name>
CACHE        = ~/.claude/cache/outsystems-spec-driven-build/<APP_KEY>/
SKILL        = <this skill's directory>
mkdir -p "$CACHE"
```

### Step 2 — Get the spec

Three entry modes — pick based on what the user has:

#### Mode A: User provides a spec file

```bash
cp <user-provided-path>.md "$CACHE/spec.md"
python3 "$SKILL/scripts/build.py" validate-spec --spec "$CACHE/spec.md"
```

If validation fails (missing sections), the script prints what's
missing. Either retry with a corrected spec or fall through to
Mode B's interview to fill gaps.

#### Mode B: Interview the user

```bash
python3 "$SKILL/scripts/build.py" list-questions > "$CACHE/questions.json"
```

Then iterate through the questions, asking the user each one and
capturing each answer. After the interview, assemble the spec:

```bash
python3 "$SKILL/scripts/build.py" assemble-spec \
  --answers "$CACHE/answers.json" \
  --output  "$CACHE/spec.md"
```

#### Mode C: Clone from the example template

```bash
cp "$SKILL/templates/example-spec.md" "$CACHE/spec.md"
```

Then either edit-in-place or instruct the user to fill in the
placeholders. Validate before proceeding (Mode A).

### Step 3 — Confirm with the user

Before firing Mentor, **show the user the final spec** and get
explicit confirmation. Mentor calls are expensive ($1–$5 typical
for a greenfield build); a missed requirement at this step costs a
full re-run.

```bash
python3 "$SKILL/scripts/build.py" show-spec --spec "$CACHE/spec.md"
```

Display the output. Ask the user a yes/no via `AskUserQuestion`:
*"Ready to fire Mentor with this spec? Estimated cost: $1–5."*

> Claude Code exposes this confirmation as the `AskUserQuestion` tool. On a
> harness without it (Codex), ask the same question inline and wait for an
> explicit answer before continuing. The gate is the confirmation, not the tool.

### Step 4 — Drive Mentor with anti-failure guardrails

Wrap the spec in a prompt that pre-empts Mentor's known fumbles:

```bash
PROMPT=$(python3 "$SKILL/scripts/build.py" build-prompt --spec "$CACHE/spec.md" --app-key "$APP_KEY")
```

The built prompt includes guardrails like:
- *"Respect the role-per-screen assignments exactly as specified.
  Do NOT default screens to anonymous/public access."* (Vasco's RBAC fix)
- *"Apply OutSystems UI to all screens. Do NOT generate bare HTML
  layouts."* (João's missing-UI fix)
- *"Use ODC terminology only. Do NOT reference 'Service Studio' or
  'eSpace' — those are O11 concepts."* (Inês's terminology fix)
- *"If you need to add a referenced library, ask the user to do it
  manually in Studio. Do NOT call `eSpace.AddDependency` — known
  broken."* (Peter's AddDependency NRE fix)

Then call `mcp__outsystems__mentor_start`:

```
mcp__outsystems__mentor_start(
  app_key = "$APP_KEY",
  prompt  = "$PROMPT"
)
```

Capture `runId`.

### Step 5 — Poll Mentor (cursor discipline)

Same polling contract as `outsystems-mentor-copilot` SKILL.md Step 4 —
DO NOT re-implement here; the rules are identical:

- First poll: no `cursor`
- Subsequent polls: pass `nextCursor` from previous response
- If `nextCursor: null`, omit `cursor` on the next poll too
- Honor `pollAfterMs` (2–5 s typical), sleep longer on empty events
- Sandbox-safe sleep: `sleep 2` to `sleep 5`; for longer waits use
  `until …; do sleep 2; done`
- Expect 1 huge event early (Mentor's OML introspection) — 50–500 KB
- Expect the terminal poll to potentially exceed max tokens — on Claude Code
  the harness auto-saves oversized MCP results to disk and injects only the
  path (read the file back if so); a harness without that auto-save (Codex)
  gets the payload inline. See `## Harness notes`.
- Stop on `status: succeeded` / `failed` / `cancelled`

### Step 6 — Save the terminal result

Same as `outsystems-mentor-copilot` Step 5 — three save paths:

1. **Terminal response inline + fits in context** → write it to
   `$CACHE/mentor-result.json`
2. **Auto-spilled to disk (Claude Code's >25 KB auto-save)** → `cp` to
   `$CACHE/mentor-result.json` OR pass path directly to Step 7. A harness
   without auto-save (Codex) gets the result inline — use path 1 or 3.
3. **Inline but you want it on disk** → write it

### Step 7 — Render the build report

```bash
python3 "$SKILL/scripts/build.py" render-report \
  --spec     "$CACHE/spec.md"             \
  --result   "$CACHE/mentor-result.json"  \
  --output   "$CACHE/build-report.md"     \
  --app-key  "$APP_KEY"                   \
  --run-id   "<runId>"
```

The report combines:
- The spec used
- Mentor's summary + any changes applied
- Counts (entities created, screens generated, actions added)
- Publish handoff (`mentor_session_token` + ready-to-fire
  `publish_start` call, **for human review — never auto-publish**)
- Suggested next steps (run `outsystems-mentor-copilot`'s
  `test-generation` task on the new actions, etc.)

### Step 8 — Report to user (3–5 lines)

- Output path
- App + revision (Mentor returns updated `mentor_session_token`)
- Counts of generated artifacts
- Cost estimate (poll count × $0.10 rough)
- *"Open the build report. Run publish-handoff to commit, or run
  `outsystems-mentor-copilot` follow-up tasks (test-generation,
  add-feature) on the same Mentor session."*

## Cache rules

> The cache path stays at `~/.claude/cache/outsystems-spec-driven-build/<APP_KEY>/`
> on **every** harness — a shared cross-agent cache, not a Claude-only location.
> Codex reads and writes the same directory, so past spec + result pairs are
> visible regardless of which agent recorded the build.

- Location: `~/.claude/cache/outsystems-spec-driven-build/<APP_KEY>/`
- TTL: **none** — spec-driven builds are user-initiated, the user
  owns retention. Past spec + result pairs stay until cleaned up.
- Re-rendering a past run: just re-run Step 7. ~1K tokens.

## Token budget (estimate)

| Scenario | Mechanism | Total |
|---|---|---|
| Greenfield build, tight spec, simple app (5 entities, 8 screens) | spec + mentor_start + ~30 polls + report | **~30–60K** ($1–$2 on Opus 4.7) |
| Same but ambitious (15+ entities, RBAC, integrations) | spec + mentor_start + ~50–80 polls | **~60–120K** ($2–$5) |
| Re-running with same spec | Mentor session reuse + render | ~10K |
| Re-rendering a past build | Just render-report | ~1K |

Empirically: testers who used spec-driven patterns report 30–50%
lower token cost than ad-hoc conversational builds for similar app
complexity. The savings come from Mentor not spinning on
under-specified requirements.

## Harness notes

- **Claude Code** auto-saves any MCP result larger than ~25 KB to disk and
  injects only the file path into context, keeping the payload itself out of
  the model's context. This skill's Mentor polls routinely cross that
  threshold — Step 5 warns of one 50–500 KB OML-introspection event early, and
  the terminal poll can exceed the context limit outright.
- **Codex** has no such auto-save: the full MCP result is injected inline. So a
  greenfield build's Mentor polling costs materially more on Codex's first pass
  — every large `mentor_get_run` payload lands in context instead of spilling
  to disk. The token-budget table above reflects Claude Code; add the inline
  payload volume for a Codex estimate.
- On a harness without auto-save, follow Step 6 path 1 or 3 (write the result to
  `$CACHE/mentor-result.json` yourself) instead of relying on the harness spill
  in path 2.
- **Re-rendering a past build** (Step 7, `render-report`) makes zero MCP calls —
  it reads the local spec + result — so it costs the same (~1K tokens) on both
  harnesses. Re-running with the same spec reuses the Mentor session and also
  avoids re-fetching.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4). Skill-specific:

- **Don't use a System-module template app as the shell** — they're
  rejected by Mentor's Model API with *"System modules cannot be
  loaded with the Model API. Consider using the Clone method instead."*
  Specifically avoid `Template_*`, `template_*`, `OutSystems Sample
  Data`. Use `mcp__outsystems__app_create` to mint a fresh shell, or
  have the user clone via ODC Portal.
- **Don't skip the spec validation step.** Validation catches missing
  RBAC, missing entity relationships, missing screen-role mappings
  before Mentor burns tokens on them.
- **Don't fire Mentor without user confirmation (Step 3).** A $1–5
  call shouldn't happen on assumption. Always show + confirm.
- **Don't try to make Mentor create a brand-new app shell** — it
  edits existing ones. If the user has no shell, route them to ODC
  Portal first.
- **Don't auto-publish the result.** The build report ends with a
  publish-handoff template. Human reviews + fires `publish_start`.
- **Don't omit the anti-Mentor-failure guardrails in the prompt
  (Step 4).** They were derived from real field-test failures —
  removing them re-introduces those failures.

## Related skills (chain after a successful build)

- `outsystems-mentor-copilot` (`test-generation`) — generate test
  scaffolds for the actions the build just created
- `outsystems-app-architecture` — visualize what was built
- `outsystems-app-documentation` — generate Markdown docs for the
  new app
- `outsystems-deploy-preview` — check the build before promoting to
  Test/Prod

Workflow: spec-driven-build → mentor-copilot test-generation →
app-architecture (visualize) → deploy-preview (gate to Test) →
publish.
