#!/usr/bin/env bash
# Rigenera l'anteprima e la pubblica sul branch gh-pages (GitHub Pages).
# Uso: bash _sorgente/pubblica-anteprima.sh
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_URL="$(git remote get-url origin)"
NAME="$(basename -s .git "$REPO_URL")"
python3 _sorgente/build.py --preview "/$NAME"
cd _anteprima
rm -rf .git
git init -q -b gh-pages
git add -A
git commit -q -m "Anteprima $(date '+%Y-%m-%d %H:%M')"
git push -q -f "$REPO_URL" gh-pages
rm -rf .git
echo "Pubblicata: https://$(echo "$REPO_URL" | sed -E 's#.*github.com[/:]([^/]+)/.*#\1#' | tr 'A-Z' 'a-z').github.io/$NAME/"
