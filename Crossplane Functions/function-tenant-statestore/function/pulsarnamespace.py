import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

class PulsarNamespace:

    def __init__(self):
      self.log = logging.get_logger()
      self.name = "PulsarNamespace"
      pass 

    def template_name(self):
      return "template-pulsar-namespace"

    def process(self, configdb, req, rsp):
        log = self.log.bind(tag=req.meta.tag)
        # Query the configuration database - ConfigDB
        configdb_response = configdb.get(self.template_name())
        if configdb_response.status_code == 200:
            xconf = configdb_response.json()
            log.info("Found configuration data for key=%s",{self.template_name()})
            
            # TODO: Use the configuration data in configdb_response.json() dictionary to modify rsp
            rsp = self.FillTemplate(req, rsp, xconf)
            
            log.info(f"{self.name}: template population completed for {self.template_name()}")
        else:
            log.info(f"{self.name}: configuration data not found: {template_key}")
            response.fatal(rsp,f"{self.name} population failed with this input {self.template_name()}")
            log.info(f"{self.name} template population failed with this input {self.template_name()}" )
        
        return rsp
    
    
    def FillTemplate(self, req, rsp, xconf):
        log = self.log.bind(tag=req.meta.tag)
        # XR or Claim Spec parameters
        pulsarConnection = req.observed.composite.resource["spec"]["parameters"]["pulsarTenant"]["pulsarConnection"]
        pulsarClusterNamespace  = req.observed.composite.resource["spec"]["parameters"]["pulsarTenant"]["pulsarClusterNamespace"]
        pulsarTenantId   = req.observed.composite.resource["spec"]["parameters"]["pulsarTenant"]["pulsarTenantId"]
        pulsarNamespace  = req.observed.composite.resource["spec"]["parameters"]["pulsarTenant"]["pulsarNamespace"]
        pulsarTopic = req.observed.composite.resource["spec"]["parameters"]["pulsarTenant"]["pulsarTopic"]
        log.info("Processed req.observed.composite.resource parms")
        #
        # Kubernetes Provider wrapper Object metadata section
        #
        xconf["metadata"]["name"] = pulsarNamespace
        # Object spec section
        obj = xconf["spec"]["forProvider"]["manifest"]
        # Object -> PulsarTenant metadata section
        obj["metadata"]["name"] = pulsarNamespace
        obj["metadata"]["namespace"] = pulsarClusterNamespace
        log.info("Processed metadata parms in template")
        # Object -> PulsarTenant spec section
        obj["spec"]["name"] = f"{pulsarTenantId}/{pulsarNamespace}"
        obj["spec"]["connectionRef"]["name"] = pulsarConnection
        log.info("Processed spec parms in template")
        xconf["spec"]["forProvider"]["manifest"] = obj
        # Create resources 
        rsp.desired.resources[pulsarNamespace].resource.update(xconf)
        return rsp 