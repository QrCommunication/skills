---
name: meta-workflow-rl
description: Meta-workflow generique injectable avec creation interactive (--create) - UN seul point d'entree pour tous les templates
argument-hint: <template-name | --list | --search "query" | --create | --pipeline "..." | --file path>
---

# Skill: /meta-workflow-rl

Execute un pipeline de workflow generique et injectable avec protection obligatoire.

## Invocation

```bash
# LISTER les templates disponibles
/meta-workflow-rl --list                    # Liste tous les templates par categorie
/meta-workflow-rl --list --category mobile  # Liste uniquement la categorie mobile
/meta-workflow-rl --search "seo"            # Recherche templates contenant "seo"

# CRÉER un nouveau template
/meta-workflow-rl --create                  # Lance l'assistant interactif
/meta-workflow-rl --create --name api-migration  # Crée avec nom pré-rempli
/meta-workflow-rl --create --from feature-dev    # Clone un template existant
/meta-workflow-rl --create --import file.yaml    # Importe et valide un fichier

# Template predefini
/meta-workflow-rl feature-dev
/meta-workflow-rl deploy-production
/meta-workflow-rl seo-audit

# Pipeline inline YAML
/meta-workflow-rl --pipeline "name: custom\nsteps:\n  - agent: tech-lead\n    ..."

# Pipeline depuis fichier
/meta-workflow-rl --file ./my-workflow.yaml

# Mode dry-run (affiche plan sans executer)
/meta-workflow-rl feature-dev --dry-run

# Resume session existante
/meta-workflow-rl --resume SESSION_ID
```

## Lister les Templates (--list)

Quand invoqué avec `--list`, **exécuter le script dynamique** :

```bash
# Liste complète (dynamique)
~/.claude/skills/meta-workflow-rl/scripts/list-templates.sh

# Par catégorie
~/.claude/skills/meta-workflow-rl/scripts/list-templates.sh --category mobile

# Recherche
~/.claude/skills/meta-workflow-rl/scripts/list-templates.sh --search "audit"

# Juste le count
~/.claude/skills/meta-workflow-rl/scripts/list-templates.sh --count-only
```

**Exemple de sortie:**

```
📋 TEMPLATES DISPONIBLES (dynamique)

┌─────────────────────────────────────────────────────────────────────────┐
│ A. DÉVELOPPEMENT APPLICATION (5)                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ feature-dev        │ Feature standard (BA → Tech → Back → Front → QA)   │
│ api-contract       │ Nouveau endpoint API avec contrats                  │
│ frontend-spa       │ React/Vue/Svelte SPA                                │
│ frontend-ssr       │ Next.js/Nuxt SSR                                    │
│ laravel-blade      │ Laravel monolith avec Blade                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ B. MOBILE (4)                                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ mobile-app         │ App mobile générale                                 │
│ mobile-ios         │ App iOS spécifique                                  │
│ mobile-android     │ App Android spécifique                              │
│ mobile-crossplatform│ iOS + Android simultané                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ C. BASE DE DONNÉES (4)                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│ db-postgresql      │ PostgreSQL natif                                    │
│ db-mysql           │ MySQL/MariaDB                                       │
│ db-mongodb         │ MongoDB                                             │
│ neon-database      │ Neon serverless PostgreSQL                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ D. INFRASTRUCTURE (7)                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ infrastructure     │ Setup infra générale                                │
│ webserver-nginx    │ Nginx + SSL                                         │
│ webserver-caddy    │ Caddy auto-SSL                                      │
│ docker-compose     │ Docker local                                        │
│ kubernetes         │ K8s production                                      │
│ terraform-infra    │ IaC Terraform                                       │
│ vercel-deploy      │ Vercel/Edge                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ E. SEO & CONTENT (4)                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ seo-content        │ Content standard                                    │
│ seo-programmatic   │ Milliers de pages SEO                               │
│ seo-audit          │ Audit SEO complet                                   │
│ landing-page       │ Landing page optimisée                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ F. IA & AGENTS (6)                                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ ai-feature         │ Intégration LLM dans app                            │
│ agent-claude       │ Création agent Claude                               │
│ rag-pipeline       │ Pipeline RAG complet                                │
│ ml-training        │ Fine-tuning/ML                                      │
│ ai-monitoring      │ Monitoring LLM                                      │
│ n8n-automation     │ Workflows n8n                                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ G. QUALITÉ & VALIDATION (7)                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ contract-validation│ Sync types front/back                               │
│ react-bestpractices│ Audit React                                         │
│ security-audit     │ Audit sécurité OWASP                                │
│ performance-audit  │ Audit performance                                   │
│ accessibility-audit│ Audit WCAG                                          │
│ model-audit        │ Audit Models Eloquent                               │
│ fix-loop           │ Correction auto CI                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ H. DÉPLOIEMENT & OPS (5)                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ deploy-staging     │ Deploy staging                                      │
│ deploy-production  │ Deploy production                                   │
│ migration-data     │ Migration données                                   │
│ disaster-recovery  │ Plan DR                                             │
│ monitoring-setup   │ Setup monitoring                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ I. MARKETING (3)                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ marketing-launch   │ Lancement produit                                   │
│ email-campaign     │ Campagne email                                      │
│ social-campaign    │ Campagne réseaux sociaux                            │
└─────────────────────────────────────────────────────────────────────────┘

💡 Usage: /meta-workflow-rl <template-name>
📁 Templates: ~/.claude/skills/meta-workflow-rl/templates/
```

