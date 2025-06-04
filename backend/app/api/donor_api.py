from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .med_work_api import get_current_user
from ..database import get_db
from ..models import User
from ..service.serv_donorInfo import DonorServices
from ..shemas.shem_donations import DonationResponse

donor_router=APIRouter(prefix="/donors",tags=["Donors"])

@donor_router.get("/me",response_model=dict)
async def get_my_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service=DonorServices(db)
    try:
        return await service.get_info_donor(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Информация о доноре не найдена")


@donor_router.get(
    "/me/donations",
    response_model=List[DonationResponse]
)
async def get_my_donations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await DonorServices(db).get_donor_donations(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Информация о донациях не найдена")


@donor_router.get(
    "/me/next_donations",
    response_model=dict
)
async def check_next_donation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await DonorServices(db).check_next_donation(current_user.id)


