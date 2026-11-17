"""Classify fictional observations; never calls AWS or controls resources."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    alert_received: bool
    named_worker_stop_reported: bool
    replacement_observed: bool
    volume_present: bool
    full_inventory_verified: bool
    later_billing_reconciled: bool


def classify(evidence: Evidence) -> dict:
    """Return only what the supplied fixture says, not inferred cloud state."""
    if not isinstance(evidence, Evidence) or any(type(value) is not bool for value in vars(evidence).values()):
        raise ValueError('Use explicit boolean observations for every evidence field')
    return {
        'alert': 'received' if evidence.alert_received else 'not observed',
        'named_worker_stop': 'reported' if evidence.named_worker_stop_reported else 'not observed',
        'replacement': 'observed' if evidence.replacement_observed else 'not observed',
        'volume': 'present' if evidence.volume_present else 'not observed present',
        'full_inventory': 'reported verified' if evidence.full_inventory_verified else 'not verified',
        'later_billing': 'reported reconciled' if evidence.later_billing_reconciled else 'not reconciled',
        'scope': 'Fictional input labels only; no resource state, bill or cleanup verified',
    }


def main() -> None:
    import json
    timeline = Evidence(True, True, True, True, False, False)
    print(json.dumps(classify(timeline), indent=2))


if __name__ == '__main__':
    main()
