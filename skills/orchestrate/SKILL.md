---
name: orchestrate
description: >-
  Generic, portable orchestration router with a tiered complexity architecture.
  Refines the request, DISCOVERS the skills installed in the environment (and
  searches/installs missing ones), detects the right tier (0-3), then DELEGATES
  execution to subagents — it never executes code itself. Use when a task needs
  routing/decomposition across multiple steps or domains, when you want a
  template-driven pipeline, a planned multi-wave build, or a custom validated
  workflow. Triggers: "orchestrate", "route this task", "plan and build",
  "multi-step", "which tier", "run a workflow/template".
argument-hint: "[task] [-s|--simple] [-p|--plan] [-c|--custom] [-d|--detect] [-t|--template NAME]"
---

# orchestrate — generic tiered orchestration router

This skill is **self-contained and portable**: every dependency it needs lives
inside `./skills/` (bundled skills) and `./agents/` (optional helper agents).
It makes **no assumption** about a specific stack, agent registry, or directory
layout. Where a capability is missing in the host environment, it **discovers,
searches and installs** the right skill instead of hard-coding one.

## Mandatory rules (read first)

- 📋 **You are a ROUTER, not an executor.** Detect → delegate. Never write code
  directly.
- 🛑 Run **STEP 0 (prompt refinement)** before anything else, except `--simple`.
- 🛑 Run **STEP 0.5 (skill discovery)** before delegating, so each step uses the
  best available (or newly installed) skill.
- 🛑 Detect the **tier** when no flag is given; honor an explicit flag otherwise.
- 🛑 **TIER_3** requires explicit human validation (AskUserQuestion) before it runs.
- 🛑 Never auto-add a custom workflow to the template catalog.
- ✅ Delegate TIER_1/2/3 execution to an **orchestration subagent**; TIER_0 may
  delegate to a single subagent directly.

## Bundled dependencies (all inside this skill — no external install required)

| Path | Role |
|------|------|
| `./skills/prompt-creator/` | STEP 0 — refine/disambiguate the raw request |
| `./skills/find-skills/` | STEP 0.5 — **search** the skills ecosystem (`npx skills find`) |
| `./skills/skill-installer/` | STEP 0.5 — **install/validate** a skill locally |
| `./skills/meta-workflow-rl/` | TIER_1/2 — template engine + YAML pipeline catalog (`./skills/meta-workflow-rl/templates/`) |
| `./skills/parallel-workers/` | Parallel ad-hoc decomposition (alternative executor) |
| `./agents/` | Optional helper agents: `step-orchestrator`, `impact-analyzer`, `regression-guard`. Install into your agent registry to enable the full protection workflow; otherwise generic subagents stand in (see "Genericity" below). |

## Genericity — how this differs from a stack-specific orchestrator

This version replaces every environment-specific assumption with a portable one:

| Original (coupled) | Generic (this version) |
|--------------------|------------------------|
| Hard-coded agents (`backend-laravel`, `frontend-react`, …) | **Discovered skills** + generic subagents (`general-purpose`, `Explore`, `Plan`) |
| Required custom agents `impact-analyzer` / `regression-guard` | Optional: bundled in `./agents/`, else a `general-purpose` subagent runs the same review prompt |
| Absolute paths `~/.claude/skills/…` | Relative paths `./skills/…` inside this skill |
| Session folder `.claude/{SESSION}/` | Workspace-relative `./.orchestrate/{SESSION}/` |
| Assumes templates pre-installed | Templates bundled; missing capabilities are **searched & installed** |

---

## STEP 0 — Prompt refinement (bundled `prompt-creator`)

Mandatory unless `--simple`. Invoke the bundled skill:

```
Skill(skill: "prompt-creator", args: "<raw user request>")
```

It returns: clarified **context**, a precise **task**, explicit **requirements**
(constraints, edge cases), and measurable **success criteria**. The refined
request replaces the raw one for every later step.

## STEP 0.5 — Skill discovery & install (bundled `find-skills` + `skill-installer`)

Before delegating, resolve the capabilities each step needs:

```
1. INVENTORY  — list the skills available in the host environment
               (the session's available-skills list).
2. MATCH      — for each capability the task needs (e.g. "postgres",
               "accessibility audit", "stripe"), is there an installed skill?
3. IF MISSING — SEARCH the ecosystem with the bundled find-skills skill:
                  npx skills find "<capability>"
                then INSTALL the best match:
                  npx skills add <package>        (ecosystem)
                or use ./skills/skill-installer/   (local validate + register)
4. RE-CHECK   — confirm the skill is now available; record it in the plan.
```

Rules: never invent a skill name — only use a skill that the inventory or a
successful install confirms exists. If a capability cannot be found or
installed, fall back to a generic subagent (`general-purpose`) and **say so**.

---

## Tiered architecture

