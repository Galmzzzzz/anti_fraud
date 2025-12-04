from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32
)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash: str, password: str) -> bool:
    try:
        return ph.verify(hash, password)
    except VerifyMismatchError:
        return False
