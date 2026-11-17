"""Offline status ledger and fan-out model. This is not a WebSocket server."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_id: str
    job_id: str
    sequence: int
    status: str


class StatusService:
    def __init__(self):
        self.grants = set()
        self.events = {}
        self.ids = {}
        self.connections = {}

    def grant(self, actor, job_id):
        self.grants.add((actor, job_id))

    def revoke(self, actor, job_id):
        self.grants.discard((actor, job_id))
        for connection_id, binding in list(self.connections.items()):
            if binding == (actor, job_id):
                del self.connections[connection_id]

    def subscribe(self, connection_id, actor, job_id, after_sequence=0):
        if (actor, job_id) not in self.grants:
            raise PermissionError("Current job grant required")
        if connection_id in self.connections or type(after_sequence) is not int or after_sequence < 0:
            raise ValueError("Connection ID or replay cursor invalid")
        history = self.events.get(job_id, [])
        if after_sequence > len(history):
            raise ValueError("Replay cursor is ahead of authoritative ledger")
        self.connections[connection_id] = (actor, job_id)
        return history[after_sequence:]

    def disconnect(self, connection_id):
        self.connections.pop(connection_id, None)

    def publish(self, principal, event_id, job_id, status):
        if principal != "trusted_worker":
            raise PermissionError("Only the fixture worker may publish")
        if not event_id or not job_id or not status:
            raise ValueError("Complete event identity, job and status required")
        payload = (job_id, status)
        if event_id in self.ids:
            if self.ids[event_id] != payload:
                raise ValueError("Conflicting replay of event ID")
            return self._deliveries(self._event_by_id(event_id)), False
        history = self.events.setdefault(job_id, [])
        event = Event(event_id, job_id, len(history) + 1, status)
        history.append(event)
        self.ids[event_id] = payload
        return self._deliveries(event), True

    def _event_by_id(self, event_id):
        job_id, _ = self.ids[event_id]
        return next(event for event in self.events[job_id] if event.event_id == event_id)

    def _deliveries(self, event):
        return [(connection_id, event) for connection_id, (actor, job_id) in self.connections.items()
                if job_id == event.job_id and (actor, job_id) in self.grants]


def main():
    service = StatusService()
    service.grant("alice", "repair-17")
    print("Alice subscribes:", service.subscribe("c1", "alice", "repair-17"))
    print("First publish:", service.publish("trusted_worker", "e1", "repair-17", "checking"))
    service.revoke("alice", "repair-17")
    print("After revoke:", service.publish("trusted_worker", "e2", "repair-17", "ready"))
    try:
        service.subscribe("c2", "alice", "repair-17", 1)
    except PermissionError:
        print("Reconnect denied without current grant")
    print("Local model only: no socket, AWS authorization, message delivery or cost observed")


if __name__ == "__main__":
    main()
