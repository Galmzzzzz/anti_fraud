from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, String, Boolean, ForeignKey, DateTime, func

class Base(DeclarativeBase):
    pass

class UsersModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    phone_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")

class UserDevicesModel(Base):
    __tablename__ = "user_devices"

    device_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device: Mapped[str] = mapped_column(String(65), nullable=False)
    user_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    screen_width: Mapped[int] = mapped_column(BigInteger)
    screen_height: Mapped[int] = mapped_column(BigInteger)



class TransactionsModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sum: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    is_fraud: Mapped[bool] = mapped_column(Boolean, default=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_devices.device_id", ondelete="SET NULL"))
    user_ip: Mapped[str] = mapped_column(String(45))

class FraudReportsModel(Base):
    __tablename__ = "fraud_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="open")
