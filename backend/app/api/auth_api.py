
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..database import get_db
from ..models import DonorInfo
from ..models.user import UserRole, User
from ..service.serv_auth import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from .med_work_api import get_current_user
from ..shemas.auth import TokenResponse
from ..shemas.shem_dohor_info import DonorInfoResponse, DonorInfoCreate
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
    try:
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        user = User(
            surname=user_data.surname,
            name=user_data.name,
            namedad=user_data.namedad,
            email=user_data.email,
            role=UserRole.DONOR
        )
        user.set_password(user_data.password)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/donors/{user_id}/info",
            response_model=DonorInfoResponse,
                  dependencies=[Depends(AuthService.get_current_medical_user)])
async def add_donor_info(
    user_id: int,
    donor_data: DonorInfoCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user or user.role != UserRole.DONOR:
        raise HTTPException(status_code=404, detail="User not found")

    donor_info = DonorInfo(
        user_id=user_id,
        **donor_data.model_dump()
    )

    db.add(donor_info)
    await db.commit()
    await db.refresh(donor_info)

    return donor_info


@auth_router.post("/login/donor",
                  response_model=TokenResponse,
                  summary="Аутентификация донора",
                  description="Возвращает access и refresh токены для донора")
async def login_donor(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await AuthService.get_user_by_email(db, form_data.username)
        if not user or not AuthService.verify_password(form_data.password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        if user.role != UserRole.DONOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ только для доноров"
            )

        tokens = await AuthService.login(db, email=form_data.username, password=form_data.password)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_role": user.role.value
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post("/login/staff",
                  response_model=TokenResponse,
                  summary="Аутентификация персонала",
                  description="Возвращает access и refresh токены для мед. работников и админов")
async def login_staff(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await AuthService.get_user_by_email(db, form_data.username)
        if not user or not AuthService.verify_password(form_data.password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        if user.role not in [UserRole.MEDICAL, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ только для персонала"
            )

        tokens = await AuthService.login(db, email=form_data.username, password=form_data.password)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_role": user.role.value
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