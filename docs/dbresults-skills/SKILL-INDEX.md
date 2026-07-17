# Which skill for which job?

A decision tree for solution architects, developers, and anyone using
`outsystems-mcp-skills`. Use this when you have a question or task
involving OutSystems and aren't sure which skill (if any) is the
right tool.

> Pinned in the agent-experience Slack channel + linked from the
> repo README. If you find yourself thinking *"I have an OutSystems
> task, is there a skill for this?"* — start here.

---

## Start here

```
What are you trying to do?
│
├─→ Understand an existing tenant or app     →  EXPLORE
├─→ Build, modify, or extend an app          →  BUILD
├─→ Ship, validate, audit, or document       →  OPERATE
└─→ None of the above                        →  When no skill fits
```

---

## EXPLORE — understand existing OutSystems work

Use these when you need to *see* what's there, not change it.

| You're asking… | The skill | What you get |
|---|---|---|
| *"What's in this tenant?"* · *"Show me the asset landscape"* · *"Architecture diagram"* | **`outsystems-tenant-architecture`** | Interactive HTML graph of every asset (apps, agents, model connections, libraries, integrations), filter-by-type, OutSystems dark theme |
| *"What does this app actually do?"* · *"Walk me through [app]"* · *"What's inside [app]?"* | **`outsystems-app-architecture`** | Interactive HTML graph of one app's screens, actions, entities, roles, AI model + library dependencies |
| *"What AI agents and models are in this tenant?"* · *"Audit my AI"* | **`outsystems-ai-agent-landscape`** | Dashboard of agents + model connections with provider breakdown, Trial-vs-Customer audit, test/demo heuristics |
| *"Who depends on this library/agent?"* · *"If I publish X, who breaks?"* · *"Blast radius"* | **`outsystems-dependency-impact`** | Searchable reverse-dependency explorer (HTML, browser-queryable after one scan) |

---

## BUILD — modify or extend an app

Use these when Mentor is in the loop.

| Your job | The skill | Notes |
|---|---|---|
| *"Build this Figma in OutSystems"* · *"Turn this design into an app"* · *"Design to model"* · *"Generate a screen from this mockup"* | **`outsystems-design-to-app`** | Four design source modes (Figma / HTML / image / brief) + mandatory block-mapping gate + 4-part spec format + batched Mentor invocation. Bundled OS UI domain knowledge (layouts, blocks, patterns, recipes). |
| *"Build a new app from spec"* · *"Generate this app from these requirements"* · *"Create [app] from scratch"* | **`outsystems-spec-driven-build`** | Three modes (spec file / interview / clone-from-example) + spec validation + Mentor-prompt with anti-failure guardrails (RBAC, UI defaults, terminology) |
| *"Have Mentor audit this app"* (quality / security / performance / accessibility / demo readiness) | **`outsystems-mentor-copilot`** | 11 curated Mentor prompt templates + cursor-paged polling loop + Markdown report |
| *"Generate tests for this app"* | **`outsystems-mentor-copilot`** (`test-generation` task) | Test scaffolds for top-N server actions; reviewer fills in assertions |
| *"Add a feature to this app"* | **`outsystems-mentor-copilot`** (`add-feature` task) | Structured prompting for Mentor; lower risk of off-the-rails generation |
| *"Migrate this app from AI model X to AI model Y"* | **`outsystems-mentor-copilot`** (`model-migration` task) | Traces all references + proposes prompt adjustments for the target model |
| *"Generate documentation for this app"* | **`outsystems-app-documentation`** | Markdown output (Confluence/wiki paste-ready); reuses arch-cache for free |
| *"Build a C# library to extend OutSystems"* · *"ODC External Logic"* · *"Custom code for ODC"* · *"Publish a `.NET` library to OutSystems"* | **`outsystems-custom-code`** | C# class-library reference: SDK attributes (`[OSInterface]` / `[OSAction]` / `[OSParameter]` / `[OSStructure]`), supported data types, runtime constraints (95s / 1 GB / 5.5 MB), unit + container tests, deploy via the OutSystems MCP. A different shape than the other Build skills — extends ODC with native code, not Mentor-generated app surface. |
| *"Review my plan against the PRD"* · *"Coverage-check this plan"* · *"Make this plan Mentor-ready"* · *"Plan-to-Mentor"* · *"Patch my plan"* | **`outsystems-plan-to-mentor`** | Coverage-review + patch ANY saved OutSystems plan against its source PRD before Mentor conversion. Plan generator is interchangeable — accepts `superpowers:writing-plans`, `outsystems-spec-driven-build` output, or hand-written. Required coverage matrix, versioned review artifacts, two-pass coverage loop, then Mentor-ready prompts (paste or MCP delivery). The "agentic-coding-for-OutSystems" track entry-point. Vendored from Paulo Ribeiro's [`PauloACRibeiro/portable-agent-skills`](https://github.com/PauloACRibeiro/portable-agent-skills). |
| *"Add BDD tests for [entity]"* · *"Add Gherkin tests"* · *"Set up BDD Framework testing"* | **`dbresults-odc-bdd-crud-tests`** | Project-local skill (`.claude/skills/`, not vendored from this catalog). BDD Framework (Forge component) scenarios covering an entity's CRUD wrapper actions. Opt-in gate first — defaults to pointing at `outsystems-mentor-copilot`'s `test-generation` task unless BDD specifically is confirmed. Wires cross-app test access via Service Actions (not a Library — that path is a confirmed platform dead end) and creates the test app via `app_create` → `dbresults-odc-new-app-baseline`. |

