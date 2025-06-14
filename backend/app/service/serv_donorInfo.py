from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.Donation import DonationStatus,Donation
from ..shemas.shem_users import UserResponse
from ..shemas.shem_dohor_info import DonorInfoResponse
from ..shemas.shem_donations import DonationResponse

class DonorServices:
    def __init__(self,db:AsyncSession):
        self.db=db

    async def get_info_donor(self,user_id:int)->dict:
        res=await self.db.execute(
            select(User)
            .where(User.id==user_id)
            .options(selectinload(User.donor_info))
        )
        user = res.scalar_one_or_none()

        if not user:
            raise ValueError("Пользователь не найден")

        if not user.donor_info:
            return {
                "user": {
                    "surname": user.surname,
                    "name": user.name,
                    "namedad": user.namedad,
                    "email": user.email,
                    "id": user.id
                },
                "donor_info": None
            }

        return {
            "user": {
                "surname": user.surname,
                "name": user.name,
                "namedad": user.namedad,
                "email": user.email,
                "id": user.id
            },
            "donor_info": {
                "blood_group": user.donor_info.blood_group,
                "date_birth": user.donor_info.date_birth.isoformat() if user.donor_info.date_birth else None,
                "phone": user.donor_info.phone,
                "height": user.donor_info.height,
                "weight": user.donor_info.weight,
                "diseases": user.donor_info.diseases if user.donor_info else None,
                "contraindications": user.donor_info.contraindications if user.donor_info else None,
                "is_verified": user.donor_info.is_verified if user.donor_info else False,
                "verified_by": user.donor_info.verified_by if user.donor_info else None,
                "verified_at": user.donor_info.verified_at.isoformat() if user.donor_info and user.donor_info.verified_at else None,
            }
        }

    async def get_info_donor_with_email(self,email:EmailStr) -> dict:
        res = await self.db.execute(
            select(User)
            .where(User.email== email)
            .options(selectinload(User.donor_info))
        )
        user = res.scalar_one_or_none()
        if not user.donor_info:
            raise ValueError("Донор не найден")

        return {
            "user": UserResponse.model_validate(user),
            "donor_info": DonorInfoResponse.model_validate(user.donor_info)
        }

    async def get_donor_donations(self,user_id:int)->List[DonationResponse]:
        res=await self.db.execute(
            select(Donation)
            .where(Donation.donor_id==user_id)
            .order_by(Donation.donation_date.desc())
        )
        donationd=res.scalars().all()
        return [DonationResponse.model_validate(d) for d in donationd]

    async def check_next_donation(self, user_id: int) -> dict:
        res = await self.db.execute(
            select(Donation)
            .where(
                (Donation.donor_id == user_id) &
                (Donation.status == DonationStatus.APPROVED)
            )
            .order_by(Donation.donation_date.desc())
            .limit(1)
        )
        last_donation = res.scalar_one_or_none()

        if not last_donation:
            return {
                "can_donate": True,
                "reason": "No previous donations found",
                "next_possible_date": None
            }

        next_possible_date = last_donation.donation_date + timedelta(days=90)
        today = datetime.now()

        return {
            "can_donate": today >= next_possible_date,
            "next_possible_date": next_possible_date,
            "days_remaining": (next_possible_date - today).days if today < next_possible_date else 0,
            "last_donation_date": last_donation.donation_date
        }
