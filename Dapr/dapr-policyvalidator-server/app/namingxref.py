import os
import time
import subprocess
import json
import yaml as yaml
import requests

class NamingXref():
      
      def __init__(self):
        self.path_resources = os.getenv("PATH_TO_RESOURCES", "/Users/hugosmitter/Documents/kyverno-output")
        self.path_policies = os.getenv("PATH_TO_KYVERNO_POLICIES", "/Users/hugosmitter/Documents/kyverno-output")
        self.target_folder = ""
        self.resources = []
        self.resources_names = {}
        self.resources_gen = {}
        return
      
      def _capture_resource_name(self, kind, res_name):
        """
        Initialize if necessary the global tracking of a particular resource's list of unique resource names
        and a generation number. 
        Capture a new name so we can plug it later in the kyverno test file for those resources.
        """
        if kind in self.resources:
          pass
        else:
          self.resources.append(kind)
          self.resources_names[kind] = []
          self.resources_gen[kind] = 0
        if res_name not in self.resources_names[kind]:
          self.resources_names[kind].append(res_name)
        return
      
      def _generate_resource_name(self, kind) -> str:
        """
        Initialize if necessary the global tracking of a a particular resource's list of unique resource names
        and a generation number. 
        Generate a new name so we can plug it later in the kyverno test file for those resources.
        """
        if kind in self.resources:
          try:
            self.resources_gen[kind] += 1
          except:
            self.resources_gen[kind] = 1
        else:
          self.resources.append(kind)
          
        try:
          x = self.resources_names[kind]
        except:
          self.resources_names[kind] = []
      
        res_name = f"my-{kind.lower()}-{self.resources_gen[kind]}"
        self.resources_names[kind].append(res_name)
        return res_name
            
      def _process_resources_names(self,input_dict) -> dict:
        try:
          kind = input_dict['kind']
          if kind not in self.resources:
            self.resources.append(kind)
        except:
          """ resource doesn't have a kind section. Leave it alone """
          return input_dict
        try:
          input_dict['metadata']
        except:
          """ resource doesn't have a metadata section. Leave it alone """
          return input_dict
        try:
          res_name = input_dict['metadata']['name']
          self._capture_resource_name(kind, res_name)
        except:
          """ No name, generate a name and store it """
          res_name = self._generate_resource_name(kind)
          
        input_dict['metadata'].update({'name': res_name})
        return input_dict
    
      def analyze_resources(self, target_folder) -> bool:
        self.target_folder = target_folder
        """ 
        Read the resources.yaml file into a Python dict and determine the various kind 
        and if they have a name clause in the metadata section, don't mess with it. 
        Just collect it. Otherwise, assign to the resource a name with the following 
        naming convention: my-kind-#  where # = 1... e.g.: my-vpc-1 
        """
        resources_i = f"{self.path_resources}/{self.target_folder}/resources/resources.yaml"
        resources_o = f"{self.path_resources}/{self.target_folder}/resources/resources.tmp"

        with open(resources_i, 'r') as file:
              input_list = list(yaml.safe_load_all(file))
              output_list = []
              input_dict = {}
              output_dict = {}
              for d in input_list:
                input_dict = d
                if input_dict != None:
                  output_dict = self._process_resources_names(input_dict)
                  output_list.append(output_dict)
        with open(resources_o, 'w') as file:
          for resource in output_list:
            yaml.dump(resource, file, default_flow_style=False)
            file.write("---\n")
            
        """ Delete yaml file in the target folder """
        command = f"rm {self.path_resources}/{self.target_folder}/resources/resources.yaml"
        try:
          result = subprocess.run(command, shell=True, capture_output=True, text=True)
        except:
          print(f"Error deleting yaml file:  {self.path_resources}/{self.target_folder}/resources/resources.yaml")
          print(result.stderr)
          return False
        """ Rename tmp to yaml file in the target folder """
        command = f"mv {self.path_resources}/{self.target_folder}/resources/resources.tmp {self.path_resources}/{self.target_folder}/resources/resources.yaml"
        try:
          result = subprocess.run(command, shell=True, capture_output=True, text=True)
        except:
          print(f"Error renaming resources.tmp file to resources.yaml file:  {self.path_resources}/{self.target_folder}/resources/resources.yaml")
          print(result.stderr)
          return False
        return True  
      
            
      def _process_test_resources(self, input_dict) -> dict:
        """
        """
        output_dict = {}
        """ Create a copy of input_dict with an empty 'results' list """ 
        input_keys = input_dict.keys()
        for key in input_keys:
          output_dict[key] = input_dict[key]
          if key == 'results':
            output_dict[key] = []
        
        for result in input_dict['results']:
          
          if result['kind'] in self.resources_names:
            try:
              x = result['resources']
              result['resources'] = list(x) + list(self.resources_names[result['kind']])
            except:
              result['resources'] = list(self.resources_names[result['kind']])
            output_dict['results'].append(result)
            
        return output_dict
            
      def analyze_tests(self, target_folder) -> bool:
        self.target_folder = target_folder
        """ 
        Read the kyverno-tests.yaml file into a Python dict and determine the various kind 
        and if they have a name clause in the metadata section, don't mess with it. 
        Just collect it. Otherwise, assign to the resource a name with the following 
        naming convention: my-kind-#  where # = 1... e.g.: my-vpc-1 
        """
        tests_i = f"{self.path_resources}/{self.target_folder}/tests/kyverno-test.yaml"
        tests_o = f"{self.path_resources}/{self.target_folder}/tests/kyverno-test.tmp"

        with open(tests_i, 'r') as file:
              input_list = list(yaml.safe_load_all(file))
              output_list = []
              input_dict = {}
              output_dict = {}
              for d in input_list:
                input_dict = d
                if input_dict != None:
                  output_dict = self._process_test_resources(input_dict)
                  output_list.append(output_dict)
        with open(tests_o, 'w') as file:
          for test in output_list:
            yaml.dump(test, file, default_flow_style=False)
            file.write("---\n")
        
        """ Delete yaml file in the target folder """
        command = f"rm {self.path_resources}/{self.target_folder}/tests/kyverno-test.yaml"
        try:
          result = subprocess.run(command, shell=True, capture_output=True, text=True)
        except:
          print(f"Error deleting yaml file:  {self.path_resources}/{self.target_folder}/tests/kyverno-test.yaml")
          print(result.stderr)
          return False
        """ Rename tmp to yaml file in the target folder """
        command = f"mv {self.path_resources}/{self.target_folder}/tests/kyverno-test.tmp {self.path_resources}/{self.target_folder}/tests/kyverno-test.yaml"
        try:
          result = subprocess.run(command, shell=True, capture_output=True, text=True)
        except:
          print(f"Error renaming kyverno-test.tmp file to kyverno-test.yaml file:  {self.path_resources}/{self.target_folder}/tests/kyverno-test.yaml")
          print(result.stderr)
          return False
        return True