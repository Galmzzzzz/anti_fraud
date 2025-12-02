import subprocess
from datetime import datetime
import os

backup_file = f"C:\\all code\\fraud_system\\Anti_fraud_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

print("Создаём резервную копию базы данных...")

# Указываем пароль через переменную окружения для Windows
env = os.environ.copy()
env["PGPASSWORD"] = "gala"

cmd = [
    "pg_dump",
    "-U", "postgres",
    "-h", "localhost",
    "-p", "5432",
    "-f", backup_file,
    "Anti_fraud"
]

try:
    subprocess.run(cmd, check=True, env=env)
    print(f"Резервная копия успешно создана: {backup_file}")
except subprocess.CalledProcessError as e:
    print(f"Ошибка при создании резервной копии: {e}")
