from datetime import datetime
from models import UsersModel, UserDevicesModel, TransactionsModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
import joblib

# Загружаем модель ML
model = joblib.load("fraud_model.pkl")

async def check_fraud(sender: UsersModel, sum: int, device_id: int, real_ip: str, session: AsyncSession) -> bool:
    """
    Проверка транзакции на фрод.
    Возвращает True, если транзакция подозрительная.
    """
    country = sender.country
    amount = float(sum)

    # Получаем устройство по device_id и user_id
    device_query = select(UserDevicesModel).where(
        UserDevicesModel.user_id == sender.id,
        UserDevicesModel.device_id == device_id
    )
    result = await session.execute(device_query)
    device = result.scalars().first()  # безопасно, даже если несколько записей

    # Проверка, была ли хотя бы одна транзакция с этого устройства
    tx_check = select(TransactionsModel.id).where(
        TransactionsModel.device_id == device_id
    )
    tx_result = await session.execute(tx_check)
    tx_exists = tx_result.scalars().first()  # безопасно

    device_new = 0 if tx_exists else 1

    # Проверка смены IP
    ip_changed = 0
    if device and getattr(device, "last_ip", None):
        ip_changed = 1 if device.last_ip != real_ip else 0
    elif device is None:
        # Если девайса нет, считаем как смену IP
        ip_changed = 1

    # Время транзакции
    hour = datetime.utcnow().hour

    # Формируем DataFrame для ML
    df = pd.DataFrame([{
        "amount": amount,
        "device_new": device_new,
        "ip_changed": ip_changed,
        "hour": hour,
        "country": country
    }])

    # One-hot кодирование страны
    df = pd.get_dummies(df, columns=["country"])
    for col in model.feature_names_in_:
        if col not in df.columns:
            df[col] = 0
    df = df[model.feature_names_in_]

    # Жёсткие правила (rule-based)
    if amount >= 150_000:
        return True
    if device_new == 1 and ip_changed == 1:
        return True
    if ip_changed == 1 and amount > 50_000:
        return True

    # ML-предсказание
    proba = model.predict_proba(df)[0][1]
    return proba > 0.6
