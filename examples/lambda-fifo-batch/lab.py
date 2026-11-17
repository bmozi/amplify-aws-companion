"""Local FIFO batch-response exercise. No AWS client or network calls."""


def handle(event, process):
    """Stop at the first failure; report that record and the unprocessed tail."""
    records = event["Records"]
    for index, record in enumerate(records):
        try:
            process(record)
        except ValueError:
            return {"batchItemFailures": [
                {"itemIdentifier": item["messageId"]} for item in records[index:]
            ]}
    return {"batchItemFailures": []}


def demo():
    records = [{"messageId": name} for name in ("A", "B", "C")]
    processed = []

    def process(record):
        if record["messageId"] == "B":
            raise ValueError("fictional dependency failure")
        processed.append(record["messageId"])

    response = handle({"Records": records}, process)
    print("Completed:", processed)
    print("Returned for retry:", response)


if __name__ == "__main__":
    demo()
