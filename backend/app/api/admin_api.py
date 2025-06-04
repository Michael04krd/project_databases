from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .med_work_api import get_current_user
from ..database import get_db
from ..models import User
from ..service.serv_Admin import AdminServices
from ..shemas.shem_med_work import MedicalWorkerResponse, MedicalWorkerCreate

admin_router=APIRouter(prefix="/admin",tags=["Admin"])

@admin_router.post(
    "/create_med_workers",
    response_model=MedicalWorkerResponse
)
async def create_workers(
    med_data: MedicalWorkerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service=AdminServices(db)
    try:
        return await service.create_medical_worker(
            current_user=current_user,
            email_new=med_data.email,
            password_new=med_data.password,
            surname_new=med_data.surname,
            name_new=med_data.name,
            namedad_new=med_data.namedad,
            hospital_new=med_data.hospital,
            position_new=med_data.job_title,
            phone_new=med_data.phone
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@admin_router.get(
    "/med_workers",
    response_model=List[MedicalWorkerResponse]
)
async def get_all_medical_workers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AdminServices(db).get_all_medical_workers(current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@admin_router.delete(
    "/med_workers/{user_id}"
)
async def delete_medical_worker(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await AdminServices(db).delete_medical_worker(current_user, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Медицинский работник не найден")
    return {"message": "Мед.работник удален"}



