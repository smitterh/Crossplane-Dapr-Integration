from fastapi import FastAPI, Header, Body, Request, Response
from policyvalidator import PolicyValidator
import json
import os
import uvicorn

app = FastAPI()
port_number = int(os.getenv("APP_PORT", 8000))
test_mode = os.getenv("TEST_MODE", "True")
dont_clean_up = os.getenv("DONT_CLEANUP", "True")

@app.post("/validate")
async def validate(request:Request):
    """ This method receives a Crossplane response object in JSON and calls policyvalidator """
    print("/validate method got called")
    validation_payload = await request.body()
    apiVersion = request.headers.get("pv-apiVersion")
    kind = request.headers.get("pv-kind")

    pv = PolicyValidator()
    
    validation_result = pv.validate(validation_payload, apiVersion, kind, test=test_mode)
    
    if dont_clean_up == "True":
       pass
    else:
       pv.clean_up_resources()

    return validation_result


if __name__ == "__main__":
    uvicorn.run(app, port=port_number, host="0.0.0.0")


