#!/usr/bin/env bash
set -euo pipefail

# Simulate a startup guard then invoke python to import psycopg2
# This script is intentionally simple and safe: it does not run any network or DB code.

# Simulate externally-set PYTHONPATH
export PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages

# Emulate the guard from populate/start scripts
if [ -n "$PYTHONPATH" ]; then
  echo "⚠️  PYTHONPATH is set — unsetting it to avoid importing incompatible system packages"
  unset PYTHONPATH
fi

# Use the project's venv python if available
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python - <<'PY'
import sys
try:
    import psycopg2
    print('OK: psycopg2 import succeeded')
except Exception as e:
    print('ERR: psycopg2 import failed:', e)
    sys.exit(2)
PY
else
  python3 - <<'PY'
import sys
try:
    import psycopg2
    print('OK: psycopg2 import succeeded')
except Exception as e:
    print('ERR: psycopg2 import failed:', e)
    sys.exit(2)
PY
fi

echo "Integration check passed."