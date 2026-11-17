"""Read selected public AWS Ohio S3 offer meters; never access an account."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "public-prices.json"
URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json"

# Reviewed selections for a direct-upload, no-read, delete-at-end workload.
# The offer has separate small-object and early-delete usage types for Standard-IA.
SELECTIONS = {
    "standard_storage": ("YPGKVRB2EKTVDJDT", "USE2-TimedStorage-ByteHrs", "GB-Mo"),
    "ia_storage": ("FNWV6QQJ34ZTYY9U", "USE2-TimedStorage-SIA-ByteHrs", "GB-Mo"),
    "ia_small_floor": ("V2ARAHA4T9964FN5", "USE2-TimedStorage-SIA-SmObjects", "GB-Mo"),
    "standard_put": ("GJKK9PMSTKPNGZS9", "USE2-Requests-Tier1", "Requests"),
    "ia_put": ("VHQYNB4HK92W7HCD", "USE2-Requests-SIA-Tier1", "Requests"),
    "ia_early_storage": ("TYYBB3K5HTXZS3CW", "USE2-EarlyDelete-SIA", "GB-Mo"),
    "ia_early_small_floor": ("CZM8DDXKKEQKFKSG", "USE2-EarlyDelete-SIA-SmObjects", "GB-Mo"),
}


def extract(offer):
    if offer.get("offerCode") != "AmazonS3":
        raise ValueError("not the AmazonS3 offer")
    rates = {}
    for meter, (sku, usage, unit) in SELECTIONS.items():
        product = offer["products"].get(sku)
        if not product or product.get("attributes", {}).get("usagetype") != usage:
            raise ValueError(f"selected {meter} SKU or usage type changed")
        if product["attributes"].get("regionCode") != "us-east-2":
            raise ValueError(f"selected {meter} is not Ohio")
        dimensions = [d for term in offer["terms"]["OnDemand"].get(sku, {}).values()
                      for d in term["priceDimensions"].values()
                      if d.get("beginRange") == "0" and d.get("unit") == unit]
        if len(dimensions) != 1 or not dimensions[0]["pricePerUnit"].get("USD"):
            raise ValueError(f"selected {meter} starting tier or unit changed")
        rates[meter] = {"sku": sku, "usage_type": usage, "unit": unit,
                        "begin_range": "0", "usd_per_unit": dimensions[0]["pricePerUnit"]["USD"]}
    return rates


def fetch():
    with urllib.request.urlopen(URL, timeout=30) as response:
        raw = response.read()
    offer = json.loads(raw)
    return {"schema_version": 1, "scope": "selected public Ohio S3 on-demand meters; pre-credit gross estimate only",
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": {"url": URL, "sha256": sha256(raw).hexdigest(),
                       "publication_date": offer["publicationDate"], "version": offer["version"]},
            "rates": extract(offer)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="replace snapshot after reviewing changed offer")
    args = parser.parse_args()
    current = fetch()
    if args.write:
        OUTPUT.write_text(json.dumps(current, indent=2) + "\n")
        print(f"Wrote {OUTPUT}; review scenario assumptions before use")
        return
    saved = json.loads(OUTPUT.read_text())
    for key in ("schema_version", "scope", "source", "rates"):
        if saved.get(key) != current.get(key):
            raise SystemExit(f"Public offer changed at {key}; inspect before updating snapshot")
    print("PASS: public Ohio offer hash and selected rates match committed snapshot")


if __name__ == "__main__":
    main()
