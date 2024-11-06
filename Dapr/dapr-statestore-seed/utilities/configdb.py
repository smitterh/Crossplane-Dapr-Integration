import time
import logging
import requests
import os

class ConfigDB:

    def __init__(self):
      self.dapr_url = os.getenv("DAPR_URL","localhost")
      self.dapr_statestore = os.getenv("DAPR_STATESTORE","atlas-statestore")
      self.dapr_port = os.getenv("DAPR_HTTP_PORT")
      logging.info("Hello from ConfigDB! my configuration database is: %s",{self.dapr_statestore})
      return
    
    def get(self, key):
      dapr_url = "http://{}:{}/v1.0/state/{}/{}".format(self.dapr_url,self.dapr_port,self.dapr_statestore,key)
      result = requests.get(
        url=dapr_url
      )
      return result
    
    def set(self, key, value):
      dapr_url = "http://{}:{}/v1.0/state/{}".format(self.dapr_url,self.dapr_port,self.dapr_statestore)
      configdata = [{
         "key" : key,
         "value": value
      }]
      result = requests.post(
        url=dapr_url,
        json=configdata
      )
      return result

    def delete(self, key):
      dapr_url = "http://{}:{}/v1.0/state/{}/key".format(self.dapr_url,self.dapr_port,self.dapr_statestore,key)
      result = requests.delete(
        url=dapr_url
      )
      return result
    
    def hello(self):
      return(print("Hello from ConfigDB! my configuration database is: %s",{self.dapr_statestore}))