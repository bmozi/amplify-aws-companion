# Fleet maintenance: assessor notes

1. A failed canary blocks later waves. The exercise does not claim that the patch is undone; inspect actual node state and follow the approved recovery procedure.
2. Stale inventory is unknown state. Refresh or investigate, then recalculate the target set. It is not a pass.
3. The unexpected selector match changes the reviewed scope. Stop before the effect boundary and reconcile tags and approved IDs.
4. The stable operation ID retrieves the saved result. Exactly-once behavior for an external patch or operating-system operation is not established.
5. A changed baseline is a changed plan. Create a newly reviewed operation or reject the changed input; do not silently replace the accepted version.
6. Report patch compliance and application health separately. The latter is closer to customer impact, but even one smoke test is narrower than proving all business functions.

The model uses sequential waves so it can prove that no later ring starts after a failed earlier ring. It does not model the exact AWS Systems Manager scheduling algorithm, simultaneous in-flight work, quotas, package-manager behavior, reboot timing, cross-account delivery, rollbacks or billing. AWS documents that operations already running can finish after a rate-control threshold stops further dispatch. Do not generalize the fixture's state transitions to live service behavior.
