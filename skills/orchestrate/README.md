# orchestrate — generic tiered orchestration router

A **portable, self-contained** orchestration skill. It refines a request,
discovers the skills available in the environment (searching and installing
missing ones), picks the right complexity **tier**, and **delegates** execution
to subagents. It is a router — it never executes code itself.

> This is a generic rewrite of a stack-specific orchestrator: all hard-coded
> agents, absolute paths, and environment assumptions have been removed and
> replaced with skill discovery + generic subagents. Every dependency it needs
> is bundled inside this folder, so it runs anywhere with no external setup.

## What it does

```
request → refine (prompt-creator)
        → discover & install needed skills (find-skills + skill-installer)
        → detect tier (0–3)
        → delegate execution (+ optional protection)
        → report
```

| Tier | Trigger | Behavior |
|------|---------|----------|
| **TIER_0** simple | `--simple` / atomic task | Delegate to one subagent. No plan, no protection. |
| **TIER_1** template | `--template NAME` / strong template match | Run a YAML pipeline from the bundled `meta-workflow-rl` catalog. |
| **TIER_2** planned | `--plan` / medium complexity | Generate a master plan, execute wave by wave, protect before/after. |
| **TIER_3** custom | `--custom` / high complexity or ambiguity | Generate a bespoke workflow, **require human approval**, then run. |

## The discovery & install step (STEP 0.5)

Before delegating, `orchestrate` resolves the capabilities a task needs:

1. **Inventory** the skills installed in the host environment.
2. **Match** each needed capability to an installed skill.
3. If **missing**, search the ecosystem with the bundled `find-skills`
   (`npx skills find "<capability>"`) and install the best match
   (`npx skills add <package>` or the local `skill-installer`).
4. **Re-check**, then use it. If nothing can be found/installed, fall back to a
   generic subagent and disclose it.

This is what makes the router portable: it never assumes a fixed set of
domain agents — it finds or installs what each task requires.

## Layout

```
orchestrate/
├── SKILL.md            # the orchestration logic (router)
├── README.md           # this file
├── skills/             # bundled dependency skills (no external install needed)
│   ├── prompt-creator/     # STEP 0  — request refinement
│   ├── find-skills/        # STEP 0.5 — search the skills ecosystem
│   ├── skill-installer/    # STEP 0.5 — install/validate a skill locally
│   ├── meta-workflow-rl/   # TIER_1/2 — template engine + YAML catalog (templates/)
│   └── parallel-workers/   # alternative parallel executor
└── agents/             # OPTIONAL helper agents (install into your agent registry)
    ├── step-orchestrator.md   # pipeline executor
    ├── impact-analyzer.md     # protection BEFORE
    └── regression-guard.md    # protection AFTER
```

## Install & use

The skill is self-contained. To use it as a personal skill, place this
`orchestrate/` folder under your agent's skills directory (e.g.
`~/.claude/skills/orchestrate/`).

The bundled `agents/*.md` are **optional**: copy them into your agent registry
(e.g. `~/.claude/agents/`) to enable the full protection/orchestration workflow.
Without them, `orchestrate` falls back to generic subagents that run the same
review prompts.

```bash
/orchestrate -s "Add a phone field to the Contact model"   # TIER_0
/orchestrate -t security-audit                             # TIER_1 template
/orchestrate -p "Implement pagination on the /users API"   # TIER_2 plan
/orchestrate -c "Migrate REST to GraphQL"                  # TIER_3 custom
/orchestrate -d "Refactor the payment module"              # detect only
```

## Notes

- **Router, not executor** — it detects and delegates; it does not write code.
- **TIER_3 always asks for human approval** before running a custom workflow.
- **Templates** live in `skills/meta-workflow-rl/templates/` (feature-dev,
  security-audit, db-postgresql, seo-audit, deploy-production, …).
- Session artifacts are written under a workspace-relative `./.orchestrate/`.
