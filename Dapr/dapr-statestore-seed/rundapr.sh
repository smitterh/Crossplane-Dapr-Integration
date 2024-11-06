#!/usr/bin/env bash
set -aeuo pipefail

export DAPR_STATESTORE=redis-statestore
dapr run --app-id seed --app-protocol http --dapr-http-port 3501  --scheduler-host-address "" -- python3 ./seed.py
export DAPR_STATESTORE=atlas-statestore
dapr run --app-id seed --app-protocol http --dapr-http-port 3501  --scheduler-host-address "" -- python3 ./seed.py