from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.db.models.user_model import UserModel
from src.schemas.user_schema import UserCreate
from src.services.hash_service import HashService


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

hash_service = HashService(
    pwd_context=password_context
)


class UserService:

    # Find a user using their email address
    @staticmethod
    def get_user_by_email(email: str,db: Session) -> Optional[UserModel]:

        user_db_result = db.execute(select(UserModel).where(UserModel.email == email))

        return user_db_result.scalar_one_or_none()

    

    # Create new user
    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> UserModel:

        hashed_password = hash_service.hash_password(user_data.password)

        user_model = UserModel(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
        )

        db.add(user_model)
        db.commit()
        db.refresh(user_model)

        return user_model

    

    # Compare the signin password with the stored hash
    @staticmethod
    def verify_user_password(user_model: UserModel,password: str) -> bool:

        return hash_service.verify_hash_password(
            password=password,
            hash_password=user_model.password,
        )
