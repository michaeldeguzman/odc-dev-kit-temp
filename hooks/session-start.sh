#!/usr/bin/env bash
# ODC session context injection.
# Outputs last build entry from CLAUDE.md so Claude knows current app state
# without needing to re-read the whole file each session.
#
# Install: add to settings.json hooks.SessionStart

REPO_ROOT="${REPO_ROOT:-$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel 2>/dev/null)}"
CLAUDE_MD="${CLAUDE_MD_PATH:-$REPO_ROOT/CLAUDE.md}"
README_MD="$REPO_ROOT/README.md"

[ ! -f "$CLAUDE_MD" ] && exit 0

# Tenant from README (CLAUDE.md has runtime URL, not tenant hostname)
TENANT=$(grep -oE '[A-Za-z0-9][A-Za-z0-9.-]*\.outsystems\.dev' "$README_MD" 2>/dev/null | head -1)
APP_KEY=$(grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' "$CLAUDE_MD" | head -1)

# Extract last table row from the most recent build history section.
# Matches lines like: | description | Rev N → M | notes |
LAST_BUILD=$(grep -E '^\| .+ \| Rev [0-9]' "$CLAUDE_MD" | tail -1 | sed 's/^| //' | sed 's/ |$//')

# Extract last session date heading
LAST_DATE=$(grep -E '^### .+ — [0-9]{4}-[0-9]{2}-[0-9]{2}' "$CLAUDE_MD" | tail -1 | sed 's/^### //')

CONTEXT="ODC: tenant=${TENANT:-unknown}"
[ -n "$APP_KEY" ] && CONTEXT="$CONTEXT | app=${APP_KEY}"
[ -n "$LAST_DATE" ] && CONTEXT="$CONTEXT | last session: $LAST_DATE"
[ -n "$LAST_BUILD" ] && CONTEXT="$CONTEXT | last build: $LAST_BUILD"

echo "$CONTEXT"
exit 0
