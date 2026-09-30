from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr



# Data accepted when creating an account
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# Data accepted when sign in
class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# Common response
class UserBaseOut(BaseModel):
    message: str
    error: Optional[str] = None


# Signup response
class UserCreateOut(UserBaseOut):
    user: User


# Signin response
class JWTOut(UserBaseOut):
    access_token: str
    token_type: str = "bearer"
