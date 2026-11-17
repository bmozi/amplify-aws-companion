"""Loopback customer journey over the existing A02 Moto domain. No AWS calls."""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import boto3
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "architectures/reliable-workflows/src"))
from domain import Lab, identifier  # noqa: E402


ACTORS = {"alice-local-token": "alice", "bob-local-token": "bob"}


def accepted_epoch(item):
    value = item.get("accepted_at")
    return int(value) if value is not None else None


def handler_for(lab):
    class JourneyHandler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, payload):
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def actor(self):
            token = self.headers.get("Authorization", "").removeprefix("Bearer ")
            return ACTORS.get(token)

        def do_POST(self):
            actor = self.actor()
            if not actor:
                return self.reply(401, {"error": "unknown local actor"})
            if self.path != "/requests":
                return self.reply(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 2048:
                    return self.reply(413, {"error": "invalid request length"})
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict) or set(body) != {"request_id", "text"}:
                    raise ValueError("expected request_id and text")
                identifier(body["request_id"])
                existing = lab.get(f"request#{actor}#{body['request_id']}")
                try:
                    item = lab.submit(actor, body["request_id"], body["text"])
                except ValueError as error:
                    if str(error) == "Request ID already used with different content":
                        return self.reply(409, {"error": "request ID already used for different work"})
                    raise
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                return self.reply(400, {"error": "invalid request"})
            return self.reply(200 if existing else 202, {
                "request_id": body["request_id"],
                "state": "appointment_recorded" if item["status"] == "DONE" else "received_processing",
                "accepted_at_epoch": accepted_epoch(item),
                "receipt_reused": bool(existing),
                "status_path": f"/requests/{body['request_id']}",
            })

        def do_GET(self):
            actor = self.actor()
            if not actor:
                return self.reply(401, {"error": "unknown local actor"})
            prefix = "/requests/"
            if not self.path.startswith(prefix):
                return self.reply(404, {"error": "not found"})
            request_id = self.path[len(prefix):]
            try:
                identifier(request_id)
            except ValueError:
                return self.reply(404, {"error": "not found"})
            item = lab.get(f"request#{actor}#{request_id}")
            if not item or item.get("kind") != "request":
                return self.reply(404, {"error": "not found"})
            return self.reply(200, {
                "request_id": request_id,
                "state": "appointment_recorded" if item["status"] == "DONE" else "received_processing",
                "accepted_at_epoch": accepted_epoch(item),
            })

    return JourneyHandler


def call(base, method, path, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(base + path, data=data, method=method,
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def run():
    with mock_aws():
        db = boto3.resource("dynamodb", region_name="us-east-2").meta.client
        db.create_table(TableName="journey", KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                        BillingMode="PAY_PER_REQUEST")
        sqs = boto3.client("sqs", region_name="us-east-2")
        queue = sqs.create_queue(QueueName="journey")["QueueUrl"]
        lab = Lab(db, "journey", sqs, queue)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(lab))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            observations = {}
            observations["accepted"] = call(base, "POST", "/requests", "alice-local-token",
                                            {"request_id": "r1", "text": "heater will not start"})
            observations["other_actor_denied"] = call(base, "GET", "/requests/r1", "bob-local-token")
            observations["anonymous_denied"] = call(base, "GET", "/requests/r1", "bad-token")
            observations["same_retry"] = call(base, "POST", "/requests", "alice-local-token",
                                              {"request_id": "r1", "text": "heater will not start"})
            observations["changed_retry"] = call(base, "POST", "/requests", "alice-local-token",
                                                 {"request_id": "r1", "text": "different repair"})
            request_key = "request#alice#r1"
            try:
                lab.dispatch(fail_after_send=True)
            except RuntimeError as error:
                assert str(error) == "Teaching failure after send, before outbox acknowledgement"
            observations["pending_after_dispatch_gap"] = lab.get("outbox#" + request_key)["sent"] is False
            observations["dispatch_recovery"] = lab.dispatch()
            messages = sqs.receive_message(QueueUrl=queue, MaxNumberOfMessages=10,
                                           WaitTimeSeconds=0).get("Messages", [])
            observations["transport_messages"] = len(messages)
            records = [{"messageId": message["MessageId"], "body": message["Body"]}
                       for message in messages]
            db.put_item(TableName="journey", Item={"pk": "control#scheduler", "unavailable": True})
            observations["outage_batch"] = lab.batch(records)
            observations["during_outage"] = call(base, "GET", "/requests/r1", "alice-local-token")
            accepted_at = observations["accepted"][1]["accepted_at_epoch"]
            observations["at_contact_deadline"] = lab.check_contact_due(accepted_at + 3600)
            observations["new_overdue_work"] = lab.check_contact_due(accepted_at + 3601)
            observations["repeat_due_check"] = lab.check_contact_due(accepted_at + 3602)
            observations["open_after_lost_check_reply"] = lab.read_open_contacts()
            observations["fixture_contact_record"] = lab.record_first_contact(
                "alice", "r1", accepted_at + 4 * 3600)
            observations["open_after_contact_record"] = lab.read_open_contacts()
            db.delete_item(TableName="journey", Key={"pk": "control#scheduler"})
            observations["recovery_batch"] = lab.batch(records)
            observations["completed"] = call(base, "GET", "/requests/r1", "alice-local-token")
            observations["appointment_count"] = sum(
                item.get("kind") == "appointment" for item in db.scan(TableName="journey")["Items"])
            assert observations["accepted"][0] == 202
            assert observations["accepted"][1]["state"] == "received_processing"
            assert observations["other_actor_denied"][0] == 404
            assert observations["anonymous_denied"][0] == 401
            assert observations["same_retry"][0] == 200
            assert observations["same_retry"][1]["receipt_reused"] is True
            assert observations["accepted"][1]["accepted_at_epoch"] == observations["same_retry"][1]["accepted_at_epoch"]
            assert observations["accepted"][1]["accepted_at_epoch"] == observations["during_outage"][1]["accepted_at_epoch"]
            assert observations["changed_retry"][0] == 409
            assert observations["pending_after_dispatch_gap"] is True
            assert observations["transport_messages"] == 2
            assert len(observations["outage_batch"]["batchItemFailures"]) == 2
            assert observations["during_outage"][1]["state"] == "received_processing"
            assert observations["at_contact_deadline"]["newly_opened"] == []
            assert len(observations["new_overdue_work"]["newly_opened"]) == 1
            assert observations["repeat_due_check"]["newly_opened"] == []
            assert len(observations["open_after_lost_check_reply"]["items"]) == 1
            assert observations["fixture_contact_record"]["met_one_hour_promise"] is False
            assert observations["open_after_contact_record"]["items"] == []
            assert observations["recovery_batch"]["batchItemFailures"] == []
            assert observations["completed"][1]["state"] == "appointment_recorded"
            assert observations["appointment_count"] == 1
            print(json.dumps(observations, indent=2, sort_keys=True))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def main():
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
