import logging
import requests
import os

class Secrets:

    def __init__(self):
      self.dapr_url = os.getenv("DAPR_URL","localhost")
      self.dapr_secretstore = os.getenv("DAPR_SECRET_STORE","local-secret-store")
      self.secret = os.getenv("SECRET","secret")
      self.dapr_port = os.getenv("DAPR_HTTP_PORT", 3500)
      return
    
    def get(self, key):
      dapr_url = "http://{}:{}/v1.0/secrets/{}/{}".format(self.dapr_url,self.dapr_port,self.dapr_secretstore,key)
      result = requests.get(
        url=dapr_url
      )
      return result