## Rechercher un Template (--search)

```bash
/meta-workflow-rl --search "audit"
# Résultat:
# 🔍 Templates contenant "audit" (5):
#   - security-audit    │ Audit sécurité OWASP
#   - performance-audit │ Audit performance
#   - accessibility-audit│ Audit WCAG
#   - model-audit       │ Audit Models Eloquent
#   - seo-audit         │ Audit SEO complet
```

## Créer un Nouveau Template (--create)

Mode interactif pour créer un nouveau template de workflow.

### Invocation

```bash
/meta-workflow-rl --create                    # Lance l'assistant interactif
/meta-workflow-rl --create --name my-template # Démarre avec un nom
/meta-workflow-rl --create --from feature-dev # Clone un template existant
/meta-workflow-rl --create --import file.yaml # Importe et valide un fichier externe
```

### Processus Interactif

Le mode `--create` guide l'utilisateur à travers 6 phases:

#### Phase 1: Identité du Workflow

```
🆕 CRÉATION DE WORKFLOW

1️⃣ Nom du workflow (slug):
   > _____________
   (ex: api-migration, onboarding-flow, backup-restore)

2️⃣ Description courte (1 ligne):
   > _____________

3️⃣ Catégorie:
   ┌──────────────────────────────────────────────────┐
   │  [1] dev       - Développement application        │
   │  [2] mobile    - Applications mobiles             │
   │  [3] database  - Base de données                  │
   │  [4] infra     - Infrastructure                   │
   │  [5] seo       - SEO & Content                    │
   │  [6] ai        - IA & Agents                      │
   │  [7] audit     - Qualité & Validation             │
   │  [8] deploy    - Déploiement & Ops                │
   │  [9] marketing - Marketing                        │
   │  [0] custom    - Nouvelle catégorie               │
   └──────────────────────────────────────────────────┘
   Choix: _
```

#### Phase 2: Skills Globaux

```
4️⃣ Skills globaux (appliqués à TOUTES les étapes):

   Suggérés (appuyer Entrée pour accepter):
   ✓ clean-code
   ✓ review-code

   Ajouter d'autres? (comma-separated ou vide):
   > _____________
```

#### Phase 3: Définition des Étapes (boucle)

