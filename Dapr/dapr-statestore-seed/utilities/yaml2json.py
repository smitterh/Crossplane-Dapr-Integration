import yaml 
import json
import sys

try:
   res = sys.argv[1]
except:
    sys.exit("Missing input file in the following format:  xxxx.yaml")
    
out_file = res.replace(".yaml",".json")

with open(res, 'r') as yaml_in, open(out_file, 'w') as json_out:
    yaml_object = yaml.safe_load(yaml_in)
    json_object = json.dumps(yaml_object, indent=4)
    json_out.write(json_object)
