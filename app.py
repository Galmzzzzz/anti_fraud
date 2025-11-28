from fastapi import FastAPI, Depends, HTTPException, Request, Response
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, ForeignKey, text, select
from datetime import datetime
from authx import AuthX, AuthXConfig
# import geocoder
import random
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from datetime import datetime


app = FastAPI()

config = AuthXConfig()
config.JWT_ACCESS_COOKIE_NAME = "my_acces_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_SECRET_KEY = "qwerqwer12341234"
config.JWT_COOKIE_CSRF_PROTECT = False
# вынести секретный ключ в .env 

security = AuthX(config=config)

DATABASE_URL = "postgresql+asyncpg://postgres:gala@localhost:5432/Anti_fraud"

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(bind=engine)


async def get_session():
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass

class UsersModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # BIGSERIAL
    phone_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")


class UserDevicesModel(Base):
    __tablename__ = "user_devices"

    device_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # BIGSERIAL
    device: Mapped[str] = mapped_column(String(65), nullable=False)
    user_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    screen_width: Mapped[int] = mapped_column(BigInteger)
    screen_height: Mapped[int] = mapped_column(BigInteger)

class TransactionsModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # BIGSERIAL
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sum: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    is_fraud: Mapped[bool] = mapped_column(Boolean, default=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_devices.device_id", ondelete="SET NULL"))
    user_ip: Mapped[str] = mapped_column(String(45))

class FraudReportsModel(Base):
    __tablename__ = "fraud_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # BIGSERIAL
    transaction_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="open")

class Register(BaseModel):
    phone_number: int
    password: str
    

class Login(BaseModel):
    
    phone_number: int
    password: str
    device: str
    screen_width: int
    screen_height: int

class Transaction(BaseModel):
    receiver: int
    sum: int


async def check_fraud(sender: UsersModel,sum: int, device_id: int, real_ip: str, session: AsyncSession) -> bool:
    
    country = sender.country
    amount = float(sum)

    # Проверяем устройство
    device_query = select(UserDevicesModel).where(
        UserDevicesModel.user_id == sender.id,
        UserDevicesModel.device_id == device_id
    )
    result = await session.execute(device_query)
    device = result.scalar_one_or_none()

    if device is None:
        device_new = 1
        ip_changed = 1  # если device не найден — считаем как новое устройство + смена IP
    else:
        device_new = 0
        # Сравниваем текущий IP с последним IP для этого девайса
        ip_changed = 1 if device.user_ip != real_ip else 0

    # Время транзакции
    hour = datetime.utcnow().hour

    # Формируем DataFrame для модели
    df = pd.DataFrame([{
        "amount": amount,
        "country": country,
        "device_new": device_new,
        "ip_changed": ip_changed,
        "hour": hour
    }])

    # one-hot для страны
    df = pd.get_dummies(df, columns=["country"])
    for col in model.feature_names_in_:
        if col not in df.columns:
            df[col] = 0
    df = df[model.feature_names_in_]

    proba = model.predict_proba(df)[0][1]
    return proba > 0.7


@app.post("/register")
async def register(credential: Register, request: Request, session: AsyncSession = Depends(get_session)):
    real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    # g = geocoder.ip(real_ip)
    # country = g.country
    countries = ["KZ", "RU", "US", "GB", "CN"]
    country = random.choice(countries)
    user = UsersModel(
        phone_number=credential.phone_number,
        balance=1000,
        password=credential.password,
        ip=real_ip,  
        country=country
    )

    session.add(user)
    await session.commit()
    return {"status" : "success",}


    
@app.post("/login")
async def login(
    credential: Login,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    
    query = select(UsersModel).where(UsersModel.phone_number == credential.phone_number)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="incorrect username or password")

    if credential.password != user.password:
        raise HTTPException(status_code=401, detail="incorrect username or password")


    
    token = security.create_access_token(uid=str(user.id))

    
    real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

    
    device_query = select(UserDevicesModel).where(
        UserDevicesModel.device == credential.device,
        UserDevicesModel.user_id == user.id
    )

    device_result = await session.execute(device_query)
    existing_device = device_result.scalar_one_or_none()

    
    if existing_device is None:
        new_device = UserDevicesModel(
            device=credential.device,
            user_ip=real_ip,
            user_id=user.id,
            screen_width=credential.screen_width,
            screen_height=credential.screen_height
        )
        session.add(new_device)
        await session.commit()
        await session.refresh(new_device) 
        device_id = new_device.device_id

    else:
        existing_device.user_ip = real_ip
        session.add(existing_device)
        session.commit()

        device_id = existing_device.device_id
    
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    response.set_cookie("device_id", device_id)
    # Add CSRF AND HTTPONLY 
    return {
        "access_token": token,
        "device_id" : device_id
        }


model = joblib.load("fraud_model.pkl")


@app.post("/transaction", dependencies=[Depends(security.access_token_required)])
async def transaction(
    data: Transaction, 
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    payload = security._decode_token(token)
    sender_id = int(payload.sub)

    
    device_id = request.cookies.get("device_id")
    if device_id is None:
        raise HTTPException(status_code=400, detail="device_id cookie missing")
    device_id = int(device_id)

    
    real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

    
    sender = await session.get(UsersModel, sender_id, with_for_update=True)
    query = select(UsersModel).where(UsersModel.phone_number == data.receiver)
    result = await session.execute(query)
    receiver = result.scalar_one_or_none()
    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")
    receiver_data = await session.get(UsersModel, receiver.id, with_for_update=True)

    
    is_fraud = await check_fraud(sender, data.sum, device_id, real_ip, session)

    if is_fraud:
        tx = TransactionsModel(
            sender_id=sender.id,
            receiver_id=receiver.id,
            sum=data.sum,
            status="blocked",
            is_fraud=True,
            device_id=device_id,
            user_ip=real_ip
        )
        session.add(tx)
        await session.flush()

        
        fraud_report = FraudReportsModel(
            transaction_id=tx.id,
            user_id=sender.id,
            reason="ML model flagged transaction as fraud",
            status="open"
        )
        session.add(fraud_report)
        await session.commit()

        return {"status": "blocked", "reason": "fraud_detected"}

    
    if sender.balance < data.sum:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    
    sender.balance -= data.sum
    receiver_data.balance += data.sum
    tx = TransactionsModel(
        sender_id=sender.id,
        receiver_id=receiver.id,
        sum=data.sum,
        status="success",
        is_fraud=False,
        device_id=device_id,
        user_ip=real_ip
    )
    session.add(tx)
    await session.commit()

    return {"status": "success"}



# uvicorn anti_fraud:app --reload
# venv\Scripts\Activate.ps1