```
📋 ÉTAPE 1

5️⃣ Nom de l'étape:
   > _____________

6️⃣ Agent responsable:
   Disponibles: business-analyst, tech-lead, backend-laravel, frontend-react,
                database-admin, seo-specialist, qa-testing, devops-infra...

   Recherche: > ____
   Sélection: _____________

7️⃣ Skills spécifiques (comma-separated):
   > _____________

8️⃣ Tâche (multiline, terminer par ligne vide):
   > Décrire ce que l'agent doit faire...
   > ...
   >

9️⃣ Output attendu:
   > _____________

🔟 Critères de validation:
   > _____________

1️⃣1️⃣ Stratégie de rollback:
   > _____________

1️⃣2️⃣ Dépend de (étapes précédentes, comma-separated ou vide):
   > _____________

➕ Ajouter une autre étape? [O/n]
```

#### Phase 4: Aperçu Visuel

Après les étapes, affiche un aperçu complet:

```
📊 APERÇU DU WORKFLOW: api-migration

┌──────────────────────────────────────────────────────────────────┐
│ Description: Migration API v1 vers v2 avec backward compatibility│
│ Catégorie: dev                                                    │
│ Skills globaux: clean-code, review-code                           │
│ Protection: impact-analyzer → [steps] → regression-guard          │
└──────────────────────────────────────────────────────────────────┘

📈 DIAGRAMME DE FLUX:

  ┌────────────────────────────┐
  │ 🛡️ impact-analyzer         │
  └────────────┬───────────────┘
               │
        ┌──────▼──────┐
        │ 1. Audit v1 │ (tech-lead)
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ 2. Design v2│ (tech-lead)
        └──────┬──────┘
               │
        ┌──────▼──────────┐
        │ 3. Implémentation│ (backend-laravel)
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │ 4. Migration BD  │ (database-admin)
        └──────┬──────────┘
               │
        ┌──────▼──────┐
        │ 5. Tests    │ (qa-testing)
        └──────┬──────┘
               │
  ┌────────────▼───────────────┐
  │ 🛡️ regression-guard        │
  └────────────────────────────┘

📄 YAML GÉNÉRÉ:

```yaml
name: api-migration
description: "Migration API v1 vers v2 avec backward compatibility"

protection:
  before: impact-analyzer
  after: regression-guard

skills_global:
  - clean-code
  - review-code

steps:
  - name: "Audit API v1"
    agent: tech-lead
    skills: [explore, mermaid-diagrams]
    task: |
      Analyser l'API v1 existante...
    output: "audit-v1.md"
    validation: "Endpoints documentés"
    rollback: "N/A - audit only"

  # ... autres étapes
```

```
#### Phase 5: Confirmation et Modifications
```

✅ CONFIRMATION

Le workflow vous convient?

  [1] ✓ Oui, sauvegarder
  [2] ✏️ Modifier une étape
  [3] ➕ Ajouter une étape
  [4] ➖ Supprimer une étape
  [5] 🔄 Réordonner les étapes
  [6] ❌ Annuler

Choix: _

# Si [2] Modifier:

Quelle étape? (1-5): _
Que modifier?
  [a] Nom
  [b] Agent
  [c] Skills
  [d] Task
  [e] Output
  [f] Validation
  [g] Rollback
  [h] Dépendances
  [*] Tout

```
#### Phase 6: Sauvegarde
```

💾 SAUVEGARDE

Fichier: ~/.claude/skills/meta-workflow-rl/templates/api-migration.yaml

✅ Template créé avec succès!

Usage:
  /workflow api-migration
  /workflow api-migration --dry-run

Le template apparaîtra dans:
  /workflow --list --category dev
  /workflow --search "api"

```
### Validation Automatique

Pendant la création, le système valide:

- ✅ Nom unique (pas de conflit avec templates existants)
- ✅ Agents existent dans le catalogue
- ✅ Skills existent dans le catalogue
- ✅ Pas de dépendances circulaires
- ✅ Au moins 1 étape définie
- ✅ Protection toujours présente (hardcoded)

## Schema Pipeline YAML

