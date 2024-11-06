""" Seed dapr-statetore """
from configdb import ConfigDB
from pulsartenant import PulsarTenant
from pulsarnamespace import PulsarNamespace
from pulsartopic import PulsarTopic
import json
import os

configdb = ConfigDB()
pt = PulsarTenant()
pns = PulsarNamespace()
pto = PulsarTopic()

"""
Template factories returns a dict: 
{"template": <template_name>, "data": <pulsar tenant template configuration>}
"""
pt_template = pt.factory()
pns_template = pns.factory()
pto_template = pto.factory()

templates = []
templates.append(pt_template)
templates.append(pns_template)
templates.append(pto_template)

for t in templates:
   result = configdb.delete(t["template"])
   print(f"Delete existing template - status code: {result.status_code}")

   result = configdb.set(t["template"], t["data"])
   print(f"Create new template - status code: {result.status_code}")

print("Done seeding templates")

