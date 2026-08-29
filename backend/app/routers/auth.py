from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserSignup, UserLogin, Token
from app.security.pwd import get_password_hash, verify_password
from app.security.jwt import create_access_token, create_refresh_token, oauth2_scheme
from jose import jwt, JWTError
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=Token)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    role_str = new_user.role.value if hasattr(new_user.role, "value") else str(new_user.role)
    token_data = {"sub": str(new_user.id), "role": role_str, "email": new_user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=role_str,
        name=new_user.name
    )

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token_data = {"sub": str(user.id), "role": role_str, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=role_str,
        name=user.name
    )

@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_data = {"sub": user.id, "role": user.role.value, "email": user.email}
    new_access_token = create_access_token(token_data)
    return {"access_token": new_access_token, "token_type": "bearer"}
