#!/usr/bin/env bash
# build-theme.sh — assemble le thème Marp final (Marp ne résout pas @import local).
# Usage : build-theme.sh <accent-override.css> > theme.css
#   <accent-override.css> : fragment :root{ --accent:...; --accent-ink:...; } (cf. theme.template.css)
# Ordre = en-tête @theme, tokens (défauts), layouts (utilisent les vars),
#         override d'accent EN DERNIER (cascade → gagne).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERRIDE="${1:?usage: build-theme.sh <accent-override.css> > theme.css}"
echo "/* @theme presentation — fichier généré par build-theme.sh, ne pas éditer à la main */"
cat "$DIR/tokens.css"
echo
cat "$DIR/layouts.css"
echo
cat "$OVERRIDE"
