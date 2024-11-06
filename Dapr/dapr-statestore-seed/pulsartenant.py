class PulsarTenant:

    def init(self):
        pass

    def factory(self) -> dict:
        template = "template-pulsar-tenant"
        data = {
                "apiVersion": "kubernetes.crossplane.io/v1alpha2",
                "kind": "Object",
                "metadata": {
                    "name": "placeholder"
                },
                "spec": {
                    "forProvider": {
                        "manifest": {
                            "apiVersion": "resource.streamnative.io/v1alpha1",
                            "kind": "PulsarTenant",
                            "metadata": {
                                "name": "placeholder",
                                "namespace": "placeholder",
                                "labels": {},
                                "annotations": {}
                            },
                            "spec":{
                                "name": "placeholder",
                                "connectionRef": {
                                    "name": "placeholder"
                                },
                                "adminRoles": [],
                                "lifecyclePolicy": "CleanUpAfterDeletion"
                            }
                        }
                    },
                    "providerConfigRef": {
                        "name": "provider-kubernetes"
                    }
                }
        }
        return {"template": template, "data": data}