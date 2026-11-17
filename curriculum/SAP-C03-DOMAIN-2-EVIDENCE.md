# Professional architecture domain 2: study map

Use the [AWS domain 2 guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain2.html) with these lesson and exercise links. **Partial** means the material practices part of a skill; the last column identifies evidence or practice still needed. It does not establish mastery or exam readiness. Check the current guide for your scheduled exam and verify AWS-specific claims before a real implementation.

## Task 2.1 — identity security

| Skill | Lessons and practice | Scope and further evidence |
| --- | --- | --- |
| 2.1.1 Workforce federation and provisioning | [Identity lesson](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7); [identity cases](../examples/identity-foundations/README.md) | **Partial.** Identity Center, SAML and SCIM are distinguished; no configured issuer, group lifecycle, assignment or sign-out test. |
| 2.1.2 Application and pod identity | [Identity lesson](../reader/BOOK-LOCATORS.md#book-eb08f5640c6b0750); [illustrated changed-condition lab](../examples/application-pod-identity/README.md); [tenant cases](../examples/tenant-isolation/README.md) | **Partial.** Customer token, optional direct-client credentials and EKS Pod Identity/IRSA paths are separated; a local worksheet tests binding and fallback omissions. No OAuth/client, identity pool, pod association, effective role, actual principal or customer-path denial has been observed. |
| 2.1.3 Cross-account least privilege | [Identity lesson](../reader/BOOK-LOCATORS.md#book-2556b725756e00e1); [illustrated vendor-boundary cases](../examples/vendor-access-boundary/README.md); [permission review](../examples/permission-review/README.md) | **Partial.** Eight paper cases separate cross-account caller permission, role trust with a customer-specific external ID, session narrowing, resource denial and a direct resource-policy path. No installed trust/permission readback, vendor tenant-binding observation, actual allow/deny, full cost or independent learner result exists. |
| 2.1.4 Data perimeter and external access | [Governance lesson](../reader/BOOK-LOCATORS.md#book-0ed8b61cd33d4d8d); [illustrated eight-route perimeter exercise](../examples/data-perimeter-path/README.md); [security design](../examples/professional-security-design/README.md) | **Partial.** The browser/app and worker/S3 requests have separate gates and direct-route counterexamples. No configured Verified Access endpoint, gateway endpoint, effective bucket/key denial, recovery test, cost measurement or independent learner result exists. |
| 2.1.5 Hybrid workload identity | [Outside workload lab](../examples/hybrid-workload-identity/README.md); [identity lesson](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7) | **Partial.** The six-case paper lab separates certificate trust, credential issuance, permission and network paths; no Roles Anywhere setup or live allow/deny evidence. |

## Task 2.2 — encryption and key management

| Skill | Lessons and practice | Scope and further evidence |
| --- | --- | --- |
| 2.2.1 Customer-managed at-rest keys | [Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153); [key policy lab](../examples/key-use-policy/README.md) | **Partial.** Key authorization, context and recovery are practiced; no customer-managed key creation, rotation or live decrypt-denial test. |
| 2.2.2 TLS and certificate management | [Security controls](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [TLS lab](../examples/tls-boundaries/README.md) | **Partial.** Local handshake failures and certificate ownership are concrete; no ACM/Private CA deployment and renewal observation. |
| 2.2.3 Dedicated HSM | [Custody and recovery lesson](../reader/BOOK-LOCATORS.md#book-aa4f22aba2f8c74a); [illustrated seven-case lab](../examples/dedicated-hsm-decision/README.md); [control review](../examples/protective-control-review/README.md) | **Partial.** Standard KMS, CloudHSM-backed KMS and direct CloudHSM are distinguished; the offline worksheet challenges AZ capacity, backup age, disconnected state and a high-volume path. No cluster, custom store, actual key use, restore, cost, control-owner acceptance or learner result is observed. |
| 2.2.4 Post-quantum design | [Three cryptographic jobs](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153); [migration cases](../examples/crypto-migration/README.md) | **Partial.** ML-KEM transport/key operation and ML-DSA signing are separated; interoperability and protocol tests are open. |

## Task 2.3 — multi-account governance

| Skill | Lessons and practice | Scope and further evidence |
| --- | --- | --- |
| 2.3.1 Landing zones and account vending | [Accounts lesson](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e); [account onboarding](../examples/account-onboarding/README.md) | **Partial.** OUs, Control Tower and approvals are taught on paper; no organization deployment or account-vending observation. |
| 2.3.2 Central logging, config and AI records | [Security evidence](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [audit evidence lab](../examples/security-audit-evidence/README.md); [AI four-record audit](../examples/ai-audit-evidence/README.md) | **Partial.** The case separates API activity, optional model content, agent steps and business disposition with wrong-scope, absent-log and duplicate-event controls. Security Lake, aggregation and live collection/delivery remain unverified. |
| 2.3.3 Cross-account resource sharing | [Governance lesson](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e); [multi-account paths](../examples/multi-account-paths/README.md) | **Partial.** Shared network and resource-owner distinctions exist; no configured RAM/TGW share and recipient acceptance evidence. |
| 2.3.4 SCP and RCP enforcement | [Governance lesson](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e); [governance cases](../examples/governance-review/README.md) | **Partial.** Policy ceilings and rollback are taught; no selected hierarchy, supported resource or live deny/exception proof. |
| 2.3.5 Automated compliance monitoring | [Security evidence](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [security design](../examples/professional-security-design/README.md) | **Partial.** Config and CSPM limits are explained; no configured rule, finding lifecycle or uncovered-resource test. |
| 2.3.6 Vulnerability scan and patch automation | [Security evidence](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [image review](../examples/image-review/README.md) | **Partial.** Finding triage and patch rollout concepts exist; no Inspector/Patch Manager configuration or repair verification. |

## Task 2.4 — compliance architecture

| Skill | Lessons and practice | Scope and further evidence |
| --- | --- | --- |
| 2.4.1 Data protection architecture | [Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153); [classification cases](../examples/data-classification/README.md) | **Partial.** Classify, authorize, encrypt and audit are linked; no selected regulated workload's end-to-end control test. |
| 2.4.2 Data sovereignty | [Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153); [hybrid design](../examples/hybrid-design/README.md) | **Partial.** Data location and ownership are raised; legal/control requirements need a jurisdiction-specific scenario reviewed with appropriate expertise. |
| 2.4.3 Regulated audit trails including AI | [Security evidence](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [audit evidence lab](../examples/security-audit-evidence/README.md); [AI four-record audit](../examples/ai-audit-evidence/README.md) | **Partial.** The paper design asks for AI event inventory, sensitive-content scope, retention and retrieval failures; no regulated control approval, integrity or live retrieval test exists. |
| 2.4.4 Residency and transfer controls | [Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153); [professional security design](../examples/professional-security-design/README.md) | **Partial.** Region choice and export checks exist; no complete transfer map, deny policy and tested exception path. |
| 2.4.5 AWS Artifact evidence and reporting | [Security evidence context](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d); [illustrated evidence packet](../examples/provider-evidence-packet/README.md) | **Partial.** A fictional packet practices report type, service/Region/control/period scope, shared responsibility, customer observation and protected handling. Actual report access and scope, live customer records and auditor acceptance are unverified. |
| 2.4.6 Threat model and mitigation | [Threat review](../examples/threat-review/README.md); [security controls](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d) | **Partial.** Actors, assets and negative cases are practiced; no independently reviewed risk register with mitigations and residual-risk ownership. |

## Task 2.5 — responsible AI security

| Skill | Lessons and practice | Scope and further evidence |
| --- | --- | --- |
| 2.5.1 Bedrock Guardrails | [Authorized retrieval](../reader/BOOK-LOCATORS.md#book-c7716c08655f741e); [agent evaluation](../examples/agent-evaluation/README.md) | **Partial.** Unsafe-output and authorization boundaries are discussed; no Bedrock Guardrails configuration, bypass or false-positive measurement. |
| 2.5.2 AgentCore Identity | [Agent tool boundary](../examples/agent-tool-boundary/README.md); [illustrated identity path](../examples/agentcore-identity-path/README.md) | **Partial.** The lesson separates inbound caller, workload/provider access, 3LO user consent, current resource/action grant, downstream token rejection and replay. No configured AgentCore identity, actual token binding, denial, provider effect or audit record is observed. |
| 2.5.3 Human oversight | [Approval lesson](../reader/BOOK-LOCATORS.md#book-842e431cbcce6c95); [approval cases](../examples/approval-workflow/README.md) | **Partial.** Approval-before-effect and replay are concrete; no Step Functions human task execution and timeout/duplicate evidence. |
