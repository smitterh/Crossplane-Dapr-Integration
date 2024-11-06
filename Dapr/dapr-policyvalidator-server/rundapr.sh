#!/bin/sh
dapr run --app-id policyvalidator --app-protocol http --dapr-http-port 4500 --app-port 8000 --scheduler-host-address "" -- python3 ./app/server.py