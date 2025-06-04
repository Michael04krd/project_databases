from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..database import get_db
from ..service.serv_auth import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from .med_work_api import get_current_user
from ..shemas.auth import TokenResponse
from ..shemas.shem_users import UserResponse, UserCreate

auth_router=APIRouter(prefix="/auth",tags=["Auth"])


@auth_router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Регистрация нового донора",
             description="Создает нового пользователя с ролью DONOR")
async def register_donor(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    name_parts = user_data.full_name.split(' ')
    surname = name_parts[0] if len(name_parts) > 0 else ''
    name = name_parts[1] if len(name_parts) > 1 else ''
    namedad = name_parts[2] if len(name_parts) > 2 else None

    try:
        return await AuthService(db).register_donor(
            email=user_data.email,
            password=user_data.password,
            surname=surname,
            name=name,
            namedad=namedad
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@auth_router.post("/login",
             response_model=TokenResponse,
             summary="Аутентификация пользователя",
             description="Возвращает access и refresh токены для аутентификации")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        tokens = await AuthService.login(db, email=form_data.username, password=form_data.password)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post("/auth/refresh",
             response_model=TokenResponse,
             summary="Обновление access токена",
             description="Возвращает новый access токен по refresh токену")
async def refresh_token(
        refresh_token: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        return await AuthService(db).refresh_token(refresh_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )