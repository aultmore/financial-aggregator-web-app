from fastapi import APIRouter, Depends
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session

from core.config import settings, appRuntime
from schema_tron import TronTransactionsResponse, TronTransaction
from schema_tron_trc20 import Trc20Response
from schema_transactions import TransactionRecord
from db_session import get_db
from db_repo_transactions import create_new_transaction, process_income

from datetime import datetime
import requests
import json


router = APIRouter()


def tron_get_transactions_trc20(last_ts: int, db: Session):
    url = "https://api.trongrid.io/v1/accounts/"
    url += requests.utils.quote(settings.TRON_ADDRESS)
    url += "/transactions/trc20"
    url += "?only_confirmed=true"
    url += "&only_to=true"
    url += "&limit=200"
    if last_ts is not None:
        url += "&min_timestamp=" + str(last_ts)

    headers = {
        "accept": "application/json",
        "TRON-PRO-API-KEY": settings.TRONGRID_API_KEY
    }
    response = requests.get(url, headers=headers)
    #print(response.text)
    res = json.loads(response.text)
    records = Trc20Response(**res)

    for tr in records.data:
        if tr.block_timestamp > appRuntime.last_ts:
            appRuntime.last_ts = tr.block_timestamp

        if tr.token_info.symbol != "USDT":
            continue

        ts0 = datetime.fromtimestamp(tr.block_timestamp / 1000)

        #print("", tr.transaction_id, " at ",  ts0)

        ts = datetime.fromtimestamp(tr.block_timestamp / 1000)
        # user_data = ""
        # if tr.raw_data.data is not None:
        #     user_data = bytes.fromhex(tr.raw_data.data).decode("utf-8")
        #     user_data = user_data.strip()
        #print(f"    user_data=({user_data})")


        #print("       amount=", tr.value / 1000000, " of ", tr.token_info.symbol)
            
        tr_record = TransactionRecord(
                hash_string = tr.transaction_id,
                ref_transaction = None,
                operation = "RECV",     # TODO operation name
                result = "DONE",        # TODO name
                block_ts = ts0,
                ts = ts0,
                amount = tr.value,
                owner_address = tr.from_,
                to_address = "system",  # TODO system address
                user_email = "",
                user_id = 0
        )
        # insert transaction into DB
        record = create_new_transaction(record=tr_record, user_id=0, db=db)
        if record is not None:
            if record.result == "DONE":
                process_income(record=record, db=db)

    return 0


def tron_get_transactions(last_ts: int, db: Session):
    url = "https://api.shasta.trongrid.io/v1/accounts/"
    url += requests.utils.quote(settings.TRON_ADDRESS)
    url += "/transactions?only_confirmed=true&&only_to=true"
    url += "&limit=200"
    if last_ts > 0:
        url += "&min_timestamp=" + str(last_ts)

    headers = {
        "accept": "application/json",
        "TRON-PRO-API-KEY": settings.TRONGRID_API_KEY
    }
    response = requests.get(url, headers=headers)
    res = json.loads(response.text)
    records = TronTransactionsResponse(**res)

    for tr in records.data:
        if tr.block_timestamp > appRuntime.last_ts:
            appRuntime.last_ts = tr.block_timestamp

        ts = datetime.fromtimestamp(tr.raw_data.timestamp / 1000)
        user_data = ""
        if tr.raw_data.data is not None:
            user_data = bytes.fromhex(tr.raw_data.data).decode("utf-8")
            user_data = user_data.strip()

        #print("", tr.txID, " at ",  ts)
        #print(f"    user_data=({user_data})")

        # for every contract in the transaction
        for c in tr.raw_data.contract:

            #print("       amount=", c.parameter.value.amount / 1000000)
            
            tr_record = TransactionRecord(
                hash_string = tr.txID,
                ref_transaction = None,
                operation = "RECV",     # TODO operation name
                result = "DONE",        # TODO name
                block_ts = datetime.fromtimestamp(tr.block_timestamp / 1000),
                ts = datetime.fromtimestamp(tr.raw_data.timestamp / 1000),
                amount = c.parameter.value.amount,
                owner_address = c.parameter.value.owner_address,
                to_address = "system",  # TODO system address
                user_email = user_data,
                user_id = 0
            )
            # insert transaction into DB
            record = create_new_transaction(record=tr_record, user_id=0, db=db)
            if record is not None:
                if record.result == "DONE":
                    process_income(record=record, db=db)

    return 0



@router.on_event("startup")
@repeat_every(seconds=5)
def tron_worker() -> None:
    if settings.DBG_SKIP_TRANSACTIONS_POLLING is None:
        db = next(get_db())
        #tron_get_transactions_trc20(last_ts=appRuntime.last_ts, db=db)
        tron_get_transactions(last_ts=appRuntime.last_ts, db=db)
    


@router.on_event("shutdown")
async def router_stop():
    #print("Shutdown event")
    with open("last_ts.txt", mode="w") as file1:
        file1.write(str(appRuntime.last_ts))
        file1.close()
