from typing import List
from typing import Optional

from fastapi import Request


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.ref = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.tlg_username: Optional[str] = None
        self.isAdult = None
        self.isAgreed = None

    async def load_data(self):
        form = await self.request.form()
        self.ref = form.get("ref")
        self.email = form.get("email")
        self.password = form.get("password")
        self.tlg_username = form.get("tlg_username")
        self.isAdult = form.get("isAdult")
        self.isAgreed = form.get("isAgreed")

    async def is_valid(self):
        if not self.ref:
            self.errors.append("Invitation reference is required")
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Требуется ввести корректный email адрес")
        if not self.password or not len(self.password) >= 8:
            self.errors.append("Пароль недостаточно надежный")
        if not self.isAdult or not self.isAdult == "1":
            self.errors.append("Требуется возраст 18+")
        if not self.isAgreed or not self.isAgreed == "1":
            self.errors.append("Требуется согласие с условиями")
        if not self.errors:
            return True
        return False


class WithdrawRequestForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.amount: int = 0
        self.to_address: str = None

    async def load_data(self):
        form = await self.request.form()
        self.amount = int(form.get("amount"))
        self.to_address = form.get("to_address")

    async def is_valid(self):
        if not self.to_address:
            self.errors.append("Требуется указать адрес кошелька для перевода")
        else:
            if self.to_address[0] != 'T':
                self.errors.append("Проверьте правильность адреса - должен быть адрес TRC20")
        if int(self.amount) < 100:
            self.errors.append("Минимальная сумма перевода - 100 токенов")
        if not self.errors:
            return True
        return False


class TransactionConfirmForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.txid: str = None

    async def load_data(self):
        form = await self.request.form()
        self.txid = form.get("txid")

    async def is_valid(self):
        if not self.txid:
            self.errors.append("Требуется указать ID подтвержденной транзакции")
        if not self.errors:
            return True
        return False
