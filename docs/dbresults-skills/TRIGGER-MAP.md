# Trigger Map — which skill for which input

Reference for both the agent and human reviewers. Lists what each skill expects as input, what it produces, and how to disambiguate when multiple skills could match.

When a new skill candidate is considered, this map gets updated FIRST — overlapping triggers get tightened on both sides before merging.

---

## At a glance — input or intent → canonical skill

| You have / want… | Skill | What it produces |
|---|---|---|
| **A whole-tenant overview** ("show me my tenant", "tenant ECG") | `outsystems-tenant-architecture` | Interactive HTML graph of every asset |
| **One app's anatomy** ("show me Banking Portal", "architecture of [app]") | `outsystems-app-architecture` | Interactive HTML graph of one app |
| **AI agents + model connections audit** ("what AI is in my tenant") | `outsystems-ai-agent-landscape` | Governance dashboard |
| **Reverse-dependency question** ("who depends on lib X?") | `outsystems-dependency-impact` | Searchable reverse-dep HTML explorer |
| **Markdown docs for one app** ("document [app]") | `outsystems-app-documentation` | Confluence-ready Markdown |
| **Deploy promotion risk check** ("safe to ship [app] to Test?") | `outsystems-deploy-preview` | HTML risk preview |
| **A Figma URL / screenshot / HTML mockup → working app** | `outsystems-design-to-app` | Mentor-built app from VISUAL source |
| **A structured markdown spec → working app** (no design source) | `outsystems-spec-driven-build` | Mentor-built app from text-only spec |
| **An existing saved plan file → patched, Mentor-ready** | `outsystems-plan-to-mentor` (when vendored from Paulo) | Coverage-checked patched plan + Mentor prompts |
| **Business intent for a specific block → Studio-native pseudocode** | `outsystems-mentor-implementation` (companion via Paulo's repo) | Paste-safe Mentor Studio prompt |
| **Mentor task on an existing app** (audit / refactor / test-gen / demo-readiness) | `outsystems-mentor-copilot` | 11 curated task templates + Markdown report |
| **C# External Logic library** | `outsystems-custom-code` | Recipe + workflow for ODC External Logic |
| **Token-efficient Mentor wrapper + telemetry dashboard** | `outsystems-mentor-polling-behavior` ⬡ (companion) | Bundled discipline + per-poll telemetry |

⬡ = optional companion skill (does not produce app artifact)

---

## When ambiguous — the agent should ASK, not guess

Some prompts could match multiple skills. These are the resolution rules.

### "Build me an app" (no specific input named)

The disambiguator is **what the user has in hand**:

| User has | Skill |
|---|---|
| A Figma URL / image / screenshot / HTML mockup | `design-to-app` |
| A markdown spec file OR willing to do an interview | `spec-driven-build` |
| A saved plan file (from `superpowers:writing-plans`, `spec-driven-build`'s output, hand-written) | `plan-to-mentor` |
| Only a prose description (no file, no design) | Ask: spec-driven-build interview mode OR ask user to write a markdown spec first |

### "Generate the Mentor prompt for X"

| X is… | Skill |
|---|---|
| A specific Studio implementation question (where does this logic go? which element?) | `mentor-implementation` (companion via Paulo's repo) |
| A curated audit task (security review, demo readiness, accessibility, test generation, …) | `mentor-copilot` |
| A fresh greenfield app build | `spec-driven-build` OR `design-to-app` per the input matrix above |

### "Show me my [thing]"

| Thing | Skill |
|---|---|
| TENANT (whole landscape) | `tenant-architecture` |
| APP [name] (one app's anatomy) | `app-architecture` |
| AI agents / model connections | `ai-agent-landscape` |
| Ambiguous / unclear scope | Ask which level (tenant / app / AI inventory) before firing — don't default |

### "Document this"

| Scope | Skill |
|---|---|
| One specific named app | `app-documentation` |
| Library / shared component | No skill yet — use `app-architecture` as the closest fit |
| Whole tenant | No skill yet — use `tenant-architecture` for visualization |

### "Run Mentor on my app to do X"

This is where the agentic stack stacks up:

1. **`mentor-polling-behavior`** auto-attaches as the wrapping layer (polling discipline + telemetry recording)
2. The SECOND skill picked depends on what X is:
   - Curated audit/build task → `mentor-copilot`
   - Studio-native pseudocode question → `mentor-implementation`
   - Greenfield app from spec → `spec-driven-build`
   - Greenfield app from design → `design-to-app`
3. The chosen build/task skill fires inside the polling-behavior wrapper

The polling-behavior skill does NOT compete with the others; it COMPOSES with them. If only it triggers and nothing else, no Mentor call happens (and dashboard stays empty — see Rui's feedback in commit `4ecbba1`).

---

## Conductor commands — the layer above this catalog

Some users (currently Deniz, possibly others) install **conductor commands** that live one layer above this catalog and orchestrate across catalog skills + MCP tools. The known ones:

| Conductor | Wraps | Adds |
|---|---|---|
| `change-app` | catalog Mentor-driven skills | Gated brief + plan before Mentor invocation |
| `demo-prep` | `outsystems-mentor-copilot` (demo-readiness + demo-data tasks) | Warm caches + seed sample data + runtime smoke |
| `ship` | `outsystems-deploy-preview` | Pre/post Playwright smoke + gated promote + rollback ready |
| `review-app` | `outsystems-mentor-copilot` (quality / security / accessibility / performance review tasks) | Multi-lens quality gate + ranked findings + gated auto-fix |
| `explore-app` | `outsystems-app-architecture` + `outsystems-app-documentation` + `outsystems-dependency-impact` | Plain-English onboarding brief, one pack |
| `tenant-audit` | `outsystems-tenant-architecture` + `outsystems-ai-agent-landscape` + `outsystems-dependency-impact` | Tenant-wide governance snapshot + cleanup recommendations |
| `design-to-app` (conductor variant) | catalog `outsystems-design-to-app` | Iterate-and-validate Playwright loop |

### When a conductor and a catalog skill both match a prompt

**The conductor wins.** That's correct behavior — the conductor matches more specific intent (e.g., *"demo-readiness check"* is exactly demo-prep's territory) and adds value (orchestration, additional steps) beyond the underlying catalog skill.

The catalog skill remains the **floor** that ships to users who haven't installed conductors. Conductors are the **ceiling** that power-users layer on top.

### Debugging tip

If you expected a catalog skill to fire and it didn't:

1. Check whether a conductor matched the prompt first. The conductor's description will name the catalog skill it wraps.
2. If a conductor fired, that's by design. The conductor is doing the catalog skill's work + more.
3. If neither fired, the catalog description may be too narrow. File a Bug / Skill feedback issue with the exact prompt.

### What we don't do

We don't promote conductors into the catalog. They're a separate concern (per-team / per-user orchestration patterns) and have their own lifecycle. The catalog ships skill primitives that conductors can compose.

## How descriptions stay sharp

Catalog hygiene rules — applied to every existing skill, applied during every new-skill review:

1. **Every skill's description leads with what INPUT it expects.** Users self-route based on what they have in hand.
2. **Every skill has a "When NOT to use" section** pointing at the alternative for adjacent jobs.
3. **Adjacent skills cross-reference each other in their "Routing Boundary" sections** (Paulo's pattern, adopted catalog-wide).
4. **When a new skill candidate has trigger overlap with an existing skill, descriptions on BOTH sides get tightened** before the merge. The catalog gets sharper, not muddier, with each addition.
5. **No description trigger phrase belongs to more than one skill.** If two skills could both match a phrase, one of them rewords. The Routing Boundary explains why.

---

## Last-audited

| Audit | Outcome |
|---|---|
| 2026-06-29 — pre-Paulo audit | Identified `design-to-app`'s "written description" trigger as overlapping with `spec-driven-build`; tightened design-to-app to visual sources only. Added Routing Boundary to `mentor-copilot` acknowledging the future `mentor-implementation` companion. Authored this trigger map |
| 2026-06-29 — post-vendor live test | Fired 15 ambiguous prompts after vendoring `outsystems-plan-to-mentor`. 13/15 catalog skills fired as expected; the 2 surprises (T9, T10) were conductor commands (`demo-prep`, `change-planner`) shadowing catalog skills — by design. Catalog trigger surfaces confirmed sharp. Added the "Conductor commands" section above to document the shadow relationship |

---

## Pre-vendor checklist (for adding new skills)

Before vendoring any new skill into this catalog:

- [ ] Identify the SINGLE input/intent it owns. Add it to the table above.
- [ ] Check the table for trigger overlap with existing skills.
- [ ] If overlap exists, tighten BOTH sides — the new skill AND the existing one. Add Routing Boundary cross-references.
- [ ] Live-test 3-5 ambiguous prompts that could match either skill. Verify the right one fires.
- [ ] Update this map with the audit date + outcome.

When this checklist isn't followed, expect: agent picks the wrong skill, inconsistent triggering across sessions, user confusion. Past field reports (Rui's polling-behavior, João's dependency-impact triggering) show the cost of skipping it.
