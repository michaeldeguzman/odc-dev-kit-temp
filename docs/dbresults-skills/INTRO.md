# What is this catalog and how do I use it?

A plain-English brief for solution architects, developers, customers, and anyone testing the OutSystems MCP skills. Skim it once, then jump to the section that matters for your job.

> [!WARNING]
> 🧪 **Prototype — internal experimentation only.** Skills may fail in surprising ways on your tenant. Treat outputs as drafts to review. Don't use in customer-facing production work.

---

## The 10-second pitch

A set of **10 small AI workflows + 1 optional companion** that you can use inside Claude Code to turn common OutSystems jobs into a one-line ask.

Instead of clicking through ODC Portal, opening five docs tabs, and assembling things by hand, you say *"show me the architecture of Banking Portal"* or *"build this Figma as an app"* — and the skill drives the OutSystems MCP server through the multi-step dance for you.

Think of it like keyboard shortcuts for OutSystems work: each skill is a shortcut for a job you'd otherwise do manually.

---

## What it's for, by job

### 👀 When you want to **understand** what's already there

| Skill | What it does | When you'd use it |
|---|---|---|
| **Tenant Architecture** | Maps every asset in your tenant (apps, agents, libraries, connections) onto one interactive page | Onboarding a new team. *"What's actually in here?"* |
| **App Architecture** | Zooms into one app and shows its screens, actions, data model, roles, dependencies as an interactive map | Debugging an app you didn't build. Quarterly review. Designer joining the project |
| **App Documentation** | Writes a clean Markdown wiki page for an app — drop-in for Confluence / Notion / a README | Compliance asks "where's the doc?" New hire joining. Customer wants a handoff package |
| **AI Agent Landscape** | Dashboards every AI agent + model connection in your tenant: who's using what, Trial vs Customer entitlements, suspicious "test" agents | Quarterly AI governance review. *"What's our AI footprint costing us?"* Spotting test agents that drifted into prod |
| **Dependency Impact** | Answers *"who would break if I publish this library?"* across the whole tenant | Right before publishing a shared library or agent. Pre-deploy risk check |

### 🛠️ When you want to **build or extend** an app

> [!IMPORTANT]
> **About the "build an app" wording.** These skills use ODC Mentor to bootstrap a structured app from a spec or design. **Mentor is officially positioned for in-flow edits to existing apps** — using it to scaffold an app end-to-end from a spec or design is an experimental pattern these skills layer on top. Output quality varies with spec detail. Treat every Mentor-built app as a draft starting point for human review and iteration — **not a ship-ready artifact, and not an officially supported "design-to-app" or "spec-to-app" workflow.**

| Skill | What it does | When you'd use it |
|---|---|---|
| **Design-to-App** | Take a **visual** design source (Figma URL, screenshot, HTML mockup) — generate a working OutSystems app from it | Designer handed you a Figma. Customer demo prep where you need a real, clickable result from a static design |
| **Spec-Driven Build** | Build a new app from a **text-only** structured markdown spec — interview mode, file mode, or clone-from-example. No design source needed | You know functionally what you want, no design yet. RFP responses. Internal tool |
| **Plan-to-Mentor** | Coverage-review an EXISTING saved plan (from `superpowers:writing-plans`, our Spec-Driven Build, or a hand-written planner) against its source PRD. Patches gaps, produces Mentor-ready prompts. The "agentic-coding-for-OutSystems" track entry-point | Senior dev workflow: PRD → plan → coverage check → Mentor. Use when you have a saved plan file in hand and want to make sure no requirements got dropped before firing Mentor |
| **Mentor Co-Pilot** | A menu of 11 ready-to-go Mentor tasks: quality review, security review, accessibility audit, demo-readiness check, test generation, add-a-feature, model migration, demo data, refactor suggestions, docs gap fill | You want Mentor to do a standard job on an EXISTING app, without writing a prompt yourself |
| **Custom Code** | The canonical recipe for building a C# library that ODC apps can call (External Logic) — SDK attributes, runtime limits, testing, deploy | You need something OutSystems' built-in patterns can't do natively (specific protocol, perf-critical math, exotic library) |

### 🚀 When you want to **ship, validate, or document**

| Skill | What it does | When you'd use it |
|---|---|---|
| **Deploy Preview** | Shows a risk preview of a Dev→Test or Test→Prod promotion before you click Deploy | About to push to Prod. Want a sanity check. Spotting *"I haven't seen this since revision 50"* moments |
| **App Documentation** | (Same as above, also lands here) | Compliance, handoff, audit trail |

### 🧰 Optional companion — wraps every Mentor invocation

| Skill | What it does | When you'd use it |
|---|---|---|
| **Mentor Polling Behavior** ⬡ | When installed, this skill becomes the **way you run any Mentor task** — it bundles the Mentor invocation, polling discipline (cuts ~99% of intermediate poll responses), and per-session telemetry into one flow. After your Mentor work, you can ask for a dashboard showing every session this skill recorded (duration, cost proxy, trends) | You run Mentor regularly and want to know *"is this getting better? Cheaper? Slower? What's failing?"*. **It's NOT a background recorder** — telemetry is captured only when you do Mentor work through this skill. Non-Mentor skills (deploy-preview, architecture, etc.) don't generate telemetry because they don't invoke Mentor |

