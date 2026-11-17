"""Fictional recovery-cutover gate. Pure local logic; it does not call AWS."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    trigger_confirmed: bool
    observer_fresh: bool
    recovery_point_selected: bool
    keys_and_dependencies_ready: bool
    business_records_reconciled: bool
    old_writer_fenced: bool
    survivor_capacity_proved: bool
    policy_allows_automatic_cutover: bool
    human_approval_received: bool = False


def decide(evidence: Evidence) -> tuple[str, list[str]]:
    """Return CUTOVER, WAIT_FOR_APPROVAL, or NO_GO with explicit reasons."""
    checks = (
        ('incident trigger is not confirmed', evidence.trigger_confirmed),
        ('observer evidence is stale or unavailable', evidence.observer_fresh),
        ('recovery point is not selected', evidence.recovery_point_selected),
        ('keys or dependencies are not ready', evidence.keys_and_dependencies_ready),
        ('business records are not reconciled', evidence.business_records_reconciled),
        ('old writer is not fenced', evidence.old_writer_fenced),
        ('survivor capacity is not proved', evidence.survivor_capacity_proved),
    )
    missing = [reason for reason, passed in checks if not passed]
    if missing:
        return 'NO_GO', missing
    if evidence.policy_allows_automatic_cutover:
        return 'CUTOVER', ['all declared pre-cutover evidence passed; policy permits automation']
    if evidence.human_approval_received:
        return 'CUTOVER', ['all declared pre-cutover evidence passed; named human approval recorded']
    return 'WAIT_FOR_APPROVAL', ['all declared evidence passed; policy requires named human approval']


def example_cases() -> list[tuple[str, Evidence]]:
    ready = Evidence(True, True, True, True, True, True, True, True)
    return [
        ('safe automatic path', ready),
        ('stale observer', Evidence(True, False, True, True, True, True, True, True)),
        ('unfenced old writer', Evidence(True, True, True, True, True, False, True, True)),
        ('manual gate required', Evidence(True, True, True, True, True, True, True, False)),
        ('approved manual gate', Evidence(True, True, True, True, True, True, True, False, True)),
        ('unreconciled business records', Evidence(True, True, True, True, False, True, True, True)),
    ]


def main() -> None:
    for label, evidence in example_cases():
        result, reasons = decide(evidence)
        print(f'{label}: {result} — {"; ".join(reasons)}')
    print('Fictional local policy model only: no AWS APIs, resources, timings, or prices.')


if __name__ == '__main__':
    main()
