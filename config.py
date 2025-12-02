from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_access_cookie_name: str = "access_token"
    jwt_cookie_csrf_protect: bool = False
    jwt_expires: int = 3600               # ← ДОБАВИТЬ
    jwt_cookie_expires: int = 3600  
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
