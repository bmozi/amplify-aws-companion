# Command-scope reasoning check

The local Kubernetes runner asks `kubectl` for its named `rancher-desktop` context, then rejects an API endpoint whose hostname is not loopback. It also checks the named local Docker context. A remote cluster with the wrong context or a remote API address must stop **before** namespace creation. That is a source-level guard; this exercise has not tested a reader's installed Docker or Kubernetes configuration.

The AWS run wrapper calls `aws sts get-caller-identity` and exports profile credentials before passing them to Terraform. For `plan`, it also calls the credit check and requires a reviewed whole-run worksheet. Planning can contact AWS and can save local plan/state material, even if it creates no workload resource. The exact resource actions and costs depend on the configuration and account. `apply` can create resources; its short-lived plan receipt does not make an unsafe plan safe.

The live verification script invokes Lambda, reads and writes DynamoDB, receives and sends SQS messages, and writes a local evidence file. Its synthetic actor strings are not authenticated customer identities. A passing check would be evidence for the selected deployed lab and observation window, not proof of production security, a customer booking or account-wide cleanup.

**Transfer test:** If a command's filename says `test_` but it imports a module that calls an AWS SDK, the filename is not enough to call it cloud-free. Follow the entry point, subprocesses, imports, network destinations and credentials. Name the exact stop and cleanup evidence for the command you selected. The packet's four default smoke groups passed locally in the October 27 study; that does not certify every other executable file in the packet.
