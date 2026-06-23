---
name: parallel-workers
description: Orchestration distribuee avec decomposition automatique et workers paralleles
argument-hint: <description de la tache>
---

## MANDATORY EXECUTION RULES (READ FIRST)

- 🛑 NEVER execute tasks directly - ALWAYS use background workers
- 🛑 NEVER skip impact-analyzer in Wave -1
- 🛑 NEVER skip regression-guard in Wave 8
- 🛑 NEVER bypass context-keeper for task enrichment
- 🛑 NEVER have workers share state directly - use Knowledge Graph only
- 🛑 NEVER block main conversation - all tasks run in background
- ✅ ALWAYS generate SESSION_ID and create session folder first
- ✅ ALWAYS decompose into atomic tasks (1 file, 1 action, < 5 min)
- ✅ ALWAYS use `run_in_background: true` for worker tasks
- ✅ ALWAYS run protection workflow: impact-analyzer (Wave -1) → work → regression-guard (Wave 8)
- ✅ ALWAYS enrich tasks via context-keeper before execution
- ✅ ALWAYS sync state via Knowledge Graph (mcp__memory__*)
- 📋 YOU ARE AN ORCHESTRATOR, not a worker
- 💬 FOCUS on "Decompose → Enrich → Dispatch → Validate"
- 🚫 FORBIDDEN to execute code yourself - workers do all implementation
- 🚫 FORBIDDEN to skip the 4-phase process (Init → Decompose → Execute → Complete)
- 🚫 FORBIDDEN to use synchronous task execution

## EXECUTION PROTOCOLS

- 🎯 Phase 1 (Init): Generate SESSION_ID, create folders, init Knowledge Graph
- 🎯 Phase 2 (Decompose): project-supervisor analyzes, tech-lead architects, create atomic tasks
- 🎯 Phase 3 (Execute): Workers pull from priority queue, context-keeper enriches, validator audits
- 🎯 Phase 4 (Complete): regression-guard validates, generate report, archive session
- 🚫 FORBIDDEN to skip any phase or reorder them

## CONTEXT BOUNDARIES

- This skill ORCHESTRATES parallel execution, it does NOT execute tasks itself
- All task execution is delegated to background workers via Task tool
- Workers are ISOLATED - they only receive context briefs from context-keeper
- State persistence is ONLY via Knowledge Graph - no shared memory
- You have NO permission to write code directly

---

# Skill: /parallel-workers

Orchestre des taches complexes via :

- Decomposition automatique en taches atomiques
- Enrichissement contextuel via context-keeper
- **Execution parallele via worker pool**
- Validation asynchrone continue
- Recovery intelligent des echecs
- Tracabilite complete via Knowledge Graph

## Quand utiliser

Utilisez `/parallel-workers` quand :

- Vous avez une tache complexe sans template predefini
- Vous voulez une decomposition automatique
- Les sous-taches peuvent s'executer en parallele
- Vous avez besoin de workers independants

Pour les pipelines predefinis, utilisez `/orchestrate --template <name>`.

## Processus

### Phase 1: Initialisation

```
1. Generer SESSION_ID
   Format: {YYYYMMDD}_{HHMMSS}_{6_RANDOM_CHARS}

2. Creer structure session
   .claude/{SESSION_ID}/
   ├── L0_MASTER_PLAN.md
   ├── context_briefs/
   └── queue/
       ├── priority_queue.json
       └── workers_status.json

3. Initialiser Knowledge Graph
   - Creer entite Mission
   - Definir contraintes globales
   - Enregistrer session
```

### Phase 2: Analyse & Decomposition

```
1. Deleguer a project-supervisor
   - Identifier les domaines concernes
   - Estimer la complexite
   - Lister les contraintes

2. Deleguer a tech-lead
   - Decisions techniques
   - Contrats API
   - Patterns a utiliser

3. Decomposer en Waves
   - Wave -1: impact-analyzer (OBLIGATOIRE AVANT)
   - Wave 0-7: Waves de travail
   - Wave 8: regression-guard (OBLIGATOIRE APRES)

4. Creer taches atomiques
   - 1 fichier par tache
   - 1 action par tache
   - < 5 min par tache
   - Dependances explicites
```

### Phase 3: Execution Parallele

