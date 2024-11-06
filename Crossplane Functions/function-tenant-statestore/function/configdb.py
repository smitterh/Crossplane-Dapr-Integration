from crossplane.function import logging
import requests
import os

class ConfigDB:

    def __init__(self):
      self.dapr_url = os.getenv("DAPR_URL","localhost")
      self.dapr_statestore = os.getenv("DAPR_STATESTORE","atlas-statestore")
      self.dapr_port = os.getenv("DAPR_HTTP_PORT")
      self.log = logging.get_logger()
      self.log.info("Hello from ConfigDB! my configuration database is: %s",{self.dapr_statestore})
    
    def get(self, key):
      dapr_url = "http://{}:{}/v1.0/state/{}/{}".format(self.dapr_url,self.dapr_port,self.dapr_statestore,key)
      result = requests.get(
        url=dapr_url
      )
      return result
  