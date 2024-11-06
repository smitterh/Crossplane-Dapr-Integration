import time
import requests 
import os
import json
from google.protobuf.json_format import MessageToJson
from crossplane.function import logging, resource, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

class PolicyValidation:

    def __init__(self):
      self.dapr_url = os.getenv("DAPR_URL","localhost")
      self.dapr_port = os.getenv("DAPR_HTTP_PORT")
      self.timeout = os.getenv("SERVICE_INVOCATION_TIMEOUT", 30)
      self.pv_namespace = os.getenv("POLICY_CENTER_NAMESPACE", ".policycenter")
      self.sleep_time = os.getenv("SLEEP_TIME",10)
      self.log = logging.get_logger()

    async def s2si_policyvalidator(self, req, rsp, flag) -> str:
        log = self.log.bind(tag=req.meta.tag)
        log.info("entered s2si_policyvalidator method")
        
        if flag == "sim":
           return "PASS"
        """
        Surgery to extract kind and apiVersion from the protobuf request (req)
        Replace any '"' with '', replace '/' or '.' with '-' to build a valid target folder name
        to store resources, policies and tests. Also, a valid GitHub repo
        from where the policies and tests for this particular resource 
        will come from. 
        """
        kind = req.observed.composite.resource.fields["kind"]
        kind_json = MessageToJson(kind)
        kind_json = kind_json.replace('"', '')
        apiVersion = req.observed.composite.resource.fields["apiVersion"]
        apiVersion_json = MessageToJson(apiVersion)
        apiVersion_json = apiVersion_json.replace('/','-')
        apiVersion_json = apiVersion_json.replace('.','-')
        apiVersion_json = apiVersion_json.replace('"','')
        log.info(f"apiVersion: {apiVersion_json}, kind: {kind_json}")

        validation_payload = MessageToJson(rsp)

        headers = {}
        headers["Content-Type"] = "application/json"
        headers["pv-apiVersion"] = apiVersion_json
        headers["pv-kind"] = kind_json
        
        dapr_url = f"http://{self.dapr_url}:{self.dapr_port}/v1.0/invoke/policyvalidator{self.pv_namespace}/method/validate"
      
        try: 
           response = requests.post(dapr_url, headers=headers, json=validation_payload, timeout=self.timeout)
        except:
           log.info(f"s2si_policyvalidator: Call to policyvalidator failed. Cannot access service.")
           return "FAIL"   
        if response.status_code == 200 or response.status_code == 204:
          log.info("s2si_policyvalidator: Call to policyvalidator app succeeded")
          otext = response.text
          otext = otext.upper().replace('"','')
  
          if otext == "PASS":
             #log.info("s2si_policyvalidator: Composition passed policy validation")
             return "PASS"
          elif otext == "LOCKED":
             #log.info("s2si_policyvalidator: Policy Validator is busy processing prior request.")
             return "LOCKED"
          elif otext == "FAIL":
             #log.info("s2si_policyvalidator: Composition failed policy validation. Check logs in Policy Validator")
             return "FAIL"
          else:
             log.info(f"s2si_policyvalidator: Unexpected Result {otext}. Check logs in Policy Validator")
             return "FAIL"
        else:
          log.info(f"s2si_policyvalidator: Call to Policy Validator failed {str(response.status_code)}")
          return "FAIL"
         
    
    async def validate(self, req: fnv1.RunFunctionRequest, rsp: fnv1.RunFunctionResponse) -> str: 
      """
      Make a Service Invocation to a Policy Validation Dapr App hosting the Kyverno CLI 
      Pass the rsp as JSON. The Kyverno CLI is hosting the Policies and Tests for the Policies.
      The passed rsp will be persisted in a temporary file system so the Kyverno CLI can run a test command
      The Policy Validation will return a True/False signaling Pass/Fail depending on Kyverno CLI test result 
      """
      log = self.log.bind(tag=req.meta.tag)

      """
      Call the Policy Validation Dapr App using Service Invocation
      The Policy Validation will only fail (return False) if a) the Policy Dapr App is available and b) the policy validation fails
      In any other case, the Policy Validation will return True to avoid blocking the Crossplane pipeline.

      Call with flag=sim makes ssi_policyvalidator return PASS
      """
      result = await self.s2si_policyvalidator(req, rsp, flag="")
      result = result.upper()

      if result == "PASS":
         log.info("policyvalidation->validation: policy validation passed.")
         return "PASS"
      elif result == "FAIL": 
         log.info("policyvalidation->validation: policy validation failed.")
         return "FAIL"
      elif result == "LOCKED":
         log.info(f"policyvalidation->validation: policy validation is locked to prevent an overload. Pass/Fail response already provided. Check Events.")
         return "LOCKED"
      else:
         log.info(f"policyvalidation->validation: unexpected result {result}. Fail policy validation.")
         return "FAIL"

  