```
1. Demarrer Worker Pool (N=5 par defaut)
   Chaque worker:
   - Prend tache de la priority queue
   - Recoit context brief de context-keeper
   - Invoque agent specialise (run_in_background: true)
   - Passe immediatement a la tache suivante

2. Validator audite en continu (async)
   - Verifie qualite code
   - Verifie architecture
   - Verifie securite

3. Recovery-agent traite les echecs
   - Analyse cause racine
   - Applique fix auto si possible (max 3 retries)
   - Escalade sinon

4. Graph-sync maintient la synchronisation
   - Met a jour Knowledge Graph
   - Regenere Master Plan
```

### Phase 4: Completion

```
1. Attendre que toutes les taches soient terminees
2. Executer regression-guard (OBLIGATOIRE)
3. Generer rapport final
4. Archiver session
```

## Options

| Option                | Description                  | Defaut |
| --------------------- | ---------------------------- | ------ |
| `--workers N`         | Nombre de workers paralleles | 5      |
| `--no-tests`          | Skip les tests (dev only)    | false  |
| `--dry-run`           | Planifie sans executer       | false  |
| `--resume SESSION_ID` | Reprendre une session        | -      |

## Exemples

```bash
# Nouvelle feature (decomposition auto)
/parallel-workers Implementer l'authentification OAuth2

# Mise a jour complexe
/parallel-workers Mettre a jour toute la stack vers les dernieres versions

# Mode dry-run (planification seule)
/parallel-workers --dry-run Ajouter un systeme de notifications
```

## Difference avec /orchestrate

| Aspect        | /parallel-workers     | /orchestrate                   |
| ------------- | --------------------- | ------------------------------ |
| Mode          | Standard (auto)       | Injectable (template)          |
| Execution     | Workers paralleles    | step-orchestrator sequentiel   |
| Input         | Description textuelle | --template, --workflow, --file |
| Decomposition | Automatique           | Pipeline YAML                  |

## Agents utilises

- `project-supervisor` : Analyse initiale
- `tech-lead` : Architecture
- `impact-analyzer` : Protection AVANT
- `context-keeper` : Enrichissement contexte
- `validator` : Validation continue
- `recovery-agent` : Gestion echecs
- `graph-sync` : Synchronisation KG
- `regression-guard` : Protection APRES

---

## SUCCESS METRICS

✅ SESSION_ID generated and session folder created
✅ Tasks decomposed into atomic units (1 file, 1 action, < 5 min each)
✅ Wave -1 executed: impact-analyzer ran BEFORE any modifications
✅ Wave 8 executed: regression-guard ran AFTER all modifications
✅ All workers used `run_in_background: true`
✅ context-keeper enriched every task with context brief
✅ Knowledge Graph updated throughout (via graph-sync)
✅ No direct execution - all work delegated to workers
✅ Parallelism achieved: 4-5 workers active simultaneously

## FAILURE MODES

❌ Executing tasks directly instead of dispatching to workers
❌ Skipping Wave -1 (impact-analyzer) - protection is MANDATORY
❌ Skipping Wave 8 (regression-guard) - validation is MANDATORY
❌ Not using `run_in_background: true` - blocks the conversation
❌ Workers sharing state directly instead of via Knowledge Graph
❌ Tasks not atomic (multiple files, multiple actions, > 5 min)
❌ Skipping context-keeper enrichment
❌ Not generating SESSION_ID and session folder
❌ **CRITICAL**: Going "free style" without following the 4-phase process

## CRITICAL REMINDERS

<critical>
1. YOU ORCHESTRATE, YOU DO NOT EXECUTE
2. Protection workflow is NON-NEGOTIABLE: impact-analyzer (Wave -1) → regression-guard (Wave 8)
3. ALL tasks MUST use `run_in_background: true`
4. Workers are ISOLATED - context comes ONLY from context-keeper briefs
5. State synchronization is ONLY via Knowledge Graph - no shortcuts
6. Atomic tasks: 1 file, 1 action, < 5 minutes - NO EXCEPTIONS
</critical>

---

## Voir aussi

- `/orchestrate` : Mode workflow injectable
- `/workflow` : Wrapper simplifie pour templates
- `~/.claude/docs/distributed-orchestration.md` : Architecture detaillee
