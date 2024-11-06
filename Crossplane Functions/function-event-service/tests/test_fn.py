import dataclasses
import unittest

from crossplane.function import logging, resource
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from google.protobuf import duration_pb2 as durationpb
from google.protobuf import json_format
from google.protobuf import struct_pb2 as structpb

from function import fn


class TestFunctionRunner(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        # Allow larger diffs, since we diff large strings of JSON.
        self.maxDiff = 2000

        logging.configure(level=logging.Level.DISABLED)

    async def test_run_function(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            reason: str
            req: fnv1.RunFunctionRequest
            want: fnv1.RunFunctionResponse

        cases = [
            TestCase(
                reason="The function should return the input as a result.",
                req=fnv1.RunFunctionRequest(
                    input=resource.dict_to_struct({"example": "Hello, world"})
                ),
                want=fnv1.RunFunctionResponse(
                    meta=fnv1.ResponseMeta(ttl=durationpb.Duration(seconds=60)),
                    desired=fnv1.State(),
                    results=[
                        fnv1.Result(
                            severity=fnv1.SEVERITY_NORMAL,
                            message="I was run with input Hello, world!",
                        )
                    ],
                    context=structpb.Struct(),
                ),
            ),
        ]

        runner = fn.FunctionRunner()

        for case in cases:
            got = await runner.RunFunction(case.req, None)
            self.assertEqual(
                json_format.MessageToDict(case.want),
                json_format.MessageToDict(got),
                "-want, +got",
            )


if __name__ == "__main__":
    unittest.main()
