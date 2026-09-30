#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
version_check='import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'

for candidate in "$project_root/.venv/bin/python" python3 python python3.14 python3.13 python3.12 python3.11; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "$version_check" >/dev/null 2>&1; then
        exec "$candidate" -X utf8 "$project_root/scripts/bootstrap.py"
    fi
done

echo 'Erro: instale Python 3.11 ou superior com suporte a venv e execute novamente.' >&2
exit 1