```yaml
name: "workflow-name"
description: "What this workflow does"

# PROTECTION OBLIGATOIRE - Automatiquement injectee si absente
# JAMAIS desactivable - hardcoded dans le systeme
protection:
  before: impact-analyzer  # TOUJOURS execute en premier
  after: regression-guard  # TOUJOURS execute en dernier

# Skills globaux injectes a TOUTES les etapes
skills_global:
  - clean-code
  - review-code

# Pipeline d'etapes
steps:
  # ÉTAPES PARALLÈLES - Même parallel_group = exécution simultanée
  - name: "Step 1A"
    agent: explore-codebase
    parallel_group: "discovery"      # <-- Groupe parallèle
    parallel_split: 5                # <-- Divise le codebase en 5 parties
    skills: [explore]
    task: "Explorer partie du codebase"
    output: "audit-part.md"
    validation: "Partie analysée"
    rollback: "N/A"

  - name: "Step 1B"
    agent: technical-writer
    parallel_group: "discovery"      # <-- Même groupe = parallèle avec 1A
    skills: [explore]
    task: "Analyser docs existantes"
    output: "analyse-docs.md"
    validation: "Docs analysées"
    rollback: "N/A"

  # ÉTAPE SÉQUENTIELLE - Attend la fin du groupe "discovery"
  - name: "Step 2"
    agent: tech-lead
    depends_on: ["discovery"]        # <-- Attend tout le groupe
    skills: [brainstorm]
    task: "Synthétiser les découvertes"
    output: "synthese.md"
    validation: "Synthèse complète"
    rollback: "Reprendre analyse"
```

### Parallélisation avec `parallel_group`

| Propriété        | Type       | Description                                                                |
| ---------------- | ---------- | -------------------------------------------------------------------------- |
| `parallel_group` | string     | Nom du groupe parallèle. Étapes avec même groupe s'exécutent simultanément |
| `parallel_split` | int (2-10) | Divise le scope en N parties pour l'agent `explore-codebase`               |
| `depends_on`     | string[]   | Peut référencer un nom de groupe pour attendre toutes ses étapes           |

**Règles de parallélisation:**

- Étapes SANS `parallel_group` ni `depends_on` → Séquentielles (ordre du YAML)
- Étapes avec MÊME `parallel_group` → Parallèles (lancées ensemble)
- `depends_on: ["group_name"]` → Attend TOUTES les étapes du groupe
- `parallel_split: N` → L'agent explore-codebase divise le travail en N workers

## Processus d'Execution

### Phase 1: Initialisation

```
1. Parse pipeline definition
   - Depuis template predefini (templates/*.yaml)
   - Depuis --pipeline inline
   - Depuis --file path

2. Validation
   - Verifier que tous les agents existent
   - Verifier que tous les skills existent
   - Valider le schema YAML

3. Session Setup
   - Generer SESSION_ID: {YYYYMMDD}_{HHMMSS}_{6_RANDOM}
   - Creer .claude/{SESSION_ID}/
   - Initialiser L0_MASTER_PLAN.md
```

### Phase 2: Protection AVANT (OBLIGATOIRE)

```
REGLE ABSOLUE - NON-NEGOCIABLE:
- impact-analyzer TOUJOURS execute AVANT toute modification
- Si impact-analyzer detecte risque CRITICAL: STOP + rapport
- AUCUN bypass possible
```

```javascript
// Pseudocode - Protection hardcoded
await executeProtection('before', 'impact-analyzer', {
  pipeline: pipelineDefinition,
  skills: ['brainstorm', 'ultrathink', 'explore'],
  stopOnCritical: true
});
```

### Phase 3: Execution (Séquentielle + Parallèle)

```
ALGORITHME D'EXECUTION:

1. Grouper les steps par parallel_group
2. Construire le DAG (graphe de dépendances)
3. Pour chaque "wave" d'exécution:

   SI steps ont parallel_group:
     → Lancer TOUS les steps du groupe en parallèle
     → Si parallel_split défini: diviser le scope en N workers
     → Attendre que TOUS les steps du groupe terminent
     → Merger les outputs

   SINON (step séquentiel):
     → Exécuter normalement
     → Attendre completion avant step suivant

4. Valider outputs selon critères
5. Si échec: rollback ou escalade
6. Mettre à jour Knowledge Graph
7. Passer à la wave suivante
```