```
            /orchestrate [task]
                   │
          STEP 0  prompt-creator        (skip if --simple)
                   │
          STEP 0.5 skill discovery/install
                   │
            FLAG / TIER DETECTION
   --simple→T0   --template→T1   --plan→T2   --custom→T3   else→detect
        │            │              │            │
        ▼            ▼              ▼            ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ TIER_0 │  │ TIER_1   │  │ TIER_2   │  │ TIER_3   │
   │ direct │  │ template │  │ planned  │  │ custom   │
   │ subagt │  │ pipeline │  │ +master  │  │ +human   │
   └────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Tier detection (no flag)

Score the **refined** request on: `domains_count`, `complexity (0-100)`,
`ambiguity (low/med/high)`, `template_match (0-1)`.

| Result | Tier |
|--------|------|
| 1 domain, complexity < 20, ambiguity low | **TIER_0** |
| `template_match > 0.8` | **TIER_1** |
| complexity 20-70, ambiguity ≠ high, no strong template | **TIER_2** |
| complexity > 70 or ambiguity high | **TIER_3** |

`--detect` / `-d` prints the recommended tier and metrics **without** executing.

### TIER_0 — simple (direct delegation)

One atomic task → delegate to a single subagent. No master plan, no protection.
Pick the executor by discovery: a matching installed skill, else a generic
subagent.

```
Task(subagent_type: "<discovered-skill-agent or general-purpose>",
     prompt: "<refined task>")
```

### TIER_1 — template pipeline (bundled `meta-workflow-rl`)

Run a catalog pipeline from `./skills/meta-workflow-rl/templates/`:

```
Skill(skill: "meta-workflow-rl", args: "<template-name>")
```

Browse templates in that folder (feature-dev, security-audit, db-postgresql,
seo-audit, deploy-production, …). Protection runs before/after (see below).

### TIER_2 — planned (master plan)

1. Generate a master plan (template `create-master-plan`) →
   `./.orchestrate/{SESSION}/L0_MASTER_PLAN.md`.
2. Protection BEFORE.
3. Execute the plan wave by wave via the orchestration subagent; launch
   unblocked waves as their blockers complete.
4. Protection AFTER. Final report with metrics.

### TIER_3 — custom (human-validated)

1. Analyze deeply, generate a bespoke YAML workflow.
2. **AskUserQuestion** showing the YAML — require approval before running.
3. Protection BEFORE → execute → protection AFTER → report.
4. Never auto-save to the catalog (only on explicit request).

---

## Execution & protection (portable)

**Delegate, never execute.** TIER_1/2/3 go through an orchestration subagent;
prefer the bundled `step-orchestrator` agent if installed, otherwise a
`general-purpose` subagent given the pipeline as its brief.

**Protection workflow** (TIER_1+), portable:

```
BEFORE: impact review  — agent "impact-analyzer" if installed,
                          else general-purpose subagent prompted to assess
                          blast radius, dependencies, regressions.
... work ...
AFTER:  regression review — agent "regression-guard" if installed,
                          else general-purpose subagent prompted to run/inspect
                          tests and confirm no regressions.
```

TIER_0 skips protection.

### Pipeline YAML schema

```yaml
name: "workflow-name"
description: "what it does"
protection: { before: impact-analyzer, after: regression-guard }   # or generic
skills_global: [clean-code, review-code]
steps:
  - name: "Step"
    agent: <discovered-skill or generic subagent>
    skills: [skill1, skill2]
    task: "what to do"
    output: "deliverable"
    validation: "success criteria"
    rollback: "if failed"
    depends_on: ["Previous Step"]
```

---

## Invocation examples

```bash
/orchestrate -s "Add a phone field to the Contact model"      # TIER_0
/orchestrate -t security-audit                                # TIER_1 (template)
/orchestrate -p "Implement pagination on the /users API"      # TIER_2 (plan)
/orchestrate -c "Migrate REST to GraphQL"                     # TIER_3 (custom)
/orchestrate -d "Refactor the payment module"                # detect only
```

## Success metrics

✅ Prompt refined (unless `--simple`) and the refined prompt drives every step.
✅ Skill discovery ran; missing capabilities searched & installed, or a generic
fallback was used **and disclosed**.
✅ Correct tier detected (or flag honored).
✅ TIER_1+ delegated to an orchestration subagent with protection before/after.
✅ TIER_3 validated by a human before running.
✅ No direct code execution — everything delegated. Session folder created.

## Failure modes

❌ Skipping prompt refinement / skill discovery. ❌ Going "free style" past tier
detection. ❌ Executing code instead of delegating. ❌ Inventing a skill name
instead of discovering/installing it. ❌ Running TIER_3 without human approval.
❌ Auto-adding custom workflows to the catalog.

## See also

- `./skills/meta-workflow-rl/` — template engine & catalog.
- `./skills/find-skills/` + `./skills/skill-installer/` — discover & install.
- `./skills/prompt-creator/` — request refinement.
- `./skills/parallel-workers/` — alternative parallel executor.
- `./agents/` — optional protection/orchestration agents.
