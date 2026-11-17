"""Offline audit-packet teaching model; every report and record here is fictional."""

from dataclasses import dataclass, replace
from datetime import date


@dataclass(frozen=True)
class Question:
    control: str
    service: str
    region: str
    start: date
    end: date
    resource: str


@dataclass(frozen=True)
class ReportReceipt:
    report_id: str
    provider: str
    controls: frozenset[str]
    services: frozenset[str]
    regions: frozenset[str]
    start: date
    end: date
    scope_checked: bool


@dataclass(frozen=True)
class CustomerReceipt:
    control: str
    resource: str
    observed: date
    reviewer: str
    result: str


def packet_gaps(question: Question, provider: ReportReceipt,
                customer: CustomerReceipt | None) -> list[str]:
    """Check packet metadata, never infer compliance from a document title."""
    gaps = []
    if provider.provider != "AWS" or not provider.report_id:
        gaps.append("provider document identity unverified")
    if not provider.scope_checked:
        gaps.append("actual report scope not reviewed")
    if question.control not in provider.controls:
        gaps.append("provider control not in reviewed scope")
    if question.service not in provider.services:
        gaps.append("service not in reviewed report scope")
    if question.region not in provider.regions:
        gaps.append("Region not in reviewed report scope")
    if provider.start > question.start or provider.end < question.end:
        gaps.append("report period does not cover requested window")
    if customer is None:
        gaps.append("customer configuration evidence missing")
    else:
        if customer.control != question.control or customer.resource != question.resource:
            gaps.append("customer evidence addresses a different control or resource")
        if not question.start <= customer.observed <= question.end:
            gaps.append("customer observation outside requested window")
        if not customer.reviewer or customer.result != "observed-pass":
            gaps.append("customer observation lacks a reviewed pass result")
    return gaps


def fixture() -> tuple[Question, ReportReceipt, CustomerReceipt]:
    question = Question("fictional-configuration-control", "Amazon S3", "us-east-2",
                        date(2026, 1, 1), date(2026, 6, 30), "fictional-bucket-17")
    provider = ReportReceipt("FICTIONAL-REPORT-NO-DOCUMENT", "AWS",
                             frozenset({question.control}), frozenset({question.service}),
                             frozenset({question.region}), question.start, question.end, True)
    customer = CustomerReceipt(question.control, question.resource,
                               date(2026, 6, 15), "fictional reviewer", "observed-pass")
    return question, provider, customer


def demonstrate() -> None:
    question, provider, customer = fixture()
    cases = (
        ("complete fictional metadata", provider, customer),
        ("wrong Region", replace(provider, regions=frozenset({"us-west-2"})), customer),
        ("old report", replace(provider, end=date(2025, 12, 31)), customer),
        ("AWS document only", provider, None),
    )
    for name, report, record in cases:
        print(name, "→", packet_gaps(question, report, record) or
              ["metadata coherent; actual report, configuration and auditor review unverified"])


if __name__ == "__main__":
    demonstrate()
