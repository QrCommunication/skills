#!/usr/bin/env bash
# Bootstrap idempotent du skill document-format-conformance.
# Installe TOUT ce dont les scripts ont besoin :
#   1. .venv + validateurs Python (requirements.txt)
#   2. CLI : qpdf (structure PDF) + xmllint (XSD/RNG XML)  [apt]
#   3. veraPDF (validateur PDF/A & Factur-X de référence)  [headless, ~/.local]
#
# Relançable sans risque : chaque étape détecte ce qui est déjà présent et skip.
# Usage : bash scripts/setup.sh
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_ROOT/.venv"
VERAPDF_VERSION_FALLBACK="1.30.2"
VERAPDF_HOME="$HOME/.local/share/verapdf"
LOCAL_BIN="$HOME/.local/bin"

say() { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()  { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn(){ printf '\033[1;33m! %s\033[0m\n' "$*"; }

# --------------------------------------------------------------------------- #
say "1/3 — venv Python + validateurs"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
  ok "venv créé : $VENV"
else
  ok "venv déjà présent"
fi
"$VENV/bin/pip" install -q -U pip
"$VENV/bin/pip" install -q -r "$SKILL_ROOT/scripts/requirements.txt"
ok "deps python installées (pikepdf, pypdf, factur-x, python-docx, python-pptx, openpyxl, lxml)"

# --------------------------------------------------------------------------- #
say "2/3 — CLI qpdf + xmllint"
NEED_APT=()
command -v qpdf    >/dev/null 2>&1 || NEED_APT+=(qpdf)
command -v xmllint >/dev/null 2>&1 || NEED_APT+=(libxml2-utils)
if [ "${#NEED_APT[@]}" -eq 0 ]; then
  ok "qpdf + xmllint déjà présents"
elif command -v apt-get >/dev/null 2>&1; then
  if sudo -n true 2>/dev/null; then SUDO="sudo"; else SUDO="sudo"; warn "sudo demandera le mot de passe"; fi
  $SUDO apt-get install -y -q "${NEED_APT[@]}"
  ok "installés via apt : ${NEED_APT[*]}"
else
  warn "apt-get absent — installer manuellement : ${NEED_APT[*]}"
fi

# --------------------------------------------------------------------------- #
say "3/3 — veraPDF (validateur PDF/A & Factur-X)"
if command -v verapdf >/dev/null 2>&1 || [ -x "$VERAPDF_HOME/verapdf" ]; then
  ok "veraPDF déjà installé"
else
  if ! command -v java >/dev/null 2>&1; then
    warn "Java absent — veraPDF requiert un JRE. Installer : sudo apt-get install -y default-jre, puis relancer."
  else
    TMP="$(mktemp -d)"
    say "  téléchargement de l'installeur veraPDF…"
    if curl -fsSL -o "$TMP/verapdf.zip" "https://software.verapdf.org/releases/verapdf-installer.zip"; then
      ( cd "$TMP" && unzip -q verapdf.zip )
      JAR="$(find "$TMP" -name 'verapdf-izpack-installer-*.jar' | head -1)"
      cat > "$TMP/auto.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<AutomatedInstallation langpack="eng">
    <com.izforge.izpack.panels.htmlhello.HTMLHelloPanel id="welcome"/>
    <com.izforge.izpack.panels.target.TargetPanel id="install_dir">
        <installpath>$VERAPDF_HOME</installpath>
    </com.izforge.izpack.panels.target.TargetPanel>
    <com.izforge.izpack.panels.packs.PacksPanel id="sdk_pack_select">
        <pack index="0" name="veraPDF GUI" selected="true"/>
        <pack index="1" name="veraPDF Mac and *nix Scripts" selected="true"/>
        <pack index="2" name="veraPDF Validation model" selected="true"/>
        <pack index="3" name="veraPDF Documentation" selected="false"/>
        <pack index="4" name="veraPDF Sample Plugins" selected="false"/>
    </com.izforge.izpack.panels.packs.PacksPanel>
    <com.izforge.izpack.panels.install.InstallPanel id="install"/>
    <com.izforge.izpack.panels.finish.FinishPanel id="finish"/>
</AutomatedInstallation>
XML
      rm -rf "$VERAPDF_HOME"
      java -jar "$JAR" "$TMP/auto.xml" >/dev/null
      mkdir -p "$LOCAL_BIN"
      ln -sf "$VERAPDF_HOME/verapdf" "$LOCAL_BIN/verapdf"
      rm -rf "$TMP"
      ok "veraPDF installé → $VERAPDF_HOME (symlink $LOCAL_BIN/verapdf)"
    else
      warn "Téléchargement veraPDF échoué — réessayer ou installer depuis https://verapdf.org/software/"
    fi
  fi
fi

# --------------------------------------------------------------------------- #
say "Vérification finale"
"$VENV/bin/python" "$SKILL_ROOT/scripts/doctor.py" || true
ok "Setup terminé."
echo "Astuce : ajouter ~/.local/bin au PATH si 'verapdf' n'est pas trouvé."
