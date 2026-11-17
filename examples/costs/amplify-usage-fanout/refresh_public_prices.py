"""Read public AWS Ohio offer files; never access an account or change a plan."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "public-prices-us-east-2.json"
BASE_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws"
# The SKU and tier are reviewed selections, not proof that the live backend uses them.
SELECTIONS = {
    "hosting_storage_gb_month": ("AWSAmplify", "9K3KMT4SNEZXVD7F", "0", "GigaBytes"),
    "hosting_transfer_gb": ("AWSAmplify", "U83YJUBMQZM9DJ9J", "0", "GigaBytes"),
    "amplify_waf_month_if_enabled": ("AWSAmplify", "R3ZW332F5SWHG4FM", "0", "Months"),
    "cognito_essentials_mau_before_free_tier": ("AmazonCognito", "NQKE2UA6GA2HDANG", "0", "CognitoUserPoolsMAU"),
    "appsync_graphql_operation": ("AWSAppSync", "B53XVVE928PX2Y76", "0", "Requests"),
    "appsync_realtime_message": ("AWSAppSync", "NVPN927XH8PD55J7", "0", "Messages"),
    "appsync_connection_minute": ("AWSAppSync", "PGKDMBCRWY5CHV76", "0", "Minutes"),
    "appsync_cache_hour_if_enabled": ("AWSAppSync", "BP5H5S6JS9QN4WVM", "0", "Hrs"),
    "dynamodb_on_demand_read_unit": ("AmazonDynamoDB", "SGMZJPDKSWXTY4VE", "0", "ReadRequestUnits"),
    "dynamodb_on_demand_write_unit": ("AmazonDynamoDB", "GGQSXTNTRBHRVS56", "0", "WriteRequestUnits"),
    "dynamodb_standard_storage_gb_month_beyond_free_tier": ("AmazonDynamoDB", "GAHPNMT39TQ47AGG", "25", "GB-Mo"),
    "s3_standard_storage_gb_month": ("AmazonS3", "YPGKVRB2EKTVDJDT", "0", "GB-Mo"),
    "s3_put_or_list_request": ("AmazonS3", "GJKK9PMSTKPNGZS9", "0", "Requests"),
    "s3_get_request": ("AmazonS3", "DJEKB32FV4HNZJZY", "0", "Requests"),
    "lambda_request": ("AWSLambda", "ZEA64MMVK5QRB5TC", "0", "Request"),
    "lambda_gb_second_tier_1": ("AWSLambda", "3BYZH4NKJN8TJUQ6", "0", "Lambda-GB-Second"),
    "cloudwatch_standard_log_ingest_gb": ("AmazonCloudWatch", "5T6Z6V26DSR7SZ49", "0", "GB"),
    "cloudwatch_standard_log_storage_gb_month": ("AmazonCloudWatch", "X7X4WD4A95NDR9U5", "0", "GB-Mo"),
}


def extract(offers):
    rates = {}
    for meter, (service, sku, begin, unit) in SELECTIONS.items():
        offer = offers[service]
        product = offer["products"].get(sku)
        if not product or product.get("sku") != sku:
            raise ValueError(f"Selected {meter} SKU disappeared")
        terms = list(offer["terms"]["OnDemand"].get(sku, {}).values())
        matches = [dimension for term in terms for dimension in term["priceDimensions"].values()
                   if dimension.get("beginRange") == begin and dimension.get("unit") == unit]
        if len(matches) != 1:
            raise ValueError(f"Selected {meter} tier or unit changed")
        price = matches[0]["pricePerUnit"].get("USD")
        if price is None:
            raise ValueError(f"Selected {meter} has no USD price")
        rates[meter] = {"service": service, "sku": sku,
                        "usage_type": product["attributes"].get("usagetype"),
                        "begin_range": begin, "unit": unit,
                        "usd_per_unit": price}
    return rates


def fetch_offers():
    offers, source = {}, {}
    for service in sorted({selection[0] for selection in SELECTIONS.values()}):
        url = f"{BASE_URL}/{service}/current/us-east-2/index.json"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        offer = json.loads(data)
        if offer.get("offerCode") != service:
            raise ValueError(f"Unexpected offer code for {service}")
        offers[service] = offer
        source[service] = {"url": url, "sha256": hashlib.sha256(data).hexdigest(),
                           "publication_date": offer["publicationDate"], "version": offer["version"]}
    return offers, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Fail if public offer bytes or selected rates changed")
    action.add_argument("--write", action="store_true", help="Write a new public-price teaching snapshot for review")
    args = parser.parse_args()
    offers, sources = fetch_offers()
    snapshot = {"schema_version": 1, "status": "public on-demand rates; selected meters only; not a whole-run estimate",
                "region": "us-east-2", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "offers": sources, "rates": extract(offers)}
    if args.check:
        existing = json.loads(OUTPUT.read_text())
        for key in ("schema_version", "status", "region", "offers", "rates"):
            if existing.get(key) != snapshot[key]:
                raise SystemExit(f"Public price snapshot changed at {key}; review before replacing it")
        print("PASS: public offer hashes and selected Ohio rates still match the committed snapshot")
    else:
        OUTPUT.write_text(json.dumps(snapshot, indent=2) + "\n")
        print(f"Wrote {OUTPUT}; review the selected rates and missing meters before use")


if __name__ == "__main__":
    main()
