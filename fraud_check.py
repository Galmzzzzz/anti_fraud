from datetime import datetime
from models import UsersModel, UserDevicesModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
import joblib

model = joblib.load("fraud_model.pkl")
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