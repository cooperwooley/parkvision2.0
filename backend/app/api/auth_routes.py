# backend/app/api/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserLogin
from app.services.auth_service import hash_password, verify_password, add_user, authenticate_user
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register a new user
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    new_user = add_user(db, user.username, user.email, user.password)
    return new_user

# Login user
@router.post("/login", response_model=UserRead)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return user

# Get current user
@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Get all users
@router.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Update user
@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if updates.username is not None:
        existing = db.query(User).filter(
            User.username == updates.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = updates.username
    
    if updates.email is not None:
        existing = db.query(User).filter(
            User.email == updates.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = updates.email
    
    if updates.password is not None:
        user.password_hash = hash_password(updates.password)
    
    db.commit()
    db.refresh(user)
    return user


# Delete user
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return