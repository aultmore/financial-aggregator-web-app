from tronpy import Tron
from tronpy.providers import HTTPProvider
import json
import sys

# to import backend modules
sys.path.insert(0, "../backend")
from core.config import settings


provider = HTTPProvider(api_key=settings.TRONGRID_API_KEY)
client = Tron(provider, network=settings.TRON_NETWORK)

wallet = client.generate_address()

print(
"""
EvaToken Utility
Tron Network Address Generator
""")
print(json.dumps(wallet, indent=2))


