from typing import List
from typing import Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


class ChangePasswordRequestForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False


class ChangePasswordForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.password = form.get("password")

    async def is_valid(self):
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be > 8 chars")
        if not self.errors:
            return True
        return False
