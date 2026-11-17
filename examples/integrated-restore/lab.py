"""A small, cloud-free recovery decision for one fictional booking."""
from dataclasses import dataclass
from hashlib import sha256


CONFIRMATION = {
    "booking_id": "B111",
    "amount_cents": 4400,
    "photo_digest": sha256(b"photo for booking B111\n").hexdigest(),
    "dispatch_id": "D111",
}

DATABASE_POINTS = {
    "10:00": {},
    "10:10": {"booking_id": "B111", "amount_cents": 4400, "photo_version": "v1"},
    "10:11": {"booking_id": "B111", "amount_cents": 400, "photo_version": "v2"},
}
OBJECT_VERSIONS = {
    "v1": b"photo for booking B111\n",
    "v2": b"wrong replacement photo\n",
    "v3": None,  # fictional current delete marker; earlier versions are retained
}
SENT_DISPATCHES = {"D111"}


@dataclass(frozen=True)
class Choice:
    database_point: str
    object_version: str
    replay_dispatch: bool = False


def assess(choice: Choice, confirmation=CONFIRMATION, sent_dispatches=SENT_DISPATCHES):
    """Return (accepted, reasons); never mutate the source or send an effect."""
    reasons = []
    if confirmation is None:
        return False, ["Independent confirmation is unavailable; desired state is unknown"]
    record = DATABASE_POINTS.get(choice.database_point)
    if record is None:
        reasons.append("Selected database point does not contain the confirmed booking")
    else:
        if (record.get("booking_id"), record.get("amount_cents")) != (
            confirmation["booking_id"], confirmation["amount_cents"]
        ):
            reasons.append("Booking identity or amount disagrees with confirmation")
        if record.get("photo_version") != choice.object_version:
            reasons.append("Booking points to a different object version")
    photo = OBJECT_VERSIONS.get(choice.object_version)
    if photo is None:
        reasons.append("Selected object version is missing or a delete marker")
    elif sha256(photo).hexdigest() != confirmation["photo_digest"]:
        reasons.append("Object bytes disagree with independent confirmation")
    if confirmation["dispatch_id"] not in sent_dispatches:
        reasons.append("Dispatch status is unknown; investigate before reopening")
    if choice.replay_dispatch and confirmation["dispatch_id"] in sent_dispatches:
        reasons.append("Dispatch was already sent; replay would duplicate the effect")
    return not reasons, reasons


if __name__ == "__main__":
    for label, choice in [
        ("matching recovery", Choice("10:10", "v1")),
        ("older database", Choice("10:00", "v1")),
        ("newer corrupted database", Choice("10:11", "v2")),
        ("current delete marker", Choice("10:10", "v3")),
        ("duplicate dispatch", Choice("10:10", "v1", True)),
    ]:
        accepted, reasons = assess(choice)
        print(f"{label}: {'ACCEPT' if accepted else 'HOLD'}")
        for reason in reasons:
            print("  -", reason)
