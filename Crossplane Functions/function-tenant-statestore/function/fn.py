"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

from function.pulsartenant import PulsarTenant
from function.pulsarnamespace import PulsarNamespace
from function.pulsartopic import PulsarTopic
from function.configdb import ConfigDB
import json


class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()
        self.configdb = ConfigDB()
        self.pulsartenant = PulsarTenant()
        self.pulsarnamespace = PulsarNamespace()
        self.pulsartopic = PulsarTopic()
        self.log.info("Initialized FunctionRunner")

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = response.to(req)

        # TODO: Add your function logic here!

        rsp = self.pulsartenant.process(self.configdb, req, rsp)
        rsp = self.pulsarnamespace.process(self.configdb, req, rsp)
        rsp = self.pulsartopic.process(self.configdb, req, rsp)

        return rsp
    
