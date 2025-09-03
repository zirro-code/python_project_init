#!/bin/bash

# set -euxo pipefail

(ruff check . && ruff format --check .) && { echo "Ruff check successful"; true; } || { echo "Ruff check failed, skipping the rest of the pipeline"; } &&
mypy $(find . -type f \( -name "*.py" -o -name "*.pyi" \)) && { echo "Mypy check successful"; true; } || { echo "Mypy check failed, skipping the rest of the pipeline"; } &&
python -m pytest  && { echo "Pytest check successful"; true; } || { echo "Pytest check failed, skipping the rest of the pipeline"; }

