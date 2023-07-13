from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class TransactionRecord(BaseModel):
    hash_string : str
    ref_transaction : str = None
    operation : str
    result : str
    block_ts : datetime
    ts : datetime
    amount : int
    owner_address : str
    to_address : str
    user_email : str
    user_id : int #TODO set user id
    #owner : int   #TODO set owner user id

    class Config:
        orm_mode = True