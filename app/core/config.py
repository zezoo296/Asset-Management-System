import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
EXPIRING_SOON_DAYS = os.getenv("EXPIRING_SOON_DAYS")
RATE_LIMIT_REQUESTS = os.getenv("RATE_LIMIT_REQUESTS")
RATE_LIMIT_WINDOW = os.getenv("RATE_LIMIT_WINDOW")