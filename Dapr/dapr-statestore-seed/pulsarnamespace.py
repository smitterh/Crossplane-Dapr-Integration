class PulsarNamespace:

    def init(self):
        pass

    def factory(self) -> dict:
        template = "template-pulsar-namespace"
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
                                "kind": "PulsarNamespace",
                                "metadata": {
                                    "name": "template-pulsar-namespace",
                                    "namespace": "test"
                                },
                                "spec": {
                                    "name": "test-tenant/testns",
                                    "connectionRef": {
                                        "name": "placeholder"
                                    },
                                    "backlogQuotaLimitSize": "1Gi",
                                    "backlogQuotaLimitTime": "10h",
                                    "bundles": 16,
                                    "messageTTL": "1h",
                                    "backlogQuotaRetentionPolicy": "producer_request_hold",
                                    "maxProducersPerTopic": 2,
                                    "maxConsumersPerTopic": 2,
                                    "maxConsumersPerSubscription": 2,
                                    "retentionTime": "24h",
                                    "retentionSize": "2Gi",
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