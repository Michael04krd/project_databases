from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.logger import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from .med_work_api import get_current_user
from ..database import get_db
from ..models import User, MedicalWorkerInfo
from ..models.user import UserRole
from ..service.serv_Admin import AdminServices
from ..shemas.shem_med_work import MedicalWorkerResponse, MedicalWorkerCreate, MedWorkUpdate
from ..shemas.shem_users import UserResponse

admin_router=APIRouter(prefix="/admin",tags=["Admin"])

@admin_router.post("/create_med_workers", response_model=MedicalWorkerResponse)
async def create_workers(
    med_data: MedicalWorkerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Требуются права администратора")

    try:
        user = User(
            email=med_data.email,
            surname=med_data.surname,
            name=med_data.name,
            namedad=med_data.namedad,
            role=UserRole.MEDICAL,
            is_active=True
        )
        user.set_password(med_data.password)
        db.add(user)
        await db.flush()

        med_info = MedicalWorkerInfo(
            user_id=user.id,
            job_title=med_data.job_title,
            hospital=med_data.hospital,
            phone=med_data.phone
        )
        db.add(med_info)
        await db.commit()

        return {
            "id": med_info.id,
            "user_id": user.id,
            "job_title": med_info.job_title,
            "hospital": med_info.hospital,
            "phone": med_info.phone,
            "user": user
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get(
    "/med_workers",
    response_model=List[MedicalWorkerResponse],
    summary="Получить всех медработников",
    responses={
        200: {"description": "Успешный запрос"},
        403: {"description": "Доступ запрещён (только для админов)"},
        404: {"description": "Медработники не найдены"},
    },
)
async def get_all_medical_workers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут просматривать этот список",
        )

    try:
        result = await db.execute(
            select(MedicalWorkerInfo)
            .options(selectinload(MedicalWorkerInfo.user))
        )
        medical_workers = result.scalars().all()

        if not medical_workers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медработники не найдены",
            )

        return [
            MedicalWorkerResponse(
                id=mw.id,
                user_id=mw.user_id,
                job_title=mw.job_title,
                phone=mw.phone,
                hospital=mw.hospital,
                user=UserResponse(
                    id=mw.user.id,
                    surname=mw.user.surname,
                    name=mw.user.name,
                    namedad=mw.user.namedad,
                    email=mw.user.email,
                    role=mw.user.role,
                    is_active=mw.user.is_active,
                    created_at=mw.user.created_at,
                ),
            )
            for mw in medical_workers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при получении данных: {str(e)}",
        )


@admin_router.delete("/med_workers/{worker_id}")
async def delete_medical_worker(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await AdminServices(db).delete_medical_worker(current_user, worker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Медицинский работник не найден")
    return {"message": "Мед.работник удален"}


@admin_router.put("/med_workers/{worker_id}", response_model=MedicalWorkerResponse)
async def update_medical_worker(
        worker_id: int,
        update_data: MedWorkUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Требуются права администратора")

    try:
        result = await db.execute(
            select(MedicalWorkerInfo)
            .where(MedicalWorkerInfo.id == worker_id)
            .options(selectinload(MedicalWorkerInfo.user))
        )
        med_info = result.scalar_one_or_none()

        if not med_info:
            raise HTTPException(status_code=404, detail="Медицинский работник не найден")

        user = med_info.user
        if update_data.surname:
            user.surname = update_data.surname
        if update_data.name:
            user.name = update_data.name
        if update_data.namedad:
            user.namedad = update_data.namedad
        if update_data.email:
            user.email = update_data.email
        if update_data.password:
            user.set_password(update_data.password)

        if update_data.job_title:
            med_info.job_title = update_data.job_title
        if update_data.hospital:
            med_info.hospital = update_data.hospital
        if update_data.phone:
            med_info.phone = update_data.phone

        await db.commit()
        await db.refresh(med_info)
        await db.refresh(user)

        return {
            "id": med_info.id,
            "user_id": user.id,
            "job_title": med_info.job_title,
            "hospital": med_info.hospital,
            "phone": med_info.phone,
            "user": user
        }

    except Exception as e:
        await db.roll



