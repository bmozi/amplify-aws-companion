"""Run and remove one isolated exercise on the local Rancher Desktop cluster.

No AWS CLI, cloud cluster or registry push is used. A cached base is required.
"""

import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlparse
from uuid import uuid4


HERE = Path(__file__).resolve().parent
CONTEXT = "rancher-desktop"


def command(*args, input_text=None, timeout=120):
    result = subprocess.run(args, input=input_text, text=True, capture_output=True,
                            timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def kubectl(*args, namespace=None, input_text=None, timeout=120):
    prefix = ["kubectl", "--context", CONTEXT]
    if namespace:
        prefix += ["--namespace", namespace]
    return command(*prefix, *args, input_text=input_text, timeout=timeout)


def preflight():
    config = json.loads(kubectl("config", "view", "--minify", "--output=json"))
    server = config["clusters"][0]["cluster"]["server"]
    if urlparse(server).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError(f"Refusing non-loopback Kubernetes API for {CONTEXT}")
    if command("docker", "--context", CONTEXT, "info", "--format", "{{.OSType}}") != "linux":
        raise RuntimeError("The local Rancher Desktop Docker daemon is unavailable")
    # Refuse before building if the required base is absent from this daemon.
    command("docker", "--context", CONTEXT, "image", "inspect", "python:3.13-slim")
    return server


def deployment_status(namespace):
    data = json.loads(kubectl("get", "deployment", "booking-api", "--output=json",
                              namespace=namespace))
    return {"desired": data["spec"]["replicas"],
            "ready": data.get("status", {}).get("readyReplicas", 0),
            "available": data.get("status", {}).get("availableReplicas", 0)}


def customer_result(namespace):
    data = kubectl("exec", "deployment/booking-api", "--", "python", "/app/probe.py",
                   namespace=namespace)
    return json.loads(data)


def pending_reason(namespace):
    for _ in range(30):
        data = json.loads(kubectl("get", "pod", "impossible-worker", "--output=json",
                                  namespace=namespace))
        for condition in data.get("status", {}).get("conditions", []):
            if condition.get("reason") == "Unschedulable":
                return {"phase": data["status"]["phase"],
                        "reason": condition["reason"],
                        "message": condition.get("message", "")}
        time.sleep(1)
    raise RuntimeError("The impossible worker did not report Unschedulable within 30 seconds")


def remove_namespace(namespace, owner):
    raw = kubectl("get", "namespace", namespace, "--ignore-not-found", "--output=json")
    if not raw:
        return
    data = json.loads(raw)
    if data.get("metadata", {}).get("labels", {}).get("amplify-lab-owner") != owner:
        raise RuntimeError("Refusing cleanup of namespace with different ownership: " + namespace)
    kubectl("delete", "namespace", namespace, "--ignore-not-found", "--wait=true",
            "--timeout=90s", timeout=105)


def run():
    api_server = preflight()
    suffix = uuid4().hex
    namespace = f"amplify-k8s-reality-{suffix}"
    image = f"amplify-k8s-reality:local-{suffix}"
    print(f"Local lab scope: namespace={namespace} image={image}", file=sys.stderr,
          flush=True)
    namespace_attempted = False
    result = None
    try:
        command("docker", "--context", CONTEXT, "build", "--pull=false", "--network=none",
                "--tag", image, str(HERE), timeout=180)
        namespace_attempted = True
        kubectl("create", "--filename=-", input_text=json.dumps({
            "apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": namespace, "labels": {"amplify-lab-owner": suffix}},
        }))
        manifest = (HERE / "deployment.yaml").read_text().replace(
            "amplify-k8s-reality:local", image)
        kubectl("apply", "--filename=-", namespace=namespace, input_text=manifest)
        kubectl("rollout", "status", "deployment/booking-api", "--timeout=90s",
                namespace=namespace, timeout=105)
        wrong_deployment = deployment_status(namespace)
        wrong_customer = customer_result(namespace)
        if wrong_deployment != {"desired": 2, "ready": 2, "available": 2}:
            raise AssertionError(f"Expected two available Pods: {wrong_deployment}")
        if wrong_customer != {"http_status": 200,
                              "body": {"id": "42", "amount_cents": 900}}:
            raise AssertionError(f"Expected wrong but successful response: {wrong_customer}")

        kubectl("set", "env", "deployment/booking-api", "BOOKING_AMOUNT=2300",
                namespace=namespace)
        kubectl("rollout", "status", "deployment/booking-api", "--timeout=90s",
                namespace=namespace, timeout=105)
        corrected_deployment = deployment_status(namespace)
        corrected_customer = customer_result(namespace)
        if corrected_deployment != {"desired": 2, "ready": 2, "available": 2}:
            raise AssertionError(f"Corrected rollout is not available: {corrected_deployment}")
        if corrected_customer != {"http_status": 200,
                                  "body": {"id": "42", "amount_cents": 2300}}:
            raise AssertionError(f"Corrected customer result not observed: {corrected_customer}")

        pending_manifest = (HERE / "pending-pod.yaml").read_text().replace(
            "amplify-k8s-reality:local", image)
        kubectl("apply", "--filename=-", namespace=namespace, input_text=pending_manifest)
        pending = pending_reason(namespace)
        if pending["phase"] != "Pending":
            raise AssertionError(f"Expected Pending Pod: {pending}")
        result = {"local_api_server": api_server,
                  "wrong_release": {"deployment": wrong_deployment,
                                    "customer": wrong_customer},
                  "corrected_release": {"deployment": corrected_deployment,
                                        "customer": corrected_customer},
                  "oversized_worker": pending,
                  "scope": "Rancher Desktop only; synthetic data and local image; no EKS, AWS IAM, load balancer, bill, or measured customer workload"}
    finally:
        try:
            if namespace_attempted:
                remove_namespace(namespace, suffix)
        finally:
            # A failed build may not have created the tag. Inspect before removal.
            found = command("docker", "--context", CONTEXT, "image", "ls",
                            "--quiet", "--filter", "reference=" + image)
            if found:
                command("docker", "--context", CONTEXT, "image", "rm", image)
    if result is None:
        raise RuntimeError("Local exercise ended before collecting its observations")
    result["cleanup"] = {"namespace": namespace, "deleted": True,
                         "image": image, "removed": True}
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
