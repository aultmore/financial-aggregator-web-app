from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    symbol: str
    address: str
    decimals: int
    name: str


class Datum(BaseModel):
    transaction_id: str
    token_info: TokenInfo
    block_timestamp: int
    from_: str = Field(..., alias='from')
    to: str
    type: str
    value: int


class Meta(BaseModel):
    at: int
    page_size: int


class Trc20Response(BaseModel):
    data: List[Datum]
    success: bool
    meta: Meta

