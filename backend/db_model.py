from typing import Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative, declared_attr



@as_declarative()
class Base:
    id: Any
    __name__: str

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tlg_username = Column(String, nullable=True)
    ref_user = Column(Integer, ForeignKey("user.id"), nullable=True)
    is_adult = Column(Boolean, default=False)
    is_agreed = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)   # TODO If we really need it
    date_registered = Column(DateTime)
    level = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    levelup_hold = Column(Integer, nullable=False)
    temp_token = Column(String, nullable=True)      # Token to make changes (password, etc)
    invite_token = Column(String, nullable=True)   # Invitation token
    wrong_logins = Column(Integer, nullable=False)
    wrong_login_ts = Column(DateTime, nullable=False)
    tron_address = Column(String, nullable=True)    # Tron address
    #transaction = relationship("Transaction", back_populates="owner")


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    hash_string = Column(String, unique=True, nullable=False)
    ref_transaction = Column(Integer, ForeignKey("transaction.id"), nullable=True)
    operation = Column(String, nullable=False, index=True)
    result = Column(String, nullable=False)
    block_ts = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    owner_address = Column(String, nullable=False, index=True)
    to_address = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    #user_id =  Column(Integer,ForeignKey("user.id"))
    user_id = Column(Integer, index=True, nullable=True)
    #owner = relationship("User", back_populates="transaction")