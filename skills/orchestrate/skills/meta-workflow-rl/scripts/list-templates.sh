#!/bin/bash
# Script: list-templates.sh
# Génère dynamiquement la liste des templates workflow
# Usage: ./list-templates.sh [--category <cat>] [--search <query>] [--count-only]

TEMPLATES_DIR="${HOME}/.claude/skills/workflow/templates"

# Catégories et leurs patterns
declare -A CATEGORIES=(
    ["dev"]="feature-dev api-contract frontend-spa frontend-ssr laravel-blade"
    ["mobile"]="mobile-app mobile-ios mobile-android mobile-crossplatform"
    ["database"]="db-postgresql db-mysql db-mongodb neon-database"
    ["infra"]="infrastructure webserver-nginx webserver-caddy docker-compose kubernetes terraform-infra vercel-deploy"
    ["seo"]="seo-content seo-programmatic seo-audit landing-page"
    ["ai"]="ai-feature agent-claude rag-pipeline ml-training ai-monitoring n8n-automation"
    ["audit"]="contract-validation react-bestpractices security-audit performance-audit accessibility-audit model-audit fix-loop tier-detector"
    ["deploy"]="deploy-staging deploy-production migration-data disaster-recovery monitoring-setup"
    ["marketing"]="marketing-launch email-campaign social-campaign"
    ["util"]="create-master-plan"
)

# Noms lisibles des catégories
declare -A CATEGORY_NAMES=(
    ["dev"]="DÉVELOPPEMENT APPLICATION"
    ["mobile"]="MOBILE"
    ["database"]="BASE DE DONNÉES"
    ["infra"]="INFRASTRUCTURE"
    ["seo"]="SEO & CONTENT"
    ["ai"]="IA & AGENTS"
    ["audit"]="QUALITÉ & VALIDATION"
    ["deploy"]="DÉPLOIEMENT & OPS"
    ["marketing"]="MARKETING"
    ["util"]="UTILITAIRES"
)

# Ordre des catégories
CATEGORY_ORDER=("dev" "mobile" "database" "infra" "seo" "ai" "audit" "deploy" "marketing" "util")

# Parse arguments
FILTER_CATEGORY=""
SEARCH_QUERY=""
COUNT_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --category)
            FILTER_CATEGORY="$2"
            shift 2
            ;;
        --search)
            SEARCH_QUERY="$2"
            shift 2
            ;;
        --count-only)
            COUNT_ONLY=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Compte total des templates
count_templates() {
    find "$TEMPLATES_DIR" -name "*.yaml" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Extrait la description d'un template
get_description() {
    local file="$1"
    grep -m1 "^description:" "$file" 2>/dev/null | sed 's/description: *"\?\([^"]*\)"\?/\1/' | cut -c1-50
}

# Détermine la catégorie d'un template
get_category() {
    local name="$1"
    for cat in "${!CATEGORIES[@]}"; do
        if [[ " ${CATEGORIES[$cat]} " =~ " ${name} " ]]; then
            echo "$cat"
            return
        fi
    done
    echo "util"
}

# Mode count-only
if $COUNT_ONLY; then
    count_templates
    exit 0
fi

# Mode search
if [[ -n "$SEARCH_QUERY" ]]; then
    echo "🔍 Templates contenant \"$SEARCH_QUERY\":"
    echo ""
    found=0
    for file in "$TEMPLATES_DIR"/*.yaml; do
        [[ ! -f "$file" ]] && continue
        name=$(basename "$file" .yaml)
        desc=$(get_description "$file")
        if [[ "$name" == *"$SEARCH_QUERY"* ]] || [[ "$desc" == *"$SEARCH_QUERY"* ]]; then
            printf "  %-25s │ %s\n" "$name" "$desc"
            ((found++))
        fi
    done
    echo ""
    echo "Total: $found template(s)"
    exit 0
fi

# Mode list (complet ou par catégorie)
total=$(count_templates)
echo "📋 TEMPLATES DISPONIBLES ($total)"
echo ""

for cat in "${CATEGORY_ORDER[@]}"; do
    # Skip si filtre catégorie et pas la bonne
    if [[ -n "$FILTER_CATEGORY" ]] && [[ "$cat" != "$FILTER_CATEGORY" ]]; then
        continue
    fi

    cat_name="${CATEGORY_NAMES[$cat]}"
    templates_in_cat=()

    # Collecte les templates de cette catégorie
    for file in "$TEMPLATES_DIR"/*.yaml; do
        [[ ! -f "$file" ]] && continue
        name=$(basename "$file" .yaml)
        if [[ "$(get_category "$name")" == "$cat" ]]; then
            templates_in_cat+=("$name")
        fi
    done

    # Skip catégories vides
    [[ ${#templates_in_cat[@]} -eq 0 ]] && continue

    # Affiche la catégorie
    count=${#templates_in_cat[@]}
    echo "┌─────────────────────────────────────────────────────────────────────────┐"
    printf "│ %s. %s (%d)%*s│\n" "${cat^^}" "$cat_name" "$count" $((55 - ${#cat_name} - ${#count})) ""
    echo "├─────────────────────────────────────────────────────────────────────────┤"

    for name in "${templates_in_cat[@]}"; do
        desc=$(get_description "$TEMPLATES_DIR/$name.yaml")
        printf "│ %-18s │ %-50s │\n" "$name" "$desc"
    done

    echo "└─────────────────────────────────────────────────────────────────────────┘"
    echo ""
done

echo "💡 Usage: /workflow <template-name>"
echo "📁 Templates: ~/.claude/skills/workflow/templates/"
