#!/bin/sh
# Compatibility entry: lifecycle code is generated from the shared template.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
exec "$ROOT/.startup/S99zz-garmyfriend-lyra-zero-w" "$@"
