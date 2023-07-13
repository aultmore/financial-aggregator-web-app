from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    tlg_username : str
    is_adult : bool = False
    is_agreed : bool = False
    is_confirmed : bool = False
    is_superuser : bool = False
    ref_user : Optional[int] = None
    level : int = 0


class ShowUser(BaseModel):
    id : int
    email : EmailStr
    date_registered : datetime
    tlg_username : str
    is_adult : bool
    is_agreed : bool
    is_confirmed : bool
    level : int
    balance : int
    levelup_hold : int
    ref_user : int
    user_network : List['ShowUser'] = None

    class Config():
        orm_mode = True
