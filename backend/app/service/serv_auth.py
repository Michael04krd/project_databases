from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from ..database import Base, intpk, str_200, get_db
from ..models.user  import User, UserRole
from ..models.med_work import MedicalWorkerInfo

SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secure-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 6

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/auth/login/donor")
#
# class AuthService:
#     def __init__(self, db: AsyncSession):
#         self.db = db
#     @staticmethod
#     def verify_password(plain_password: str, hashed_password: str) -> bool:
#         return pwd_context.verify(plain_password, hashed_password)
#
#     @staticmethod
#     def get_password_hash(password: str) -> str:
#         return pwd_context.hash(password)
#
#     @classmethod
#     async def register_donor(
#             cls,
#             db: AsyncSession,
#             email: str,
#             password: str,
#             surname: str,
#             name: str,
#             namedad: Optional[str] = None
#     ) -> User:
#         existing_user = await db.execute(select(User).where(User.email == email))
#         if existing_user.scalar_one_or_none():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )
#
#         user = User(
#             email=email,
#             hash_password=cls.get_password_hash(password),
#             surname=surname,
#             name=name,
#             namedad=namedad,
#             role=UserRole.DONOR
#         )
#         db.add(user)
#         await db.commit()
#         await db.refresh(user)
#         return user
#
#     @classmethod
#     async def login(
#             cls,
#             db: AsyncSession,
#             email: str,
#             password: str
#     ) -> dict:
#         user = await db.execute(select(User).where(User.email == email))
#         user = user.scalar_one_or_none()
#
#         if not user or not cls.verify_password(password, user.hash_password):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect email or password"
#             )
#
#         access_token = cls.create_token(
#             data={"sub": user.email, "user_id": user.id, "role": user.role.value},
#             expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         )
#
#         refresh_token = cls.create_token(
#             data={"sub": user.email, "user_id": user.id, "role": user.role.value},
#             expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#         )
#
#         return {
#             "access_token": access_token,
#             "refresh_token": refresh_token,
#             "token_type": "bearer"
#         }
#
#     @staticmethod
#     def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#         to_encode = data.copy()
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(minutes=15)
#         to_encode.update({"exp": expire})
#         return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
#     @classmethod
#     async def get_user_by_email(cls, db: AsyncSession, email: str) -> Optional[User]:
#         result = await db.execute(select(User).where(User.email == email))
#         return result.scalar_one_or_none()
#
#
#     @staticmethod
#     async def get_current_user(
#             db: AsyncSession,
#             token: str
#     ) -> User:
#         credentials_exception = HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             user_id: int = int(payload.get("user_id"))
#             if user_id is None:
#                 raise credentials_exception
#         except (JWTError, ValueError):
#             raise credentials_exception
#
#         user = await db.get(User, user_id)
#         if user is None:
#             raise credentials_exception
#
#         return user
#
#     @classmethod
#     async def get_current_medical_user(
#             cls,
#             db: AsyncSession = Depends(get_db),
#             token: str = Depends(oauth2_scheme)
#     ) -> User:
#         user = await cls.get_current_user(db, token)
#
#         if user.role not in [UserRole.MEDICAL, UserRole.ADMIN]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Доступ только для медперсонала"
#             )
#
#         return user
#
#
#     @staticmethod
#     async def refresh_token(
#             db: AsyncSession,
#             refresh_token: str
#     ) -> dict:
#         try:
#             payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#             user_id: int = int(payload.get("user_id"))
#             if user_id is None:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Invalid refresh token"
#                 )
#         except (JWTError, ValueError):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid refresh token"
#             )
#
#         user = await db.get(User, user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
#
#         new_access_token = AuthService.create_token(
#             data={"sub": user.email, "user_id": user.id, "role": user.role},
#             expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         )
#
#         return {
#             "access_token": new_access_token,
#             "token_type": "bearer"
#         }
#
#     @staticmethod
#     async def verify_role(
#             user: User,
#             required_role: UserRole
#     ) -> bool:
#         if user.role != required_role:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Required role: {required_role.value}"
#             )
#         return True

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def register_donor(
        self,
        email: str,
        password: str,
        surname: str,
        name: str,
        namedad: Optional[str] = None
    ) -> User:
        existing_user = await self.db.execute(select(User).where(User.email == email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = User(
            email=email,
            hash_password=self.get_password_hash(password),
            surname=surname,
            name=name,
            namedad=namedad,
            role=UserRole.DONOR
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()

        if not user or not self.verify_password(password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = self.create_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = self.create_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("user_id"))
            if user_id is None:
                raise credentials_exception
        except (JWTError, ValueError):
            raise credentials_exception

        user = await self.db.get(User, user_id)
        if user is None:
            raise credentials_exception

        return user

    async def get_current_medical_user(self, token: str) -> User:
        user = await self.get_current_user(token)

        if user.role not in [UserRole.MEDICAL, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ только для медперсонала"
            )

        return user

    async def refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("user_id"))
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        new_access_token = self.create_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def verify_role(user: User, required_role: UserRole) -> bool:
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role.value}"
            )
        return True


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    return await AuthService(db).get_current_user(token)


async def get_current_medical_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    return await AuthService(db).get_current_medical_user(token)