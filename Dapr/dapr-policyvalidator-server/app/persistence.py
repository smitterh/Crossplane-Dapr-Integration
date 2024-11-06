import os
import time
import subprocess
import json
import yaml
import requests

class Persistence():
      
      def __init__(self):
         """ Get all the class variables needed to store resources temporarily, access policies and tests """
         self.path_resources = os.getenv("PATH_TO_RESOURCES", "/Users/hugosmitter/Documents/kyverno-output")
         self.path_policies = os.getenv("PATH_TO_KYVERNO_POLICIES", "/Users/hugosmitter/Documents/kyverno-output")
         self.target_folder = ""
         self.kyverno_repo = os.getenv("KYVERNO_REPO","smitterh")
         self.command = f"kyverno test {self.path_resources}"
         self.dapr_url = os.getenv("DAPR_URL","localhost")
         self.dapr_secretstore = os.getenv("DAPR_SECRET_STORE","local-secret-store")
         self.dapr_github_secret = os.getenv("GITHUB_SECRET","github-smitterh-readonly")
         self.dapr_port = os.getenv("DAPR_HTTP_PORT")
         return
    
      def get_github_pat(self) -> str:
         dapr_url = f"http://{self.dapr_url}:{self.dapr_port}/v1.0/secrets/{self.dapr_secretstore}/{self.dapr_github_secret}"
         try:
            result = requests.get(
                    url=dapr_url
                    )
         except:
            print(f"persistent->get_github_pat: Malformed Dapr request to Secrets Building Block. Secret: {self.dapr_github_secret} Secret Store: {self.dapr_secretstore} failed")
            return ""
         
         if result.status_code == 200:
            """ result.content = {'secretname' : secret}"""
            t = json.loads(result.content)
            if t[self.dapr_github_secret] != "":
               return t[self.dapr_github_secret]
         elif result.status_code == 204:
            print(f"persistent->get_github_pat: Secret not found. Status Code: {str(result.status_code)}")
            return ""
         elif result.status_code == 400:
            print(f"persistent->get_github_pat: Secret store is missing or misconfigured. Status Code: {str(result.status_code)}")
            return ""
         elif result.status_code == 403:
            print(f"persistent->get_github_pat: Access denied to secret {self.dapr_github_secret}. Status Code: {str(result.status_code)}")
            return ""
         else:
            print(f"persistent->get_github_pat: Failed to get secret or no secret stores define. Status Code: {str(result.status_code)}")
            return ""

      def persist_resources(self, target_folder, resources_list: list) -> bool:
         self.target_folder = target_folder
         """ Create resources directory in the target folder """
         command = f"mkdir {self.path_resources}/{self.target_folder}/resources"
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
         except:
            print(f"Error creating resources folder:  {self.path_resources}/{self.target_folder}/resources")
            print(result.stderr)
            return False

         """ Convert the payload into YAML and then persists the output in a file system"""
         tname = f"{self.path_resources}/{self.target_folder}/resources/resources.tmp"
         fname = f"{self.path_resources}/{self.target_folder}/resources/resources.yaml"
         try:
            with open(tname, 'w') as file:
               for resource in resources_list:
                  yaml.dump(resource, file, default_flow_style=False)
                  file.write("---\n")
            print("persistence->persist_resources: wrote resources in target folder")
         except:
            print(f"persistence->store->persist_resources: failed writing file {tname}")
            return False
         
         """ Convert the booleans in the YAML files from string back to boolean as they should be"""
         try:
            with open(tname, 'r') as input:
               with open(fname, 'w') as output:
                  l = input.read()
                  l = l.replace("'false'", "false")
                  l = l.replace("'true'", "true")
                  l = l.replace("'False'", "False")
                  l = l.replace("'True'", "True")
                  output.write(l)
         except:
            print(f"persistence->store->persist_resources: failed writing file {fname}")
            return False
         
         """ Delete tmp file in the target folder """
         command = f"rm {self.path_resources}/{self.target_folder}/resources/*.tmp"
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
         except:
            print(f"Error deleting temp file:  {self.path_resources}/{self.target_folder}/resources/*.tmp")
            print(result.stderr)
            return False
         
         
      def persist_kyverno_policies_tests(self, target_folder) -> bool:
         self.target_folder = target_folder
         """ Clone the git repo with the policies and tests """
         """ Make sure to delete first the local repo clone of policies and tests """
         command = f"rm -rf {self.path_policies}/{self.target_folder}"
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            t = result.stdout
            if t.find("No such file or directory") > 0:
               print(f"Error deleting folder {self.path_policies}/{self.target_folder}")
         except:
            print(f"Error deleting folder {self.path_policies}/{self.target_folder}")
            print(result.stderr)
         """ Create target directory """
         command = f"mkdir {self.path_resources}/{self.target_folder}"
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
         except:
            print(f"Error creating resources folder: {self.path_resources}/{self.target_folder}")
            print(result.stderr)
            return False
         """ Clone the Kyverno repo with policies and tests """
         """ Use Dapr to obtain the read-only secret to access GitHub repo """
         github_pat = self.get_github_pat()
         if github_pat == "":
            print(f"persistence->persist_kyverno_policies_tests: failed accessing GitHub repo {self.kyverno_repo}")
            return False
         kyverno_repo = f"{self.kyverno_repo}/{self.target_folder}.git"
         command = f"cd {self.path_policies}/{self.target_folder};git clone https://{github_pat}@github.com/{kyverno_repo} ."
         try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)
         except:
            print(f"Error cloning {self.kyverno_repo} in {self.path_policies}/{self.target_folder}")
            print(result.stdout)
            print(result.stderr)
            return False
         return True
