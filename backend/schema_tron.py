from __future__ import annotations

from typing import List

from pydantic import BaseModel


class RetItem(BaseModel):
    contractRet: str
    fee: int


class Value(BaseModel):
    amount: int
    owner_address: str
    to_address: str


class Parameter(BaseModel):
    value: Value
    type_url: str


class ContractItem(BaseModel):
    parameter: Parameter
    type: str


class RawData(BaseModel):
    data: str = None
    contract: List[ContractItem]
    ref_block_bytes: str
    ref_block_hash: str
    expiration: int
    timestamp: int


class TronTransaction(BaseModel):
    ret: List[RetItem]
    signature: List[str]
    txID: str
    net_usage: int
    raw_data_hex: str
    net_fee: int
    energy_usage: int
    blockNumber: int
    block_timestamp: int
    energy_fee: int
    energy_usage_total: int
    raw_data: RawData
    internal_transactions: List


class Meta(BaseModel):
    at: int
    page_size: int


class TronTransactionsResponse(BaseModel):
    data: List[TronTransaction]
    success: bool
    meta: Meta
