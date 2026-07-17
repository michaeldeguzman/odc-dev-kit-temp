# Cursor portability — Phase 1 tests

**Goal:** Validate 6 technical assumptions about Cursor's behavior before we invest in porting any skill. Each test confirms or falsifies one architectural assumption. The answers determine the whole adapter design.

**Who runs this:** Deniz (Cursor user, ~30-60 min total).

**How to report back:** Either fill in the `RESULT:` block under each test, OR just paste findings into chat. Per-test answers are independent — partial results are useful.

**Setup once before starting:**

1. Have Cursor installed and signed in.
2. Have the `outsystems` MCP server registered in Cursor (Cursor → Settings → MCP, same `claude mcp add ...` URL transformed to Cursor's config format).
3. Have a tenant connected — `one26-legacymod` is fine; any tenant with ≥150 assets is fine for Test 1 specifically.
4. Open a fresh Cursor chat / Compose session for each test (avoid context pollution).

---

## Test 1 — The cornerstone: MCP large-response handling 🔴

**Why it matters:** This single behavior determines whether porting makes economic sense. Claude Code's harness auto-saves any MCP tool result over ~25 KB to disk and sends only the file path to the model. Without this, every large MCP response inflates context 5-50×.

**The hypothesis:** Cursor does NOT auto-save. Large MCP responses get fully injected into the conversation context (= much more expensive).

**How to test:**

1. Fresh Cursor chat.
2. Authenticate the outsystems MCP if not already (Cursor should prompt OAuth on first MCP call).
3. Ask the agent verbatim:

   > *"Call `mcp__outsystems__app_list` with `limit: 1000`. Then tell me whether the result was saved to a file or injected into your context. Show me the first 100 characters of how it arrived."*

4. Observe how Cursor surfaces the result.

**What to look for:**

- ✅ **Hypothesis falsified (best case):** Cursor shows a *"Output saved to /tmp/..."* notice or similar disk-spill indicator. Agent reads from disk, not from context.
- ❌ **Hypothesis confirmed (likely):** Agent receives the full JSON in-line. Conversation token count jumps by ~50-150 KB equivalent. No "saved to file" message.
- ⚠️ **In between:** Maybe Cursor truncates? Or pages? Note the exact behavior.

**Why I'm asking:** if Cursor DOES auto-save → adapter is much simpler. If it DOESN'T → adapter needs to wrap every large-response MCP call in a Bash `python3 -c "..."` pipe-to-disk pattern, which is more invasive.

**RESULT:** _________________

---

## Test 2 — `.mdc` rule discovery via description matching

**Why it matters:** Claude Code skills auto-fire on natural-language prompts matching their description. Cursor's `.cursor/rules/*.mdc` system has a `description` field too, but it's unclear how aggressively Cursor uses it for auto-include vs requiring `@`-mentions.

**The hypothesis:** Cursor auto-includes `.mdc` rules whose `description` field matches the user's prompt — similar to Claude Code but possibly less aggressive.

**How to test:**

1. Create `~/.cursor/rules/test-trigger.mdc` (or workspace-level `.cursor/rules/`) with:

   ```markdown
   ---
   description: Use when the user asks about cats or felines or kittens
   alwaysApply: false
   ---

   When this rule fires, respond with: "🐱 CAT RULE ACTIVE — your prompt matched my description"
   ```

2. Fresh Cursor chat. Type:

   > *"tell me something interesting about cats"*

3. Observe: Did the agent's response include the *"CAT RULE ACTIVE"* string?

4. Now try ambiguity:

   > *"what should I get my partner for their birthday"*

5. Observe: Did the rule fire incorrectly?

**What to look for:**

- ✅ **Best case:** Rule fires when prompt clearly matches the description, doesn't fire on unrelated prompts.
- ⚠️ **Moderate:** Rule only fires when `@test-trigger` is explicitly mentioned, OR fires on too many prompts (over-triggering).
- ❌ **Bad case:** Description field is ignored entirely; rules need explicit invocation.

**Why I'm asking:** if Cursor auto-fires on description → we can port SKILL.md descriptions almost 1:1 to `.mdc` files. If not → we need an explicit-invocation pattern.

**RESULT:** _________________

---

## Test 3 — Can `.mdc` rules invoke MCP tools?

**Why it matters:** Our skills are 80% about driving MCP tool calls. If `.mdc` rules can only inject context (not direct tool use), the porting model changes significantly.

**The hypothesis:** `.mdc` rules can describe procedures that include MCP tool calls; the agent follows the procedure and invokes the tools.

**How to test:**

1. Create `~/.cursor/rules/test-mcp.mdc`:

   ```markdown
   ---
   description: Use when the user asks "what tenant am I on" or "tenant id"
   alwaysApply: false
   ---

   Call `mcp__outsystems__auth_status` and report the `tenant_id` from the response. Format: "Tenant: <tenant_id>".
   ```

2. Fresh chat. Type:

   > *"what tenant am I on"*

3. Observe: Did the agent invoke `mcp__outsystems__auth_status` and return a real tenant ID?

**What to look for:**

- ✅ **Best case:** Agent calls the MCP tool, parses the response, reports the tenant_id. Just works.
- ⚠️ **Moderate:** Agent asks permission to call the tool (acceptable; matches Claude Code's permission model).
- ❌ **Bad case:** Agent says it "can't" or echoes the rule text without calling the tool.

**RESULT:** _________________

---

## Test 4 — Multi-step procedures

**Why it matters:** Our SKILL.md files have numbered procedures (Step 1, Step 2, Step 3...). Does Cursor follow them, or does it improvise?

**The hypothesis:** Cursor follows numbered procedures reasonably well, especially when they're stated explicitly.

**How to test:**

1. Create `~/.cursor/rules/test-steps.mdc`:

   ```markdown
   ---
   description: Use when the user says "run the test procedure"
   alwaysApply: false
   ---

   Execute these steps IN ORDER. Do NOT skip or reorder.

   ### Step 1
   Output verbatim: `[STEP 1 DONE]`

   ### Step 2
   Output verbatim: `[STEP 2 DONE]`

   ### Step 3
   Output verbatim: `[STEP 3 DONE]`

   ### Step 4
   Output a summary: "Procedure complete. 3 steps executed in order."
   ```

2. Fresh chat. Type: *"run the test procedure"*

3. Observe: Did the agent output `[STEP 1 DONE]`, then `[STEP 2 DONE]`, then `[STEP 3 DONE]`, then the summary, in that order?

**What to look for:**

- ✅ **Best case:** All 4 outputs in order. Procedure followed faithfully.
- ⚠️ **Moderate:** Steps execute but get summarized or merged (e.g., agent says "I executed all 3 steps" without the verbatim markers).
- ❌ **Bad case:** Steps reorder, skip, or get rewritten.

**RESULT:** _________________

---

## Test 5 — Confirmation-gate UX

**Why it matters:** Three of our skills (`outsystems-spec-driven-build`, `outsystems-design-to-app`, `outsystems-dependency-impact`) have explicit confirmation gates before they spend money on Mentor or before they start a long-running scan. Claude Code uses `AskUserQuestion` for these — surfaces a multi-choice UI. What does Cursor offer?

**The hypothesis:** Cursor doesn't have a native multiple-choice question UI. The agent just asks in text and waits for the user's reply.

**How to test:**

1. Create `~/.cursor/rules/test-gate.mdc`:

   ```markdown
   ---
   description: Use when the user asks to "start the gate test"
   alwaysApply: false
   ---

   STOP. Before doing anything else, ask the user this question and WAIT for their answer:

   "I'm about to do a fake expensive thing. Do you want to proceed? Reply with 'yes' or 'no'."

   ONLY proceed when the user answers. If yes, output "Proceeding". If no, output "Cancelled".
   ```

2. Fresh chat. Type: *"start the gate test"*

3. Observe how the question is surfaced:
   - Is it just text in chat (you type "yes" / "no" as a normal reply)?
   - Does Cursor render any kind of interactive widget?
   - Does the agent reliably wait for your reply, or does it keep going?

4. Reply with "yes" and verify it proceeds. Restart, reply "no", verify it cancels.

**What to look for:**

- ✅ **Reliable text-based gate:** Agent waits, accepts your reply, proceeds correctly. We can port the gates as plain-text questions.
- ⚠️ **Cursor has its own widget:** Note what it looks like; we adapt.
- ❌ **Agent doesn't wait:** Major problem — gates don't work; we'd need a different pattern.

**RESULT:** _________________

---

## Test 6 — Subprocess execution (Bash equivalent)

**Why it matters:** Our skills run Python scripts via Bash (`python3 scripts/build.py ...`). If Cursor has no Bash equivalent or it requires per-command approval, the UX differs significantly.

**The hypothesis:** Cursor has a built-in terminal / shell tool. The agent can run subprocesses, possibly with permission prompts.

**How to test:**

1. Fresh chat. Type:

   > *"Run `python3 -c \"import sys; print(sys.version)\"` and tell me what version it printed."*

2. Observe:
   - Did Cursor execute the command?
   - Did it ask for permission first?
   - Did it show the output?

3. Also try (in a separate fresh chat):

   > *"List the files in `~/.cursor/rules/` using a shell command."*

4. Observe: Does this work? Is there a permission model?

**What to look for:**

- ✅ **Works similarly to Claude Code:** Agent runs commands, may ask first time. Output visible.
- ⚠️ **Permission heavy:** Every command requires approval (annoying but workable).
- ❌ **No subprocess support:** Can't run Python directly; we'd need a wrapper.

**RESULT:** _________________

---

## After you finish

Drop the results back in chat (just paste, no need for formal structure). Based on what you find, I'll either:

- **All 6 hypotheses good** → write the full architecture spec + draft the first `tenant-architecture/cursor/` adapter
- **Some hypotheses fail** → revise architecture to compensate, OR re-scope the port
- **Cornerstone (Test 1) is unfavorable AND we can't work around it** → honestly recommend pausing the Cursor port; the economics may not work

The biggest tell is Test 1. If Cursor auto-saves large MCP responses, this is mostly a packaging problem. If it doesn't, we have to decide whether to push through with explicit disk-piping in every adapter or accept that Cursor users will pay 3-10× more per skill run.

## Quick reference — what's in scope

| Skill | Port target | Why this one |
|---|---|---|
| `outsystems-tenant-architecture` | ✅ Phase 1 first adapter | Simplest: 2 MCP calls (`app_list`, `env_list`), single render step, no Mentor, no AskUserQuestion in the critical path |
| `outsystems-app-architecture` | ✅ Phase 1 second adapter | More complex: 6 parallel context_* calls + AskUserQuestion gate. Tests the multi-call + gate patterns |
| `outsystems-dependency-impact` | ✅ Phase 1 third adapter | Tests the long-running scan pattern + AskUserQuestion gate + throttle discipline |

All three are pure-MCP, no Mentor. We're not touching Mentor-driven skills in Phase 1 — those have their own polling complexity that's orthogonal to harness portability.
