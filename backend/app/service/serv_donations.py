# Для работы с донациями:
#
#     createDonation(donorId, data) → Donation (обновляет запас крови и историю донора)
#
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..shemas.shem_donations import DonationResponse, DonationCreate
from ..models.Donation import Donation
from ..models.user import User,UserRole


class DonationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_donation(self,current_user: User,data:DonationCreate)->DonationResponse:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может регистрировать донации")
        medical_worker = await self.db.get(User, data.medical_id)
        if not medical_worker or medical_worker.role != UserRole.MEDICAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid medical worker"
            )

        if not hasattr(data, 'next_donation_date') or data.next_donation_date is None:
            data.next_donation_date = data.donation_date + timedelta(days=90)

        donation=Donation(**data.model_dump())
        self.db.add(donation)
        await self.db.commit()
        await self.db.refresh(donation)
        return DonationResponse.model_validate(donation)