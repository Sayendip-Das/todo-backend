from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.schemas.user_schema import JWTOut, User, UserBaseOut, UserCreate, UserCreateOut, UserSignIn
from src.db.models.user_model import UserModel
from src.api.routes.todo_routes import get_current_user
from src.services.jwt_service import JWTService
from src.services.user_service import UserService
from src.core.config import COOKIE_SAMESITE, COOKIE_SECURE, JWT_REFRESH_EXPIRY_IN_DAYS

router = APIRouter(prefix="/users", tags=["Users"])

#Sign Up User
@router.post("/signup", response_model=UserCreateOut)
def signup_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserCreateOut:

    existing_user = UserService.get_user_by_email(email=user_data.email, db=db)

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="User already exists with this email"
        )

    user_model = UserService.create_user(user_data=user_data, db=db)

    user = User.model_validate(user_model)

    return UserCreateOut(
        user=user,
        message="User created successfully"
    )

# ======================================================================================

# Generate a new access token using refresh-token cookie
@router.post("/refresh", response_model=JWTOut)
def refresh_token(request : Request, response : Response, db: Session = Depends(get_db)) -> JWTOut:

    current_refresh_token = request.cookies.get("refresh_token")

    if current_refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found"
        )

    payload = JWTService().decode(token=current_refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Email not found in token"
        )

    user_model = UserService.get_user_by_email(email=email, db=db)

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_model.refresh_token != current_refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is not valid"
        )

    access_token = JWTService().create_access_token(email=user_model.email)
    new_refresh_token = JWTService().create_refresh_token(email=user_model.email)

    user_model.refresh_token = new_refresh_token

    db.commit()
    
    db.refresh(user_model)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=JWT_REFRESH_EXPIRY_IN_DAYS * 24 * 60 * 60,
        path="/api/v1/users"
    )

    return JWTOut(
        access_token=access_token,
        message="Token refreshed successfully"
    )


# Sign In User
@router.post("/signin", response_model=JWTOut)
def signin_user(user_data: UserSignIn, response: Response ,db: Session = Depends(get_db)) -> JWTOut:

    user_model = UserService.get_user_by_email(email=user_data.email, db=db)

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    password_is_valid = UserService.verify_user_password(
        user_model=user_model,
        password=user_data.password
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = JWTService().create_access_token(email=user_model.email)
    refresh_token = JWTService().create_refresh_token(email=user_model.email)

    user_model.refresh_token = refresh_token

    db.commit()

    db.refresh(user_model)

    # Save refresh token in the browser's HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=JWT_REFRESH_EXPIRY_IN_DAYS * 24 * 60 * 60,
        path="/api/v1/users"
    )

    return JWTOut(
        access_token=access_token,
        message="User signed in successfully"
    )


# Log Out User
@router.post("/logout", response_model=UserBaseOut)
def logout_user(request : Request, response : Response, db: Session = Depends(get_db)) -> UserBaseOut:

    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found"
        )

    payload = JWTService().decode(token=refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Email not found in token"
        )

    user_model = UserService.get_user_by_email(email=email, db=db)

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_model.refresh_token != refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is not valid"
        )

    user_model.refresh_token = None

    db.commit()

    db.refresh(user_model)

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/users",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite=COOKIE_SAMESITE
    )

    return UserBaseOut(
        message="User logged out successfully"
    )


# Get currently signed-in user
@router.get("/me", response_model=User)
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)) -> User:

    user = User.model_validate(current_user)

    return user