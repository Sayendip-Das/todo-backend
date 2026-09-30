from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import JWTError, jwt
from src.core.config import JWT_ALGORITHM, JWT_EXPIRY_IN_MINUTES, JWT_REFRESH_EXPIRY_IN_DAYS, JWT_SECRET

class JWTService:

    def create_access_token(self, email: str) -> str:

        data = {"email": email, "token_type": "access"}

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JWT_EXPIRY_IN_MINUTES
        )

        data.update({"exp": expire})

        return jwt.encode(
            data,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    def create_refresh_token(self, email: str) -> str:

        data = {"email": email, "token_type": "refresh"}

        expire = datetime.now(timezone.utc) + timedelta(
            days=JWT_REFRESH_EXPIRY_IN_DAYS
        )

        data.update({"exp": expire})

        return jwt.encode(
            data,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    def decode(self, token: str) -> Optional[dict[str, Any]]:

        try:
            return jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )

        except JWTError:
            return None
