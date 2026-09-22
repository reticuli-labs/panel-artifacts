#!/bin/bash
cd /home/user/claude-projects/Reticuli/panel-artifacts/outcome-replication-2026-09-22 || exit 9
export COLONY_API_KEY="$(python3 -c "import json;d=json.load(open('/home/reticuli/.reticuli/colony.json'));print(next(v for v in (d.values() if isinstance(d,dict) else d) if isinstance(v,str) and v.startswith('col_')))")"
echo "START $(date -u +%FT%TZ) harness $(~/.venvs/colony/bin/python -c 'import ainglish;print(ainglish.__version__)')"
~/.venvs/colony/bin/ainglish-panel run runspec-successor.json --submit; echo "PANEL_EXIT $? $(date -u +%FT%TZ)"
