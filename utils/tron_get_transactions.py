from tronpy import Tron
from tronpy.providers import HTTPProvider
import json
import sys

# to import backend modules
sys.path.insert(0, "../backend")
from core.config import settings
import requests

# for SHASTA network
url = "https://api.shasta.trongrid.io/v1/accounts/"

# for NILE network
#url = "https://nile.trongrid.io/v1/accounts/"

url += sys.argv[1] + "/transactions/trc20"

headers = {
    "accept": "application/json",
    'TRON-PRO-API-KEY': settings.TRONGRID_API_KEY
}

response = requests.get(url, headers=headers)
res = json.loads(response.text)
print(json.dumps(res, indent=2))
