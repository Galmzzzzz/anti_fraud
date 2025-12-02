from pydantic import BaseModel

class Transaction(BaseModel):
    receiver: int
    sum: int


class Register(BaseModel):
    phone_number: int
    password: str

class Login(BaseModel):
    phone_number: int
    password: str
    device: str
    screen_width: int
    screen_height: int