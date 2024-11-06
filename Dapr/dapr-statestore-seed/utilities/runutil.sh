#!/usr/bin/env bash
set -aeuo pipefail

export DAPR_STATESTORE=redis-statestore
#export DAPR_STATESTORE=atlas-statestore
dapr run --app-id util --app-protocol http --dapr-http-port 3501  --scheduler-host-address "" -- python3 $1