**Exemple de parallélisation avec `parallel_split`:**

```
Workflow: readme-refactor
Codebase: apps/api, apps/dashboard, apps/landing, apps/mcp-server, apps/cli

parallel_split: 5 → Lance 5 agents explore-codebase en parallèle:
  ├── Worker 1: apps/api/
  ├── Worker 2: apps/dashboard/
  ├── Worker 3: apps/landing/
  ├── Worker 4: apps/mcp-server/
  └── Worker 5: apps/cli/

Résultat: 5x plus rapide que séquentiel
```

**Diagramme d'exécution parallèle:**

```
                    ┌─────────────────────┐
                    │ 🛡️ impact-analyzer  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ explore W1    │    │ explore W2    │    │ explore W3    │
│ (apps/api)    │    │ (apps/dash)   │    │ (apps/land)   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └──────────────────┬─┴────────────────────┘
                           │ (merge outputs)
                           ▼
                    ┌─────────────────┐
                    │ Step suivant    │
                    └─────────────────┘
```

### Phase 4: Protection APRES (OBLIGATOIRE)

```
REGLE ABSOLUE - NON-NEGOCIABLE:
- regression-guard TOUJOURS execute APRES toute modification
- Compare baseline vs nouvel etat
- Si regression detectee: BLOCK + rapport
- AUCUN bypass possible
```

```javascript
// Pseudocode - Protection hardcoded
await executeProtection('after', 'regression-guard', {
  changes: allChangesFromSteps,
  skills: ['ci-fixer', 'review-code'],
  blockOnRegression: true
});
```

### Phase 5: Completion

```
1. Generer rapport final
   - Resume des changements
   - Fichiers crees/modifies
   - Decisions prises
   - Metriques

2. Archiver session
   - Finaliser Master Plan
   - Preserver Knowledge Graph
   - Logger completion
```

## Delegation au Step-Orchestrator

Le workflow delegue l'execution a l'agent `step-orchestrator`:

```javascript
Task({
  description: "Execute workflow pipeline",
  subagent_type: "step-orchestrator",
  run_in_background: true,
  prompt: `
    SESSION: ${sessionId}
    PIPELINE: ${JSON.stringify(pipeline)}

    INSTRUCTIONS:
    1. Protection BEFORE deja executee (impact-analyzer)
    2. Execute chaque step sequentiellement
    3. Maintiens context entre steps
    4. Valide chaque step avant de continuer
    5. En cas d'echec: rollback + rapport
    6. A la fin: notifie pour protection AFTER

    RULES:
    - Chaque step = 1 agent + ses skills
    - Context brief injecte a chaque agent
    - Validation obligatoire avant step suivant
    - Max 3 retries par step
  `
})
```

## Templates Disponibles

Les templates sont dans `~/.claude/skills/meta-workflow-rl/templates/`:

| Template                 | Usage                   |
| ------------------------ | ----------------------- |
| `feature-dev.yaml`       | Feature standard        |
| `api-contract.yaml`      | Nouveau endpoint API    |
| `frontend-spa.yaml`      | React/Vue/Svelte SPA    |
| `frontend-ssr.yaml`      | Next.js/Nuxt SSR        |
| `mobile-app.yaml`        | App mobile generale     |
| `db-postgresql.yaml`     | PostgreSQL setup        |
| `deploy-production.yaml` | Deploy prod             |
| `seo-audit.yaml`         | Audit SEO complet       |
| `security-audit.yaml`    | Audit securite          |
| ...                      | (Voir /workflow --list) |

## Options

