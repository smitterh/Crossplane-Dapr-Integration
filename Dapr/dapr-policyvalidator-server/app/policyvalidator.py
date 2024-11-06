import os
import json
import time
import subprocess
from ast import literal_eval
from kyvernocli import KyvernoCLI
from persistence import Persistence
from dlock import DLock


class PolicyValidator:
    def __init__(self):
      """ Get all the class variables needed to store resources temporarily, access policies and tests """
      self.path_resources = os.getenv("PATH_TO_RESOURCES", "/Users/hugosmitter/Documents/kyverno-output")
      self.path_policies = os.getenv("PATH_TO_KYVERNO_POLICIES", "/Users/hugosmitter/Documents/kyverno-output")
      self.dlock_expiry_seconds = os.getenv("DLOCK_EXPIRY_SECONDS", "60")
      self.target_folder = "default_target_folder"
      self.kyverno_cli = KyvernoCLI()
      self.persistence = Persistence()
      self.dlock = DLock()
      return
    
    def clean_up_resources(self):
      """ 
      Make sure to delete target target folder prior to leaving 
      """
      folder = f"{self.path_resources}/{self.target_folder}"
      command = f"rm -rf {folder}"
      try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"persistence->clean_up_resources: Deleted folder: {folder}")
        if result.stdout.find("No such file or directory") > 0:
            print(f"persistence->clean_up_resources: Error deleting folder: {folder}")
            return 
      except:
        print(f"persistence->clean_up_resources: Error deleting folder: {folder}")
        print(result.stderr)
        return 

    def construct_target_folder_name(self, apiVersion: str, kind: str) -> str:
       """ 
       Using the apiVersion and kind parameters of the Crossplane Request
       construct a string to be used as the name of the folder where 
       resources, tests and policies will be stored for this policyvalidator run

       This default strategy is simple: concatenate kind and apiVersion with a '-'
       and replace any '/' with a '-' so the string becomes a valid Linux folder name.
       """
       name = f"{kind}-{apiVersion}"
       name = name.replace('/','-')
       name = name.replace('"','')
       return name
    
    def fake_rsp(self) -> str:
       """
       For testing purposes, define a a fake rsp coming from Crossplane
       """
       x =  {
              "meta": {
                "ttl": "60s"
              },
              "desired": {
                "resources": {
                  "tenant-1234567-mytopic": {
                    "resource": {
                      "kind": "Object",
                      "metadata": {
                        "name": "tenant-1234567-mytopic"
                      },
                      "apiVersion": "kubernetes.crossplane.io/v1alpha2",
                      "spec": {
                        "providerConfigRef": {
                          "name": "provider-kubernetes"
                        },
                        "forProvider": {
                          "manifest": {
                            "apiVersion": "resource.streamnative.io/v1alpha1",
                            "kind": "PulsarTopic",
                            "metadata": {
                                "name": "placeholder",
                                "namespace": "placeholder"
                            },
                            "spec": {
                                "name": "placeholder",
                                "connectionRef": {
                                    "name": "placeholder"
                                },
                                "partitions": 0,
                                "persistent": False,
                                "maxProducers": 8,
                                "maxConsumers": 8,
                                "retentionTime": "20h",
                                "retentionSize": "2Gi",
                                "backlogQuotaLimitTime": "24h",
                                "backlogQuotaLimitSize": "1Gi",
                                "backlogQuotaRetentionPolicy": "producer_request_hold",
                                "lifecyclePolicy": "CleanUpAfterDeletion"
                            }
                          }
                        }
                      }
                    }
                  }
                }
              },
              "context": {}
            }
       return json.dumps(x)

    def validate(self, validation_payload: list, apiVersion: str, kind: str, test: str) -> str:
      """
      Construct the target folder name where resources will be stored for this policy validation
      This name will also be used to map against the GitHub repo from where the policies and tests will be cloned from
      The name is also used to identify a lock to prevent multiple executions of the policyvalidator in a given period
      """
      self.target_folder = self.construct_target_folder_name(apiVersion, kind)
      """
      Issue a lock for this kind-apiVersion resource with policyvalidator as the lock owner.
      A dlock.lock call will only return True when the lock is acquired. It will return False in any other attempt
      until a dlock.unlock for the same resourceID/owner is issued or the lock expires for that same resourceID/owner.
      """
      result = self.dlock.lock(self.target_folder, self.dlock_expiry_seconds)
      if result.upper() == "FALSE":
        return "LOCKED"
      print(f"validate: dlock issued for resource: {self.target_folder} to expire in {self.dlock_expiry_seconds} seconds")
      
      """
      For testing purposes, allow injecting a fake validation payload
      In any case, convert validation_payload JSON string into a dict
      Note: Boolean coversion is tricky. In Python you have to convert booleans
      back to strings before loading them into Python dict structures
      """
      if test == "False":
        temp_payload = json.loads(validation_payload)
        temp_payload = temp_payload.replace('True',"'True'")
        temp_payload = temp_payload.replace('true',"'true'")
        temp_payload = temp_payload.replace('False',"'False'")
        temp_payload = temp_payload.replace('false',"'false'")
        rsp2dict = dict(literal_eval(temp_payload))
      else:
        rsp2dict = json.loads(self.fake_rsp())
        print("validate: *** Running in Test mode ***")
  
      """
      Strip Crossplane metadata from resources to be tested
      """
      try:
         rsp2dict = rsp2dict["desired"]["resources"]
      except:
         print(f"Failed parsing validation_payload: {rsp2dict}")
         return "FAIL"

      """ 
      Clone Kyverno policies and tests into target folder
      """
      result = self.persistence.persist_kyverno_policies_tests(self.target_folder)
      if result == "False":
         return "FAIL"

      """
      Construct list of resources to be validated by Kyverno CLI
      and persist resources in the target folder
      """
      resources_list = []
      keys = rsp2dict.keys()
      for k in keys:
          r = rsp2dict[k]
          resources_list.append(r["resource"])
      
      result = self.persistence.persist_resources(self.target_folder, resources_list)
      if result == False:
         return "FAIL"
      
      """
      Call the Kyverno CLI to test resources against policies
      """
      result = self.kyverno_cli.invoke_cli(self.target_folder)
      if int(result["tests_failed"]) == 0:
          return "PASS"
      else:
          print(f"Number of tests failed: {str(result['tests_failed'])}")
          return "FAIL"
      
    

