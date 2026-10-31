#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
export GAR_BOARD_SDK="${GAR_BOARD_SDK:-${GAR_LYRA_SDK:-}}"
exec python3 "$ROOT/tools/product.py" build
