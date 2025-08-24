from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, Student, Admin
from models import TokenData
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str, user_type: str):
    if user_type == "student":
        user = db.query(Student).filter(Student.username == username).first()
    elif user_type == "admin":
        user = db.query(Admin).filter(Admin.username == username).first()
    else:
        return False
    
    if not user or not verify_password(password, user.password_hash):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if username is None or user_type is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_type=user_type)
    except JWTError:
        raise credentials_exception
    
    if token_data.user_type == "student":
        user = db.query(Student).filter(Student.username == token_data.username).first()
    elif token_data.user_type == "admin":
        user = db.query(Admin).filter(Admin.username == token_data.username).first()
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user = Depends(get_current_user)):
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_student(current_user = Depends(get_current_user)):
    if not hasattr(current_user, 'assigned_bus_id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a student account"
        )
    return current_user