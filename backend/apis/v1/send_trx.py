from tronpy import Tron
from tronpy.keys import PrivateKey
from core.config import settings

client = Tron(network='shasta')

def send_trx(to_address:str, amount:float):
  priv_key = PrivateKey(bytes.fromhex(settings.TRON_ADDRESS_PRIV))
  total = int(amount) * 1_000_000
  txn = (
    client.trx.transfer(settings.TRON_ADDRESS, to_address, total)
    .memo("")
    .fee_limit(0)
    .build()
    .inspect()
    .sign(priv_key)
    .broadcast()
  )
  
  if txn['result'] == True:
    return True
  else:
    return False