### Where there's no skill yet (you can still build, just without a wrapper)
| Your job | Best path today |
|---|---|
| *"Build a fresh app in 5 minutes for a demo"* | Direct conversational `mentor_start`. Expect rough OOTB UX — for production builds, use `outsystems-spec-driven-build` instead (the 30-min spec investment saves $5+ per build). |

---

## OPERATE — ship, validate, audit, document

Use these for the "is it safe?" and "what changed?" questions.

| Your job | The skill | Notes |
|---|---|---|
| *"Is it safe to promote [app] to Test/Prod?"* · *"Deploy preview"* | **`outsystems-deploy-preview`** | Risk preview computed client-side — works around a known issue where `deploy_impact` returns null indefinitely. Useful even when `deploy_impact` would be the "right" answer if it worked. |
| *"Document [app] for compliance / Confluence / wiki"* | **`outsystems-app-documentation`** | Same as in BUILD branch — works for either greenfield docs or retroactive |

---

## Optional companion — polling discipline + telemetry

Layers on top of EVERY Mentor invocation across the catalog. Does not produce an app artifact. Install alongside Build/Operate if you want polling discipline enforced and benchmark data on Mentor token usage.

| Your job | The skill | Notes |
|---|---|---|
| *"Use Mentor on [app] to do X"* (and you want token discipline) · *"Generate the Mentor dashboard"* · *"Mentor session summary"* · *"Mentor session trends"* | **`outsystems-mentor-polling-behavior`** ⬡ | Three modes: (1) enforce Tier 1/2/3 polling discipline when running Mentor — records per-poll telemetry silently, no auto-render; (2) generate on-demand HTML benchmark dashboard; (3) cross-session summary + trend analysis with recommendations. Tier 3 polls (`mentor_get_run`) at 30s cadence instead of the 500ms default — ~99% fewer poll-response payloads in context per typical 6-min Mentor run. |

⬡ This skill enforces a contract on top of the Mentor-driven skills above. It's an optional layer — without it, the Mentor-driven skills work but at default polling cadence.

---

## When no skill fits

Some asks aren't (yet) skill-shaped. Reach for one of these instead:

