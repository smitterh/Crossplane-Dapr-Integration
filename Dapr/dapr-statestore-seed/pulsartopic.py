class PulsarTopic:

    def init(self):
        pass

    def factory(self) -> dict:
        template = "template-pulsar-topic"
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
                            "kind": "PulsarTopic",
                            "metadata": {
                                "name": "placeholder",
                                "namespace": "placeholder"
                            },
                            "spec": {
                                "name": "placeholder",
                                "connectionRef": {
                                    "name": "placeholder"
                                },
                                "partitions": 0,
                                "persistent": False,
                                "maxProducers": 8,
                                "maxConsumers": 8,
                                "retentionTime": "20h",
                                "retentionSize": "2Gi",
                                "backlogQuotaLimitTime": "24h",
                                "backlogQuotaLimitSize": "1Gi",
                                "backlogQuotaRetentionPolicy": "producer_request_hold",
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