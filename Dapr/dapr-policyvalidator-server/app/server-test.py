from fastapi import FastAPI, Header, Body, Request, Response
from policyvalidator import PolicyValidator
import json
import os
import uvicorn

app = FastAPI()
port_number = int(os.getenv("APP_PORT", 8001))


@app.get("/")
async def echo(request:Request):
    return "echo"

if __name__ == "__main__":
    uvicorn.run(app, port=port_number, host="0.0.0.0")