| Option                | Description                     | Default |
| --------------------- | ------------------------------- | ------- |
| `--list`              | Liste tous les templates        | -       |
| `--list --category X` | Liste templates d'une catégorie | -       |
| `--search "query"`    | Recherche templates par mot-clé | -       |
| `--create`            | Lance l'assistant interactif    | -       |
| `--create --name X`   | Crée avec nom pré-rempli        | -       |
| `--create --from X`   | Clone un template existant      | -       |
| `--create --import F` | Importe et valide un fichier    | -       |
| `--dry-run`           | Affiche plan sans executer      | false   |
| `--resume SESSION_ID` | Reprendre session existante     | -       |
| `--pipeline "YAML"`   | Pipeline inline                 | -       |
| `--file PATH`         | Pipeline depuis fichier         | -       |
| `--workers N`         | Nombre workers paralleles       | 5       |
| `--no-cache`          | Force re-execution              | false   |

### Catégories disponibles (pour --list --category)

| Catégorie   | Templates                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| `dev`       | feature-dev, api-contract, frontend-spa, frontend-ssr, laravel-blade                                                    |
| `mobile`    | mobile-app, mobile-ios, mobile-android, mobile-crossplatform                                                            |
| `database`  | db-postgresql, db-mysql, db-mongodb, neon-database                                                                      |
| `infra`     | infrastructure, webserver-nginx, webserver-caddy, docker-compose, kubernetes, terraform-infra, vercel-deploy            |
| `seo`       | seo-content, seo-programmatic, seo-audit, landing-page                                                                  |
| `ai`        | ai-feature, agent-claude, rag-pipeline, ml-training, ai-monitoring, n8n-automation                                      |
| `audit`     | contract-validation, react-bestpractices, security-audit, performance-audit, accessibility-audit, model-audit, fix-loop |
| `deploy`    | deploy-staging, deploy-production, migration-data, disaster-recovery, monitoring-setup                                  |
| `marketing` | marketing-launch, email-campaign, social-campaign                                                                       |

## Gestion des Erreurs

| Situation            | Action                         |
| -------------------- | ------------------------------ |
| Agent non trouve     | STOP + suggestion agent proche |
| Skill non trouve     | WARNING + continue sans        |
| Step validation fail | Retry (max 3) puis rollback    |
| Rollback fail        | Escalade humaine               |
| Protection fail      | HARD STOP + rapport detaille   |
| Session corrompue    | Recovery-agent + escalade      |

## Exemples

### Template predefini

```bash
/meta-workflow-rl feature-dev
# -> Charge templates/feature-dev.yaml
# -> Execute: business-analyst -> impact-analyzer -> tech-lead -> backend -> frontend -> qa -> regression-guard
```

### Pipeline custom inline

```bash
/meta-workflow-rl --pipeline "
name: quick-fix
description: Fix rapide avec validation
steps:
  - name: Analyze
    agent: tech-lead
    skills: [brainstorm, explore]
    task: Analyser le probleme
    output: Diagnostic
    validation: Cause identifiee
    rollback: Escalade
  - name: Fix
    agent: backend-laravel
    skills: [clean-code, apex]
    task: Implementer le fix
    output: Code corrige
    validation: Tests passent
    rollback: git revert
"
```

### Mode dry-run

```bash
/meta-workflow-rl feature-dev --dry-run
# -> Affiche le plan complet:
#    - Steps a executer
#    - Agents impliques
#    - Skills charges
#    - Estimations
#    - Dependances
# -> Sans rien executer
```

## Integration Knowledge Graph

Entites creees automatiquement:

```
Workflow
├── name: string
├── session_id: string
├── status: PENDING | RUNNING | COMPLETED | FAILED
├── started_at: timestamp
└── completed_at: timestamp

Step
├── name: string
├── agent: string
├── status: PENDING | RUNNING | COMPLETED | FAILED
├── output: any
└── validation_result: boolean

Protection
├── type: BEFORE | AFTER
├── agent: string (impact-analyzer | regression-guard)
├── result: PASS | FAIL | CRITICAL
└── report: string
```

## Voir aussi

- `~/.claude/skills/meta-workflow-rl/templates/` : Templates YAML
- `~/.claude/agents/step-orchestrator.md` : Agent d'execution
- `~/.claude/skills/orchestrate/SKILL.md` : Orchestration distribuee
- `~/.claude/docs/distributed-orchestration.md` : Architecture
