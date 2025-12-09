from fastapi import FastAPI, Depends, HTTPException, Request, Response, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, load_only
from sqlalchemy import func, text, select
from fastapi.responses import JSONResponse
from authx import AuthX, AuthXConfig
from sqlalchemy.exc import SQLAlchemyError
from models import UsersModel, UserDevicesModel, UserRolesModel, TransactionsModel, FraudReportsModel
from schemas import Register, Login, Transaction
from fraud_check import check_fraud
from config import settings
from security import verify_password, hash_password
from fastapi.middleware.cors import CORSMiddleware
from authx.exceptions import JWTDecodeError
import random
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = AuthXConfig()
config.JWT_ACCESS_COOKIE_NAME = settings.jwt_access_cookie_name
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_SECRET_KEY = settings.jwt_secret_key
config.JWT_COOKIE_CSRF_PROTECT = settings.jwt_cookie_csrf_protect

security = AuthX(config=config)

DATABASE_URL = "postgresql+asyncpg://gala:gala@pg:5432/anti_fraud"
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine)

async def get_session():
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

@app.post("/register")
async def register(credential: Register, request: Request, session: AsyncSession = Depends(get_session)):
    real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    countries = ["KZ", "RU", "US", "GB", "CN"]
    country = random.choice(countries)
    hashed_password = hash_password(credential.password)
    user = UsersModel(
        phone_number=credential.phone_number,
        balance=1000,
        password=hashed_password,
        ip=real_ip,
        country=country
    )
    session.add(user)
    await session.flush()
    role = UserRolesModel(user_id=user.id, is_admin=False)
    session.add(role)
    await session.commit()
    return {"status": "success"}

@app.post("/login")
async def login(credential: Login, response: Response, request: Request, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        query = select(UsersModel).options(load_only(UsersModel.password, UsersModel.id)).where(
            UsersModel.phone_number == credential.phone_number
        )
        result = await session.execute(query)
        user = result.scalars().first()  # <-- безопасно, даже если дубликаты

        if not user or not verify_password(user.password, credential.password):
            raise HTTPException(status_code=401, detail="incorrect username or password")

        token = security.create_access_token(uid=str(user.id))
        real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

        device_query = select(UserDevicesModel).where(
            UserDevicesModel.device == credential.device,
            UserDevicesModel.user_id == user.id
        )
        device_result = await session.execute(device_query)
        existing_device = device_result.scalars().first()  # <-- исправлено

        if not existing_device:
            new_device = UserDevicesModel(
                device=credential.device[:255],  # <-- обрезаем, чтобы не было ошибки StringDataRightTruncation
                user_ip=real_ip,
                user_id=user.id,
                screen_width=credential.screen_width,
                screen_height=credential.screen_height
            )
            session.add(new_device)
            await session.flush()
            await session.refresh(new_device)
            device_id = new_device.device_id
        else:
            existing_device.user_ip = real_ip
            existing_device.screen_width = credential.screen_width
            existing_device.screen_height = credential.screen_height
            session.add(existing_device)
            await session.flush()
            device_id = existing_device.device_id

    response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=3600,
    )
    response.set_cookie(
        "device_id",
        str(device_id),
        httponly=True,
        secure=False,
        max_age=60*60*24*365
    )

    return {"access_token": token, "device_id": device_id}

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(key="device_id")
    return {"status": "success", "message": "Logged out successfully"}

@app.post("/transaction", dependencies=[Depends(security.access_token_required)])
async def transaction(data: Transaction, request: Request, session: AsyncSession = Depends(get_session)):
    response = JSONResponse(content={})
    token = request.cookies.get(settings.jwt_access_cookie_name)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Token missing"})
    try:
        payload = security._decode_token(token)
        sender_id = int(payload.sub)
    except JWTDecodeError:
        response = JSONResponse(status_code=401, content={"detail": "Token expired or invalid"})
        response.delete_cookie(key=settings.jwt_access_cookie_name)
        response.delete_cookie(key="device_id")
        return response

    device_id = request.cookies.get("device_id")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id cookie missing")
    device_id = int(device_id)

    real_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    sender = await session.get(UsersModel, sender_id, with_for_update=True)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    query = select(UsersModel).where(UsersModel.phone_number == data.receiver)
    result = await session.execute(query)
    receiver = result.scalars().first()  # <-- исправлено

    if not receiver:
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

@app.get("/me", dependencies=[Depends(security.access_token_required)])
async def get_me(request: Request, session: AsyncSession = Depends(get_session)):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    payload = security._decode_token(token)
    user_id = int(payload.sub)
    user = await session.get(UsersModel, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    devices_query = select(UserDevicesModel).where(UserDevicesModel.user_id == user_id)
    result = await session.execute(devices_query)
    devices = result.scalars().all()
    role_query = select(UserRolesModel).where(UserRolesModel.user_id == user_id)
    role_result = await session.execute(role_query)
    role = role_result.scalar_one_or_none()
    is_admin = role.is_admin if role else False

    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "balance": user.balance,
        "country": user.country,
        "ip": user.ip,
        "is_admin": is_admin,
        "devices": [
            {"device_id": d.device_id, "device": d.device, "user_ip": d.user_ip,
             "screen_width": d.screen_width, "screen_height": d.screen_height} for d in devices
        ],
    }

@app.get("/get_transactions", dependencies=[Depends(security.access_token_required)])
async def get_transactions(request: Request, session: AsyncSession = Depends(get_session),
                           limit: int = Query(50, gt=0, le=100), offset: int = Query(0, ge=0)):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    payload = security._decode_token(token)
    user_id = int(payload.sub)
    query = select(TransactionsModel).where(
        (TransactionsModel.sender_id == user_id) | (TransactionsModel.receiver_id == user_id)
    ).order_by(TransactionsModel.id.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    txs = result.scalars().all()
    return [{"id": tx.id, "sender_id": tx.sender_id, "receiver_id": tx.receiver_id, "sum": tx.sum,
             "status": tx.status, "is_fraud": tx.is_fraud, "device_id": tx.device_id,
             "user_ip": tx.user_ip, "direction": "sent" if tx.sender_id == user_id else "received"} for tx in txs]


async def is_admin(user_id: int, session: AsyncSession):
    query = select(UserRolesModel).where(UserRolesModel.user_id == user_id)
    result = await session.execute(query)
    role = result.scalar_one_or_none()
    if not role or not role.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


@app.get("/total_sent", dependencies=[Depends(security.access_token_required)])
async def total_sent(request: Request, session: AsyncSession = Depends(get_session)):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    payload = security._decode_token(token)
    user_id = int(payload.sub)
    await is_admin(user_id, session)
    query = select(UsersModel.phone_number, func.sum(TransactionsModel.sum).label("total_sent")) \
        .join(TransactionsModel, TransactionsModel.sender_id == UsersModel.id) \
        .group_by(UsersModel.id)
    result = await session.execute(query)
    rows = result.all()
    return [{"phone_number": phone, "total_sent": total or 0} for phone, total in rows]


@app.delete("/fraud_reports", dependencies=[Depends(security.access_token_required)])
async def delete_fraud_reports(request: Request, session: AsyncSession = Depends(get_session)):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    payload = security._decode_token(token)
    user_id = int(payload.sub)
    await is_admin(user_id, session)
    try:
        await session.execute(text("DELETE FROM fraud_reports"))
        await session.commit()
        return {"status": "success", "message": "All fraud reports deleted."}
    except SQLAlchemyError as e:
        await session.rollback()
        return {"status": "error", "message": f"Failed to delete fraud reports: {str(e)}"}
