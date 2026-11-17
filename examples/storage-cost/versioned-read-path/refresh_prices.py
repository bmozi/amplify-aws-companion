"""Verify selected public Ohio price meters without accessing an AWS account."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "public-prices.json"
URLS = {
    "s3": "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json",
    "transfer": "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json",
}
SELECTIONS = {
    "standard_storage": ("s3", "YPGKVRB2EKTVDJDT", "USE2-TimedStorage-ByteHrs", "GB-Mo"),
    "standard_put": ("s3", "GJKK9PMSTKPNGZS9", "USE2-Requests-Tier1", "Requests"),
    "standard_get": ("s3", "DJEKB32FV4HNZJZY", "USE2-Requests-Tier2", "Requests"),
    "internet_out": ("transfer", "36H7S3NU9B7S3UT5", "USE2-DataTransfer-Out-Bytes", "GB"),
}


def extract(offers):
    if offers["s3"].get("offerCode") != "AmazonS3" or offers["transfer"].get("offerCode") != "AWSDataTransfer":
        raise ValueError("unexpected AWS offer")
    rates = {}
    for name, (source, sku, usage, unit) in SELECTIONS.items():
        offer = offers[source]
        attrs = offer["products"].get(sku, {}).get("attributes", {})
        if attrs.get("usagetype") != usage:
            raise ValueError(f"{name}: SKU or usage type changed")
        if source == "s3" and attrs.get("regionCode") != "us-east-2":
            raise ValueError(f"{name}: wrong S3 Region")
        if source == "transfer" and (attrs.get("fromRegionCode") != "us-east-2"
                                      or attrs.get("toLocation") != "External"
                                      or attrs.get("transferType") != "AWS Outbound"):
            raise ValueError("internet_out: wrong transfer route")
        dimensions = [d for term in offer["terms"]["OnDemand"].get(sku, {}).values()
                      for d in term["priceDimensions"].values()
                      if d.get("beginRange") == "0" and d.get("unit") == unit]
        if len(dimensions) != 1 or not dimensions[0]["pricePerUnit"].get("USD"):
            raise ValueError(f"{name}: starting tier or unit changed")
        d = dimensions[0]
        rates[name] = {"source": source, "sku": sku, "usage_type": usage,
                       "unit": unit, "begin_range": "0", "end_range": d["endRange"],
                       "usd_per_unit": d["pricePerUnit"]["USD"]}
    return rates


def fetch():
    raw = {}
    for key, url in URLS.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            raw[key] = response.read()
    offers = {key: json.loads(value) for key, value in raw.items()}
    return {
        "schema_version": 1,
        "scope": "selected public Ohio on-demand meters; pre-credit gross example only",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {key: {"url": URLS[key], "sha256": sha256(value).hexdigest(),
                          "publication_date": offers[key]["publicationDate"],
                          "version": offers[key]["version"]} for key, value in raw.items()},
        "rates": extract(offers),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="replace snapshot after reviewing changed offers")
    args = parser.parse_args()
    current = fetch()
    if args.write:
        OUTPUT.write_text(json.dumps(current, indent=2) + "\n")
        print(f"Wrote {OUTPUT}; review assumptions before use")
        return
    saved = json.loads(OUTPUT.read_text())
    for key in ("schema_version", "scope", "sources", "rates"):
        if saved.get(key) != current.get(key):
            raise SystemExit(f"Public offer changed at {key}; inspect before updating snapshot")
    print("PASS: selected Ohio public offer hashes and rates match the saved snapshot")


if __name__ == "__main__":
    main()
