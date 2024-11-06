"""A Crossplane composition function."""
import time
import grpc
from crossplane.function import logging, resource, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

from function.policyvalidation import PolicyValidation

class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()
        self.validator = PolicyValidation()
        self.log.info("Initialized FunctionRunner")

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = response.to(req)
        
        """ Call Policy Validation passing the req and rsp """
        log.info("Calling validator")
        result = await self.validator.validate(req, rsp)
        result = result.upper()

        if result == "PASS":
            response.normal(rsp, "Policy Validation Passed")
        elif result == "FAIL": 
            response.fatal(rsp,"Policy Validation Failed")
        elif result == "LOCKED": 
            response.normal(rsp,"Policy Validator is currently locked to prevent an overload. Pass/Fail Response already provided. Check Events.")
        else:
            log.info(f"Unexpected result {result}")
            response.fatal(rsp,"Policy Validation Failed - Unexpected result")
        return rsp
