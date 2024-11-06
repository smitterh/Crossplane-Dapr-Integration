"""
find_detail parses the output of a "kyverno test" command. The output should as follows:

Loading test  ( .kyverno-test/kyverno-test.yaml ) ...
   Loading values/variables ...
   Loading policies ...
   Loading resources ...
   Loading exceptions ...
   Applying 1 policy to 2 resources with 1 exception ...
   Checking results ...

│────│──────────────────────────│─────────────────│───────────────────────────│────────│────────│
│ ID │ POLICY                   │ RULE            │ RESOURCE                  │ RESULT │ REASON │
│────│──────────────────────────│─────────────────│───────────────────────────│────────│────────│
│ 1  │ disallow-host-namespaces │ host-namespaces │ Deployment/important-tool │ Pass   │ Ok     │
│ 2  │ disallow-host-namespaces │ host-namespaces │ Deployment/not-important  │ Pass   │ Ok     │
│────│──────────────────────────│─────────────────│───────────────────────────│────────│────────│


Test Summary: 2 tests passed and 0 tests failed
"""
import os
import time
import subprocess
import json

class KyvernoCLI:

      def __init__(self):
         """ Get all the class variables needed to store resources temporarily, access policies and tests """
         self.path_resources = os.getenv("PATH_TO_RESOURCES", "/Users/hugosmitter/Documents/kyverno-output")
         self.path_policies = os.getenv("PATH_TO_KYVERNO_POLICIES", "/Users/hugosmitter/Documents/kyverno-output")
         self.target_folder = ""
         return
   
      def find_detail(self, cli_output: str) -> dict: 
         detail_dict = {"policies_applied": 0, "resources": 0, "tests_passed": 0, "tests_failed": 0}
         """ Parse 'kyverno test' command output and determine if the resources passed the tests """
         cli_output = cli_output.replace("\n","")

         if cli_output.find("No test yamls available") > 0:
            print("kyvernocli->invokecli->find_detail: No test yamls available.")
            return detail_dict

         if cli_output.find("failed to run test") > 0:
            print("kyvernocli->invokecli->find_detail: failed to run test.")
            return detail_dict

         policies_applied_off = cli_output.find("Applying")+9
         policies_applied_end = cli_output.find("policy to")-1
         policies_applied_val = cli_output[policies_applied_off:policies_applied_end]
         policies_applied_val = policies_applied_val.strip() 
         #print("policies_applied_val "+policies_applied_val)
         
         resources_off = cli_output.find("policy to")+10
         resources_end = cli_output.find("resource",resources_off)-1
         resources_val = cli_output[resources_off:resources_end]
         resources_val = resources_val.strip()
         #print("resources_val "+resources_val)

         summary_passed_off = cli_output.find("Test Summary:")+14
         summary_passed_end = cli_output.find("tests passed")-1
         summary_passed_val = cli_output[summary_passed_off:summary_passed_end]
         summary_passed_val = summary_passed_val.strip()
         #print("summary_passed_val "+summary_passed_val)

         summary_failed_off = cli_output.find("tests passed and")+17
         summary_failed_end = cli_output.find("tests failed")-1
         summary_failed_val = cli_output[summary_failed_off:summary_failed_end]
         summary_failed_val = summary_failed_val.strip()
         #print("summary_failed_val "+summary_failed_val)

         try:
            detail_dict["policies_applied"] = int(policies_applied_val)
            detail_dict["resources"] = int(resources_val)
            detail_dict["tests_passed"] = int(summary_passed_val)
            detail_dict["tests_failed"] = int(summary_failed_val)
         except:
            print("kyvernocli->invokecli->find_detail: command output invalid.")
            print(f"{cli_output}")
            return detail_dict

         return detail_dict

      def invoke_cli(self, target_folder) -> dict:
         detail_dict = {"policies_applied": 0, "resources": 0, "tests_passed": 0, "tests_failed": 0}
         self.target_folder = target_folder
         """ Make sure the file system exists """
         command = f"ls {self.path_resources}/{self.target_folder}"
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout.find("No such file or directory") > 0:
               print(f"Error finding filesystem {self.path_resources}/{self.target_folder}")
               return detail_dict
         except:
            print(f"Error finding filesystem {self.path_resources}/{self.target_folder}")
            print(result.stderr)
            return detail_dict
         
         """ Invoke Kyverno CLI test command """
         command = f"kyverno test {self.path_resources}/{self.target_folder} --detailed-results"
         print(f"Kyverno command: {command}")
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)

         except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(result.stderr)
            return detail_dict

         if result.stdout != "":
            detail_dict = self.find_detail(result.stdout)
            return(detail_dict)