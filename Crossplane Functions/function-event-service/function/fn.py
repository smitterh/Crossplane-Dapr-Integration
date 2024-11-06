"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1
import json

from function.dlock import DLock

class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()
        self.dlock = DLock()
        self.log.info("Initialized FunctionRunner")

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function function-event-service")

        rsp = response.to(req)

        watch = ""
        if "watch" in req.input:
            watch = req.input["watch"]
        expiryInSeconds = 60
        if "expiryInSeconds" in req.input:
            expiryInSeconds = req.input["expiryInSeconds"]

        # TODO: Add your function logic here!
        #print(f"*** kind: {req.observed.composite.resource['kind']}")
        #print(f"*** status->conditions: {req.observed.composite.resource['status']['conditions']}")
        if req.observed.composite.resource["kind"] == watch:
           if "status" in req.observed.composite.resource:
              for x in req.observed.composite.resource["status"]["conditions"]:
                 if x['type'] == "Ready":
                     if self.dlock.lock(watch, expiryInSeconds):
                        log.info(f"Composite resource {watch} is Ready. This the first notification. All other are redundant.")
                        ''' 
                        Insert here any logic you want executed once for the duration of the lock.
                        This can be updating a state store and/or sending an event to a pub/sub middleware or
                        a notification to an operator.
                        '''
                     else:
                        log.info(f"Composite resource {watch} is Ready. This is a redundant notification.")

        response.normal(rsp, f"function-event-service was run to watch {watch} Composite resources.")
        log.info(f"function-event-service was run to watch {watch} Composite resources.")

        return rsp
