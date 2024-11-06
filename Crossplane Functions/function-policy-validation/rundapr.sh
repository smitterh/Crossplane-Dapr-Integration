#!/bin/sh
dapr run --app-id function-policy-validation --app-protocol http --dapr-http-port 3500 --scheduler-host-address "" -- hatch run development