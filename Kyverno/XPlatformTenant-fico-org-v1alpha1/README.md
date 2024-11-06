The XPlatformTenant-fico-org-v1alpha1 is the name of the sample repo containing Kyverno policies and tests used by the Policy Validator.

The naming convention for the repo is the concatenation of the composite Resource kind and the apiVersion for the Composite resource.
In this example, the Composite resource name is XPlatformTenant and the apiVersion is fico.org/v1alpha1. 

This convention is also used to name the temporary folder used by the Kyverno test command. Therefore, '/' and '.' characters are replaced by dashes '-'.
