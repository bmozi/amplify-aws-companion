# Know where a lab command runs

This companion snapshot disables direct execution of live AWS helpers. The live-account rows below describe source behavior for inspection and separate adaptation; they are not commands to run from this copy.

Maya wants to practice a recovery lesson. She sees one command that checks answers, one that creates a temporary local container, and one that applies Terraform. All three are called *labs*. They have different destinations and different cleanup jobs. Before she runs one, she asks: **What system will this command contact, what can it change, and how will I know it stopped?**

Think of three doors. A file-only exercise stays in the packet. A local service exercise also changes your computer. A live exercise reaches an account or external service. A command may cross more than one door, so check the actual entry point and its dependencies.

| Example in this companion | Boundary it crosses | What to predict and check |
| --- | --- | --- |
| `python3 scripts/check-companion.py --lab-only` | Packet files and local Python processes | Verifies the packet manifest and runs four selected cloud-free groups. Check its report; it neither deploys nor proves the other labs. |
| `python3 examples/governed-delivery/lab.py` | Local Terraform process and disposable files | Builds plans for a `terraform_data` proposal without an external provider or backend. Check the temporary plan decision and removal of local files. It does not test IAM. |
| `python3 examples/kubernetes-reality/run_lab.py` | Local Rancher Desktop Docker and Kubernetes | Builds a local image and temporarily changes a namespace. Its preflight requires loopback Kubernetes and the named local context; check namespace and image cleanup. It does not create an EKS cluster. |
| `python3 architectures/reliable-workflows/run.py plan --profile YOUR_PROFILE --cost-worksheet YOUR_WORKSHEET` | Local Terraform files **and live AWS identity, credit and provider reads** | Requires a selected profile and reviewed worksheet. Inspect identity, Region, plan, estimated whole-run cost and saved state before considering apply. A plan is not an approval or a hard spending cap. |
| `python3 architectures/reliable-workflows/run.py apply --profile YOUR_PROFILE --cost-worksheet YOUR_WORKSHEET` | **Live AWS writes** | Can create billed resources from a reviewed plan. This inspection-only specimen has example account checks and is not a ready-to-run reader deployment. Its separate destroy and absence checks are required if a suitably authorized run is ever adapted. |
| `.venv-labs/bin/python architectures/reliable-workflows/verify_live.py --profile YOUR_PROFILE --outputs YOUR_OUTPUTS --evidence YOUR_EVIDENCE` | **Live AWS reads and writes** | Invokes Lambda and changes synthetic DynamoDB and SQS work in a deployed lab. It is not a local unit test. Read its exact outputs and cleanup procedure first. |

The `examples/github-workflows/` files are teaching examples at an **inactive path**. Copying one into `.github/workflows/` can make GitHub eligible to run it when its trigger and credentials are configured. Review the workflow, repository permissions, secrets, identity trust, enable switch and artifact audience before such a change. Terraform under `infra/` is source to study; running it is a separate account decision.

The app’s `npm run build` is frontend bundling only. It neither runs full TypeScript/backend typechecking nor installs the backend/CDK development tree. See [the app build scope](../app/README.md); the unresolved private backend advisories remain a separate review.

## Try a changed condition before looking at code

First, label each row **files**, **local service**, or **live account**, allowing more than one label. Write one observation that would prove the command did what you intended and one observation it cannot provide. Now change the fact: a teammate points `kubectl` at a remote context, while another supplies a valid AWS profile to `run.py plan`. Which preflight should stop the first command? Why does the second command need a cost and identity review even though its verb is *plan*?

Check the [local Kubernetes runner](../examples/kubernetes-reality/run_lab.py) and [AWS run wrapper](../architectures/reliable-workflows/run.py) after your first answer. Ask Codex to challenge your labels by tracing subprocess calls from the entry point, then verify each claim in source. Never paste credentials, private outputs or customer records into that prompt. Compare your reasoning with the [separate assessor](COMMAND-SCOPE-ASSESSOR.md) only after you have written it down.

**Stop rule.** Use the file-only examples first. For any local service, know its process, storage and cleanup. For a live account, establish a scoped non-root identity, current plan and service eligibility, a whole-run estimate and reserve chosen for your own account, an owner who can stop and remove resources, and a later billing check. This field card classifies the named source revision; inspect a command again after its code changes. It is no substitute for running a bounded experiment and observing the real result.
