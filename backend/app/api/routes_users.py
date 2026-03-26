from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from backend.app.db.session import get_db
from backend.app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    class Config:
        orm_mode = True


class UserPreferences(BaseModel):
    target_roles: list[str] = []
    locations: list[str] = []
    salary_min: int | None = None
    salary_max: int | None = None
    job_types: list[str] = []
    aggressiveness: int = 50


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return TokenResponse(access_token=create_access_token(user.email))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/preferences", response_model=UserPreferences)
def get_my_preferences(current_user: User = Depends(get_current_user)) -> UserPreferences:
    if not current_user.preferences:
        return UserPreferences()
    return UserPreferences(**current_user.preferences)


@router.put("/me/preferences", response_model=UserPreferences)
def update_my_preferences(
    payload: UserPreferences,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPreferences:
    current_user.preferences = payload.dict()
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserPreferences(**(current_user.preferences or {}))


@router.post("/me/resume")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    current_user.resume_path = f"uploads/{current_user.id}/{file.filename}"
    db.add(current_user)
    db.commit()
    return {"message": "Resume metadata saved", "resume_path": current_user.resume_path}

