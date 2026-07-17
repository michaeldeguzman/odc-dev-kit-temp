# outsystems-mcp-skills

11 core Claude Code skills + 1 optional companion, built on top of the [`outsystems`](https://github.com/) MCP server. Each skill turns a multi-step ODC workflow into a single natural-language request.

> [!WARNING]
> **🧪 PROTOTYPE — internal experimentation only**
>
> This is an R&D exploration into whether MCP-driven AI tooling is a useful abstraction over the OutSystems MCP server. **It is not a product.** It may be rewritten, reorganized, or deleted at any time. Skills may fail in surprising ways on your tenant.
>
> **Do not use in customer-facing production work.**
>
> Why we built this: to learn whether Claude Code skills are the right primitive for common SA / developer workflows. Your feedback is the point — what works, what doesn't, what's missing.

---

## Where to start

| You are… | Read… |
|---|---|
| **New here — what is this catalog and how do I use it?** | **[`docs/INTRO.md`](docs/INTRO.md)** — plain-English overview, per-skill use cases, trigger phrases, gotchas. Designed for SAs, customers, and you-on-Monday |
| Not sure which skill to use for your task | [`docs/SKILL-INDEX.md`](docs/SKILL-INDEX.md) — decision tree: which skill for which job |
| Need the canonical "input → skill" map (agent-side reference) | [`docs/TRIGGER-MAP.md`](docs/TRIGGER-MAP.md) — disambiguation rules for adjacent skills + pre-vendor checklist for new additions |
| An engineer reviewing the catalog | [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) — shared rules, API quirks, token-efficiency patterns |
| Looking for what changed and when | [`CHANGELOG.md`](CHANGELOG.md) — per-skill release notes |

---

## What's in here

10 core skills + 1 optional companion, each in its own directory under `skills/`. Each turns a multi-step ODC workflow into a one-line natural-language ask. Grouped by primary use case:

### Explore — understand existing OutSystems work

| Skill | What it produces | Example trigger |
|---|---|---|
| `outsystems-tenant-architecture` | Interactive HTML graph of every asset in a tenant | *"Show me my tenant"* |
| `outsystems-app-architecture` | Interactive HTML graph of one app — screens, actions, entities, roles, AI model + library deps | *"Architecture of Banking Portal"* |
| `outsystems-ai-agent-landscape` | HTML dashboard of every AI agent + model connection in the tenant | *"AI inventory"* |
| `outsystems-dependency-impact` | Reverse-dependency explorer ("who depends on lib X?") | *"Who breaks if I publish [lib]?"* |

### Build — generate or extend an app via Mentor

> **Honest scope.** These skills drive ODC Mentor to bootstrap a structured app from a spec, design, or saved plan. Mentor is officially positioned for in-flow edits to existing apps; using it for end-to-end greenfield builds is an experimental pattern these skills layer on top. Treat the output as a draft scaffold for human review and iteration, not a ship-ready app or an officially supported workflow.

| Skill | What it produces | Example trigger |
|---|---|---|
| `outsystems-design-to-app` | Turn a **visual** design source (Figma URL / screenshot / HTML mockup) into a working OutSystems app — extracts design tokens + structure, composes a structured `spec.json` mapping every visual element to a real OS UI block, drives `mentor_start` in batches | *"Build this Figma in OutSystems"* · *"Design to model"* |
| `outsystems-spec-driven-build` | Build a new app from a **text-only** structured markdown spec via Mentor + anti-failure guardrails (RBAC, UI, terminology). Three modes: spec file / interview / clone-from-example | *"Build a new app from this spec"* · *"build app from scratch (no design)"* |
| `outsystems-plan-to-mentor` | **Coverage-review and patch** an existing saved plan file against its source PRD, then produce Mentor-ready prompts. Plan source is interchangeable — accepts `superpowers:writing-plans`, our `spec-driven-build` output, or hand-written plans | *"Review my plan against the PRD"* · *"Make this plan Mentor-ready"* |
| `outsystems-mentor-copilot` | Curated 11-task library + 3 workflows on top of ODC Mentor (quality / perf / security / accessibility / tests / docs / refactor / add-feature / model-migration / demo-data / demo-readiness) | *"Have Mentor audit [app]"* |
| `outsystems-custom-code` | Reference + workflow for building C# class-library "External Logic" libraries for ODC: SDK attributes, runtime constraints, unit + container tests, deploy via the OutSystems MCP | *"Build a C# library for OutSystems"* · *"ODC External Logic"* |

### Operate — ship, validate, document

| Skill | What it produces | Example trigger |
|---|---|---|
| `outsystems-deploy-preview` | HTML risk preview of a Dev→Test or Test→Prod promotion | *"Is it safe to ship [app] to Test?"* |
| `outsystems-app-documentation` | Markdown docs for one app (Confluence-ready) | *"Generate docs for [app]"* |

### Optional companion

| Skill | What it produces | Example trigger |
|---|---|---|
| `outsystems-mentor-polling-behavior` ⬡ | Three modes: (1) enforce Tier 1/2/3 polling discipline when running Mentor — records per-poll telemetry silently, no auto-render; (2) generate on-demand HTML benchmark dashboard; (3) cross-session summary + trend analysis with recommendations | *"Use Mentor on [app] to do X"* · *"Generate the Mentor dashboard"* · *"Mentor session summary"* |

⬡ **Optional companion skill.** Does not produce an app artifact. Install alongside the Build / Operate skills if you want Tier 1/2/3 polling discipline enforced and benchmark data on Mentor token usage. Layers on top of every Mentor invocation across the catalog.

All skills are versioned independently; current versions are in each `SKILL.md` frontmatter. Most skills are small (~250 lines of Markdown + ~100 lines of pure-stdlib Python + an HTML or Markdown template). The two design / external-code skills are larger — `outsystems-design-to-app` ships ~30 reference files (OS UI block catalogue + screen-archetype recipes), `outsystems-custom-code` is reference-style (no scripts/assets), and `outsystems-mentor-polling-behavior` ships an HTML dashboard + an SFTDD test suite.

---

## ⚠️ Harness compatibility — read before installing

**These skills work on Claude Code and Codex CLI.** Both harnesses are validated against live-tenant flows. The two behave the same on outcome; they diverge on first-pass cost — Claude Code's harness auto-saves oversized MCP responses to disk and injects only the file path (see `docs/CONVENTIONS.md` §8.1), while Codex receives the same payloads inline. For large-MCP skills (Mentor sessions, tenant scans, Figma extracts) Claude Code is materially cheaper on the first pass; on cached re-runs both are equivalent.

| Harness | Status | Notes |
|---|---|---|
| **Claude Code** | ✅ Supported | Most token-efficient path — harness auto-saves oversized MCP payloads to disk |
| **Codex CLI** | ✅ Supported | Same procedure + guardrails; first-pass cost higher for large-MCP skills. See each skill's `Harness notes` |
| Kiro CLI | ❌ Not supported | Runs but ~3-5× more expensive — no disk-save, full payloads enter context |
| VS Code + Copilot | ❌ Not supported | Token expires every 2–5 min mid-session; can't find apps by name |
| Cursor / Windsurf / Continue.dev | ❓ Untested | Probably broken — file an [Idea issue](../../issues/new?template=idea.yml) if you want one |

If you're on a non-supported harness, **don't install these** — open an issue tagged "Portability request" instead. Real money has been burned by testers trying to force these onto the wrong harness.

`outsystems-custom-code` is agent-neutral as of v1.1.0 and works on Codex and Claude Code with no workflow changes.

`outsystems-ai-agent-landscape` is agent-neutral as of v1.2.0 — validated on Codex + Claude Code, behavior unchanged (first run costs ~2x on Codex; see the skill's Harness notes).

`outsystems-tenant-architecture` is agent-neutral as of v1.5.0 — validated on Codex + Claude Code, behavior unchanged (large tenants cost more on Codex; see the skill's Harness notes).

`outsystems-app-architecture` is agent-neutral as of v1.4.0 — validated on Codex + Claude Code, behavior unchanged (first-run cost is higher on Codex; see the skill's Harness notes).

`outsystems-app-documentation` is agent-neutral as of v1.4.0 — validated on Codex + Claude Code, behavior unchanged (costs the same on both; see the skill's Harness notes).

`outsystems-deploy-preview` is agent-neutral as of v1.2.0 — validated on Codex + Claude Code, behavior unchanged (costs the same on both; see the skill's Harness notes).

`outsystems-dependency-impact` is agent-neutral as of v1.3.0 — validated on Codex + Claude Code, behavior unchanged (scan cost is the same on both; see the skill's Harness notes).

`outsystems-mentor-copilot` is agent-neutral as of v1.2.0 (validated on Codex + Claude Code; Claude Code is materially cheaper because its harness disk-saves Mentor's 30–500 KB OML-scan event, which lands inline elsewhere — see its Harness notes).

`outsystems-mentor-polling-behavior` is agent-neutral as of v1.4.0 — validated on Codex + Claude Code, behavior unchanged (Claude Code is cheaper to run; see the skill's Harness notes).

`outsystems-spec-driven-build` is agent-neutral as of v1.1.0 — validated on Codex + Claude Code, behavior unchanged (Claude Code is cheaper to run; see the skill's Harness notes).

`outsystems-design-to-app` is agent-neutral as of v1.1.0 — validated on Codex + Claude Code, behavior unchanged (a greenfield build costs more on Codex; see the skill's Harness notes).

---

## Installation

Skills auto-load from a per-agent skills directory. Install paths:

| Agent | Skills directory |
|---|---|
| **Claude Code** | `~/.claude/skills/` (`%USERPROFILE%\.claude\skills` on Windows) |
| **Codex CLI** | `~/.agents/skills/` (`%USERPROFILE%\.agents\skills` on Windows) |

> Note: `~/.codex/skills/` is Codex's deprecated location — don't use it. `~/.agents/skills/` is the current path.

### Path A — let your agent install it for you (recommended)

In a Claude Code session:

> *"Clone https://github.com/denwx/outsystems-mcp-skills and copy the contents of `skills/` into my `~/.claude/skills/` folder."*

In a Codex CLI session:

> *"Clone https://github.com/denwx/outsystems-mcp-skills and copy the contents of `skills/` into my `~/.agents/skills/` folder."*

Restart your session. On Claude Code, type `/skills` to verify 12 `outsystems-*` entries (11 core + 1 optional companion). On Codex, list your available skills via the agent's own mechanism.

### Path B — manual

**Claude Code:**
```bash
git clone https://github.com/denwx/outsystems-mcp-skills.git
cd outsystems-mcp-skills
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

**Codex CLI:**
```bash
git clone https://github.com/denwx/outsystems-mcp-skills.git
cd outsystems-mcp-skills
mkdir -p ~/.agents/skills
cp -R skills/* ~/.agents/skills/
```

Restart your agent.

### Prerequisites

- **Claude Code** or **Codex CLI** (the two validated harnesses — see `docs/CONVENTIONS.md` §8.1 for the token-efficiency trade-off between them)
- **Python 3.7+** as `python3` (stdlib only — no `pip install` ever)
- **The `outsystems` MCP server** registered and authenticated. Setup:
  ```
  claude mcp add -s user --transport http --client-id service_studio \
    --callback-port 7890 outsystems https://<your-tenant>.outsystems.dev/mcp
  ```
  Then in a fresh session, ask Claude to *"authorize the outsystems MCP"* — it'll walk you through the OAuth flow.

---

## Complementary tools (recommended companion installs)

These aren't part of this catalog — they're independent projects that pair well with our skills. Install separately.

| Tool | What it does | When to use |
|---|---|---|
| [`donnieprakoso/mcp-outsystems-docs`](https://github.com/donnieprakoso/mcp-outsystems-docs) | A separate **MCP server** doing semantic search over OutSystems ODC + O11 documentation. Fully local (offline embeddings), respects OutSystems CC BY-NC-ND license by keeping everything on your machine. Tools: `search_docs`, `get_doc`, freshness timestamp | When you want to query OutSystems docs from inside the same agent session you're running our workflow skills in. Particularly useful when Mentor builds reference platform features you're not sure about |
| [`PauloACRibeiro/portable-agent-skills` → `outsystems-mentor-implementation`](https://github.com/PauloACRibeiro/portable-agent-skills/tree/main/skills/outsystems-mentor-implementation) | A **companion skill** by Paulo Ribeiro (OutSystems R&D) that converts business intent into **Studio-native pseudocode** — real element names, parameter labels, runtime constraints — then produces paste-safe Mentor Studio prompts. Designed for the "agentic-coding-for-OutSystems" track that pairs with our `outsystems-plan-to-mentor`. Substantial knowledge artifact (~1 MB across ~80 reference files); not vendored here because Paulo's repo is the source-of-truth for ongoing maintenance | When you want deterministic Studio-native pseudocode generation BEFORE Mentor invocation (the "interpreted-language intermediate layer" angle Paulo articulated). **Prerequisite:** requires the `outsystems-tech-content` MCP server + `workspace-knowledge-cc` (or equivalent docs-mirror access) per Paulo's `colleague-readiness` notes. Verify those are available before installing |

---

## How to give feedback

This is the whole point. **Three lightweight ways:**

1. **Found a bug?** → [Open a Bug report](../../issues/new?template=bug-report.yml). What you tried, what happened, what you expected.
2. **Tried a skill and have a verdict?** → [Open a Skill feedback issue](../../issues/new?template=skill-feedback.yml). 30 seconds: 👍 / 👎 / 🤷 + would-use-again + a one-line comment.
3. **Have an idea for a new skill or improvement?** → [Open an Idea issue](../../issues/new?template=idea.yml). Tell us what you wish you could ask — in your words, the literal sentence.

For open-ended chat (*"is anyone else seeing this?"*, *"what should we build next?"*, install help, war stories) → use [Discussions](../../discussions).

**There is no "correct" feedback.** *"I tried this and it wasn't useful"* is as valuable as *"this is amazing."* What we want is your honest read.

---

## Honest expectations

- **Skills are early.** Each has been live-tested against a stage tenant, but not against your customers' workloads. Expect rough edges.
- **Some skills cost real money.** The Mentor-driven skills (`outsystems-mentor-copilot`, `outsystems-spec-driven-build`, `outsystems-design-to-app`) cost ~$1–15 per build depending on app complexity. The visualization and operate skills (`*-architecture`, `*-documentation`, `deploy-preview`, `dependency-impact`, `ai-agent-landscape`) are cents.
- **A handful of MCP-layer quirks** were found while building these. Each has a workaround baked into the relevant skill — see the individual `SKILL.md` files. If something looks off, file a Bug report issue.
- **This may be deleted next quarter.** If field signal says these aren't useful, we stop. Don't build production workflows on top of them.

(Harness compatibility is its own thing — see the matrix at the top of this README.)

---

## Repo layout

```
outsystems-mcp-skills/
├── README.md                — this file
├── CHANGELOG.md             — release notes per skill
├── LICENSE                  — MIT
├── docs/
│   ├── SKILL-INDEX.md       — decision tree: which skill for which job
│   └── CONVENTIONS.md       — engineering reference (shared rules across skills)
├── .github/
│   └── ISSUE_TEMPLATE/      — three feedback templates
└── skills/
    ├── outsystems-ai-agent-landscape/
    ├── outsystems-app-architecture/
    ├── outsystems-app-documentation/
    ├── outsystems-custom-code/
    ├── outsystems-dependency-impact/
    ├── outsystems-deploy-preview/
    ├── outsystems-design-to-app/
    ├── outsystems-mentor-copilot/
    ├── outsystems-mentor-polling-behavior/   ← optional companion
    ├── outsystems-plan-to-mentor/             ← from Paulo's portable-agent-skills repo
    ├── outsystems-spec-driven-build/
    └── outsystems-tenant-architecture/
```

Each skill follows a consistent structure where applicable: `SKILL.md` (front-door + procedure), `scripts/` (pure-Python stdlib transformer), `assets/` and/or `templates/` (HTML / Markdown templates + JSON task libraries), and `references/` for skills that ship domain knowledge (e.g. `outsystems-design-to-app`'s OS UI catalogue + screen-archetype recipes). Reference-style skills like `outsystems-custom-code` are SKILL.md only.

---

## Status

**v0.6.** 10 core skills + 1 optional companion. Four field-feedback patches shipped this cycle (dependency-impact v1.2.0/v1.2.1/v1.2.2 + architecture perf-defense bundle). Three new skills accepted via PR: `outsystems-design-to-app` (Swamy), `outsystems-custom-code` (Diogo), `outsystems-mentor-polling-behavior` (Donnie — optional companion). See [`CHANGELOG.md`](CHANGELOG.md) for the history.

**License:** MIT — see [`LICENSE`](LICENSE).

**Maintainer:** Deniz Arin, OutSystems R&D.
