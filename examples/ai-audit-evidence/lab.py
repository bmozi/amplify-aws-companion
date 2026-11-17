"""Classify fictional, normalized AI audit evidence without calling AWS."""

import json
from pathlib import Path


FIXTURE = Path(__file__).with_name("fixture.json")


def assess(packet):
    """Report what each independent evidence route actually establishes."""
    account, region = packet["account"], packet["region"]
    case_id, request_id = packet["case_id"], packet["request_id"]

    def in_scope(record):
        return record.get("account") == account and record.get("region") == region

    api_calls = [event for event in packet["cloudtrail"]
                 if in_scope(event) and event.get("request_id") == request_id
                 and event.get("endpoint") == packet["endpoint"]
                 and event.get("eventType") == "AwsApiCall"]
    completions = [event for event in packet["cloudtrail"]
                   if in_scope(event) and event.get("parent_request_id") == request_id
                   and event.get("endpoint") == packet["endpoint"]
                   and event.get("eventType") == "AwsServiceEvent"]

    logging = packet["collection"]["invocation_logging"]
    content_supported = (logging["enabled"] and in_scope(logging)
                         and packet["endpoint"] == "bedrock-runtime")
    content = [record for record in packet["invocation_logs"]
               if in_scope(record) and record.get("request_id") == request_id
               and record.get("case_id") == case_id] if content_supported else []

    tracing = packet["collection"]["agent_tracing"]
    trace_supported = tracing["enabled"] and in_scope(tracing)
    traces = [record for record in packet["agent_traces"]
              if in_scope(record) and record.get("case_id") == case_id
              and record.get("steps")] if trace_supported else []
    receipts = [record for record in packet["business_receipts"]
                if in_scope(record) and record.get("case_id") == case_id]

    return {
        "case_id": case_id,
        "api_call_count": len(api_calls),
        "stream_completion_count": len(completions),
        "model_content": ("recorded" if content else
                          "not_expected_from_this_configuration" if not content_supported else
                          "unknown_missing_record"),
        "agent_steps": ("recorded" if traces else
                        "not_expected_from_this_configuration" if not trace_supported else
                        "unknown_missing_trace"),
        "business_outcome": receipts[0]["status"] if len(receipts) == 1 else "unknown",
        "sensitive_log_risk": any(record.get("input_contains_synthetic_marker", False)
                                  for record in content),
        "conclusion": ("four_routes_present_review_business_status" if
                       len(api_calls) == 1 and len(content) == 1 and len(traces) == 1
                       and len(receipts) == 1 else "incomplete_evidence_do_not_claim_success"),
    }


if __name__ == "__main__":
    print(json.dumps(assess(json.loads(FIXTURE.read_text())), indent=2))