---

## Value, in one line each

| For… | The value is… |
|---|---|
| **Solution architects** | Two clicks instead of two hours to map a tenant or audit AI usage |
| **Developers** | *"Run mentor to do X"* without writing the prompt — the library encodes what works |
| **Customers running demos** | A working demo app from a Figma — no manual translation tax |
| **Anyone shipping** | A risk preview before Prod promotion — catches surprises before they bite |
| **Tech leads** | One source of truth for app architecture, exportable as Markdown for review |
| **Anyone running Mentor at scale** | Mentor sessions that cost ~30× fewer poll-responses + a dashboard to spot trends |

---

## How to trigger the skills

### The short version

After install, just **ask Claude Code what you want in plain English.** Claude reads your message, compares it to each installed skill's description, and picks the matching one automatically. No `/slash-command`, no menu, no manual selection.

The trick is that each skill's description includes the natural-language phrases you'd actually use. So when you say *"show me the architecture of Banking Portal"*, Claude matches that to the App Architecture skill's trigger list and runs it.

### The 5-step first-time path

| Step | What you do | What you see |
|---|---|---|
| 1 | Install the skills (one command, see [Installation](#how-to-install) below) | Files copied to `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex CLI) |
| 2 | **Restart your agent** (critical — the harness only reads skill descriptions at startup) | Fresh session |
| 3 | Register the OutSystems MCP server for your tenant (one line in `claude mcp add`) | MCP server appears in `/mcp` list |
| 4 | First time you ask anything OutSystems, your agent says *"the outsystems MCP needs authentication"* and gives you a URL | You open the URL in your browser, click Authorize |
| 5 | After auth, the MCP's real tools become available and skills can run | You ask anything OutSystems and it just works |

The auth flow is one-time per session (tokens expire after a while; Claude will ask you to re-auth if needed).

### Trigger phrase cheat sheet

Each skill has a list of trigger phrases baked into its description. Here's the menu — say any of these and the matching skill fires:

| Skill | Phrases that trigger it |
|---|---|
| **Tenant Architecture** | *"show me my tenant"* · *"tenant overview"* · *"architecture diagram"* · *"what's in my tenant"* · *"show me my apps"* |
| **App Architecture** | *"architecture of [app]"* · *"show me [app]"* · *"explore [app]"* · *"what's inside [app]"* · *"give me an overview of [app]"* |
| **App Documentation** | *"document [app]"* · *"generate docs for [app]"* · *"write up [app]"* · *"compliance docs for [app]"* · *"create documentation for [app]"* |
| **AI Agent Landscape** | *"AI inventory"* · *"audit my AI"* · *"what AI is in my tenant"* · *"show me my agents"* · *"which models are we using"* |
| **Dependency Impact** | *"who depends on [library]"* · *"if I publish [library] who breaks"* · *"blast radius of [library]"* · *"library impact"* · *"dependency audit"* |
| **Deploy Preview** | *"deploy preview"* · *"is it safe to promote [app] to [env]"* · *"what would change if I deploy [app] to [env]"* · *"show me the deploy plan for [app]"* |
| **Design-to-App** | *"build this Figma in OutSystems"* · *"design to model"* · *"generate a screen from this mockup"* · *"build this design"* — or just paste a Figma URL / image path / HTML file and say *"turn this into an app"* |
| **Spec-Driven Build** | *"build a new app from this spec"* · *"generate an app from these requirements"* · *"create [app] from scratch"* · *"build app from scratch"* |
| **Mentor Co-Pilot** | *"have Mentor audit [app]"* · *"have Mentor review [app]"* · *"use Mentor to [add feature / generate tests / etc.]"* · *"Mentor demo readiness"* · or just name the task ID (e.g., *"run security-review on Banking Portal"*) |
| **Custom Code** | *"build a C# library for OutSystems"* · *"ODC external logic"* · *"write custom code for ODC"* · *"deploy an external library"* |
| **Mentor Polling Behavior** ⬡ | **To run a Mentor task** *with* discipline + telemetry: *"use Mentor on [app] to do X"* · *"have Mentor add a button to my Profile screen"* · *"run Mentor on [app] to generate tests for [action]"* (any Mentor request — polling-behavior auto-attaches). **To see the dashboard AFTER you've done Mentor work**: *"generate the Mentor polling dashboard"* · *"show me my Mentor report"*. **For cross-session trends**: *"Mentor session summary"* · *"how is Mentor performing"*. ⚠️ The skill only records what runs *through* it — if you do non-Mentor work (deploy-preview, architecture, etc.) the dashboard for that session will be empty |

You don't need to memorize these. Claude is pretty forgiving — describe the job in your own words and the right skill usually fires.

### When Claude picks the wrong skill

**Force a specific skill by naming it.** Just say its full name in your prompt:

> *"Use `outsystems-design-to-app` to turn this Figma into an app: https://figma.com/..."*

That overrides whatever Claude would have picked from the trigger phrases.

**Or list what's available.** Type:

> *"What outsystems skills do I have installed?"*

Claude will list them with a one-line summary each.

### Confirmation gates — some skills check before spending money

A few skills cost real money (the Mentor-driven ones can be $1–$15 per run). They have built-in safety gates:

- **Design-to-App / Spec-Driven Build / Mentor Co-Pilot**: before firing Mentor, they show you a summary of what they're about to do + the rough cost, and ask *"go / cancel?"*. You pick "go" via the on-screen question — nothing fires until you confirm.
- **Dependency Impact**: same idea. Before scanning a large tenant (9-25 min), it asks *"continue?"*. Smaller tenants get a smaller ETA and the same gate.
- **Tenant Architecture** (large tenants): if your prompt is ambiguous about whether you want just the tenant view OR every app deep-dived, it asks which.

If you say "no / cancel", nothing happens and no money is spent.

### Common gotchas

| Gotcha | Fix |
|---|---|
| You installed a skill but Claude doesn't seem to know it | You forgot to restart Claude Code. The harness reads skill descriptions at session start only |
| Claude picks the wrong skill | Name the one you want: *"Use `outsystems-spec-driven-build` to..."* |
| Skill fires but says *"MCP server requires authentication"* | The OAuth token expired (every few minutes mid-session). Just say *"authorize the OutSystems MCP"* and follow the browser prompt |
| Skill seems stuck mid-run | The Mentor-driven skills can take 5-15 min. You'll see progress lines (*"Progress: 42/150 scanned"*). If totally silent for 60+ seconds, ctrl-C is safe — most skills cache partial work and resume |
| You want to skip a confirmation gate | You can't — by design. Cost-spending skills always require an explicit "go" |

---

## What this isn't (set expectations)

- **Not a product.** Internal R&D prototype catalog. May be rewritten, reorganized, or deleted at any time.
- **Not for customer-facing production work.** Skills can fail in unexpected ways on your specific tenant. Treat outputs as drafts to review.
- **Not an officially supported greenfield-app generator.** The "build an app" skills drive Mentor for a use case Mentor isn't officially positioned for (Mentor is for in-flow edits to existing apps). What you get is an experimental scaffold to review and refine, not a finished app.
- **Not free for everyone.** The visualization / documentation skills cost cents per run. The Mentor-driven ones (Design-to-App, Spec-Driven Build, Mentor Co-Pilot) can cost **$1–15 per build** depending on app complexity.
- **Claude Code and Codex CLI only.** Both are validated. Claude Code is materially cheaper on the first pass for large-MCP skills (Mentor, tenant scans, Figma extracts) because its harness auto-saves oversized MCP responses to disk; Codex receives the same payloads inline, so first-run cost is higher. On cached re-runs, cost is equivalent. Other harnesses (VS Code + Copilot, Kiro, Cursor, Windsurf, Continue.dev) don't work cleanly — we've seen real money burned trying to force them onto the wrong harness.

---

## How to install

Quick path (pick your agent's skills directory):

**Claude Code** — `~/.claude/skills/`:
```bash
git clone https://github.com/denwx/outsystems-mcp-skills.git
cd outsystems-mcp-skills
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

**Codex CLI** — `~/.agents/skills/` (note: `~/.codex/skills/` is deprecated, don't use it):
```bash
git clone https://github.com/denwx/outsystems-mcp-skills.git
cd outsystems-mcp-skills
mkdir -p ~/.agents/skills
cp -R skills/* ~/.agents/skills/
```

Then restart your agent and ask anything OutSystems — the agent will walk you through the OAuth dance the first time.

Or just tell your agent to install for you — e.g. *"Clone https://github.com/denwx/outsystems-mcp-skills and copy `skills/` into my `~/.claude/skills/` folder"* (swap the path for `~/.agents/skills/` on Codex).

Full prereqs and the MCP-add command are in the [README](../README.md).

---

## Feedback

This is the whole point. Three lightweight ways:

1. **Found a bug?** → [Open a Bug report](https://github.com/denwx/outsystems-mcp-skills/issues/new?template=bug-report.yml). What you tried, what happened, what you expected.
2. **Tried a skill and have a verdict?** → [Open a Skill feedback issue](https://github.com/denwx/outsystems-mcp-skills/issues/new?template=skill-feedback.yml). 30 seconds: 👍 / 👎 / 🤷 + would-use-again + a one-line comment.
3. **Have an idea for a new skill?** → [Open an Idea issue](https://github.com/denwx/outsystems-mcp-skills/issues/new?template=idea.yml). Tell us the literal sentence you wish you could say.

For open-ended chat (*"is anyone else seeing this?"*, *"what should we build next?"*, install help, war stories) → use Slack: `#agent-experience-internal-testing`.

**There is no "correct" feedback.** *"I tried this and it wasn't useful"* is as valuable as *"this is amazing."* What we want is your honest read.

---

**Maintainer:** Deniz Arin, OutSystems R&D · **License:** MIT
