import time
import logging
import requests
import os
import json

class DLock:

    def __init__(self):
      self.dapr_url = os.getenv("DAPR_URL","localhost")
      self.dapr_port = os.getenv("DAPR_HTTP_PORT")
      self.dapr_dlock = os.getenv("DAPR_DLOCK","redis-lock")
      self.lockOwner =  os.getenv("DAPR_DLOCK_OWNER","policyvalidator")
      logging.info("Hello from DLock! my Dapr Configuration Component is: %s",{self.dapr_dlock})
      return
    
    def lock(self, resourceId, expiryInSeconds):
      dapr_url = "http://{}:{}/v1.0-alpha1/lock/{}".format(self.dapr_url,self.dapr_port,self.dapr_dlock)
      headers = {"Content-Type":"application/json"}
      lock = {"resourceId": resourceId, "lockOwner": self.lockOwner, "expiryInSeconds": expiryInSeconds}
      response = requests.post(
        headers=headers,
        json=lock,
        url=dapr_url
      )
      """
      status_code == 200 is normal. The "success" variable can be True if lock is successful or False
      """
      if response.status_code == 200:
         response_dict = json.loads(response.content)
         return str(response_dict["success"])
      else:
         return "False"

    
    def unlock(self, resourceId):
      dapr_url = "http://{}:{}/v1.0-alpha1/unlock/{}".format(self.dapr_url,self.dapr_port,self.dapr_dlock)
      headers = {"Content-Type":"application/json"}
      lock = {"resourceId": resourceId, "lockOwner": self.lockOwner}
      response = requests.post(
        headers=headers,
        json=lock,
        url=dapr_url
      )
      if response.status_code == 200:
         response_dict = json.loads(response.content)
         if response_dict["status"] == 0:
            return True
         else:
            return False
      else:
         return False
    
    def hello(self):
      logging.info("Hello from DLock! my Dapr Configuration Component is: %s",{self.dapr_dlock})