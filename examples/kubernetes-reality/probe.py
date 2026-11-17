"""Call the Service DNS name from a Pod and print its customer response."""

import json
from urllib.request import urlopen


with urlopen("http://booking-api:8000/bookings/42", timeout=5) as response:
    print(json.dumps({"http_status": response.status, "body": json.load(response)}))
