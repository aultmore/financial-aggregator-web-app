from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TempToken(BaseModel):
    temp_token: str
