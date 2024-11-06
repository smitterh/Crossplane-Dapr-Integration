""" Test dapr-statetore """
from configdb import ConfigDB
import json

configdb = ConfigDB()

result = configdb.get("template-pulsar-tenant")
print(f"result is %s",result)
print(result.content)