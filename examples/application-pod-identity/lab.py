"""Offline identity-path worksheet, not an IAM or Kubernetes evaluator."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Path:
    kind: str  # api, direct-client, or eks-worker
    customer_token_checked: bool = False
    business_owner_checked: bool = False
    client_aws_credentials: bool = False
    client_scope_reviewed: bool = False
    cluster: str = ""
    namespace: str = ""
    service_account: str = ""
    associated_cluster: str = ""
    associated_namespace: str = ""
    associated_service_account: str = ""
    credential_source: str = ""
    role_scope_reviewed: bool = False
    target_account_differs: bool = False
    target_grant_reviewed: bool = False


def review(path: Path) -> tuple[str, ...]:
    """Report missing design evidence without predicting a live AWS outcome."""
    issues = []
    if path.kind not in {"api", "direct-client", "eks-worker"}:
        return ("unknown identity path",)
    if path.kind in {"api", "direct-client"}:
        if not path.customer_token_checked:
            issues.append("customer token validation missing")
        if not path.business_owner_checked:
            issues.append("repair ownership check missing")
    if path.kind == "api" and path.client_aws_credentials:
        issues.append("API-mediated path unexpectedly gives browser AWS credentials")
    if path.kind == "direct-client":
        if not path.client_aws_credentials:
            issues.append("direct AWS request has no declared client credential path")
        if not path.client_scope_reviewed:
            issues.append("direct client AWS scope not reviewed")
    if path.kind == "eks-worker":
        if not all((path.cluster, path.namespace, path.service_account)):
            issues.append("pod cluster, namespace or service account missing")
        if (path.cluster, path.namespace, path.service_account) != (
            path.associated_cluster, path.associated_namespace,
            path.associated_service_account
        ):
            issues.append("Pod Identity association does not match pod binding")
        if path.credential_source != "pod-identity":
            issues.append("actual credential source is not the declared Pod Identity path")
        if not path.role_scope_reviewed:
            issues.append("workload role and target scope not reviewed")
        if path.target_account_differs and not path.target_grant_reviewed:
            issues.append("cross-account target grant not reviewed")
    return tuple(issues)


def fixture() -> Path:
    return Path(kind="eks-worker", cluster="repair-cluster", namespace="repairs",
                service_account="photo-writer", associated_cluster="repair-cluster",
                associated_namespace="repairs", associated_service_account="photo-writer",
                credential_source="pod-identity", role_scope_reviewed=True)


def demonstrate() -> None:
    base = fixture()
    cases = (
        ("declared pod path", base),
        ("moved namespace", replace(base, namespace="preview")),
        ("static-key fallback", replace(base, credential_source="static-key")),
        ("second account", replace(base, target_account_differs=True)),
    )
    for label, path in cases:
        print(f"{label}: {', '.join(review(path)) or 'worksheet complete; live result unknown'}")


if __name__ == "__main__":
    demonstrate()