### 1. Call MCP tools directly
For one-off questions where a skill would be overkill. Examples:
- *"Just show me the list of apps"* → `mcp__outsystems__app_list`
- *"I have a very specific Mentor task that doesn't match any template"* → `mcp__outsystems__mentor_start` with a custom prompt
- *"What environments do we have?"* → `mcp__outsystems__env_list`

The MCP tools are documented in the OutSystems plugin instructions
(use `/outsystems:outsystems` in a Claude Code session to view them).

### 2. File an idea in this repo
If you keep needing the same thing and there's no skill, **open an Idea issue** in this repo. Use the `idea.yml` template. We triage these weekly. If it shows up 2-3 times across testers, it gets built.

### 3. Check if it's actually an engineering problem
Many tester problems aren't fixable in the skills catalog — they need work on the MCP server, Mentor, or the ODC platform itself. Examples:
- **OAuth token expires too fast** → MCP server team
- **Mentor session corrupts after errors** → Mentor team
- **New apps don't apply OutSystems UI by default** → Mentor team
- **Need to see real-time AI cost per agent** → ODC platform team

When you file an Idea issue (above), tag it `engineering routing needed` and we'll triage to the right team — it just won't get fixed in this catalog.

### 4. Ask in the Slack channel
`#agent-experience-internal-testing` — community input often surfaces
the right path. You're probably not the only one.

---

## Quick reference: skills by primary use case

```
┌────────────────────────────────────────────────────────────────┐
│  EXPLORE  →  tenant-architecture · app-architecture            │
│           →  ai-agent-landscape · dependency-impact            │
│                                                                │
│  BUILD    →  design-to-app   (Figma / mockup → app via Mentor) │
│           →  spec-driven-build (greenfield from text spec)     │
│           →  plan-to-mentor  (post-plan coverage gate)         │
│           →  mentor-copilot  (11 task templates + 3 workflows) │
│           →  custom-code     (C# External Logic libraries)     │
│                                                                │
│  OPERATE  →  deploy-preview · app-documentation                │
│                                                                │
│  OPTIONAL →  mentor-polling-behavior (polling discipline +     │
│              telemetry dashboard — not an app-building skill)  │
└────────────────────────────────────────────────────────────────┘
```

11 core skills + 1 optional companion, current versions:

**Core:**
- `outsystems-tenant-architecture` v1.4.2
- `outsystems-app-architecture` v1.3.2
- `outsystems-app-documentation` v1.2.1
- `outsystems-ai-agent-landscape` v1.1.1
- `outsystems-dependency-impact` v1.2.2
- `outsystems-deploy-preview` v1.1.1
- `outsystems-mentor-copilot` v1.1.1
- `outsystems-spec-driven-build` v1.0.1
- `outsystems-design-to-app` v1.0.0
- `outsystems-custom-code` v1.0.0
- `outsystems-plan-to-mentor` v1.0.0 — vendored from Paulo Ribeiro's portable-agent-skills

**Optional companion:**
- `outsystems-mentor-polling-behavior` v1.3.0 — polling discipline + telemetry dashboard

**Companion in a separate repo** (install from upstream):
- `outsystems-mentor-implementation` — Studio-native pseudocode generation (Paulo's [`portable-agent-skills`](https://github.com/PauloACRibeiro/portable-agent-skills))

See `CHANGELOG.md` for what changed in each release.

---

## Compatibility note

All skills are validated on **Claude Code** and **Codex CLI**. Claude
Code is the most token-efficient path — its harness auto-saves
oversized MCP results to disk and injects only the file path, keeping
large-payload skills (Mentor, tenant scans, Figma extracts) cheaper on
the first pass. Codex CLI receives the same payloads inline, so
first-pass cost is materially higher for large-MCP skills — see each
skill's `## Harness notes` section for its specific cost profile.

They will probably not work cleanly in Cursor / Windsurf /
Continue.dev / Kiro today. If you'd use them in another harness,
**file a Portability request** (idea template, `Portability request`
category) so we can gauge demand and plan adapters.
