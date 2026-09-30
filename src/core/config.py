import os

from dotenv import load_dotenv

# Reading the .env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_SCHEMA_NAME = os.getenv("DEFAULT_SCHEMA_NAME")

JWT_SECRET = os.getenv("JWT_SECRET")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

JWT_EXPIRY_IN_MINUTES = int(os.getenv("JWT_EXPIRY_IN_MINUTES", "30"))

JWT_REFRESH_EXPIRY_IN_DAYS = int(os.getenv("JWT_REFRESH_EXPIRY_IN_DAYS", "7"))

COOKIE_SECURE = os.getenv(
    "COOKIE_SECURE",
    "false"
).lower() == "true"

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE",
    "lax"
)

if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL is missing from the .env file"
    )


PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER")
