# Для работы с запасами крови:
#
#     getBloodBags(filters) → BloodBag[]
#     Фильтры: bloodType, isExpired, sortByExpiry
#
#     updateBloodBagStatus(id, status) → BloodBag



from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import BloodBag
from ..models.BloodBags import StatusBlood
from ..models.user import User, UserRole
from ..models.DonorInfo import DonorInfo,BloodGroup
from ..models.Donation import Donation, DonationStatus
from ..shemas.shem_dohor_info import DonorInfoResponse, DonorInfoCreate, DonorInfoUpdate
from ..shemas.shem_bloodbags import BloodBagResponse, BloodBagCreate, BloodBagUpdate

class BloodBagsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_blood_bags(
            self,
            current_user: User,
            blood_type: Optional[BloodGroup] = None,
            is_expired: Optional[bool] = None,
            sort_by_expiry: bool = False
    ) -> List[BloodBagResponse]:
        if current_user.role != UserRole.MEDICAL or current_user.role != UserRole.ADMIN :
            raise HTTPException(status_code=403, detail="Только мед. работник может просматривать запасы крови")
        query = select(BloodBag)
        if blood_type:
            query = query.where(BloodBag.blood_group == blood_type)
        if is_expired is not None:
            if is_expired:
                query = query.where(BloodBag.expiry_date < datetime.utcnow())
            else:
                query = query.where(BloodBag.expiry_date >= datetime.utcnow())

        if sort_by_expiry:
            query = query.order_by(BloodBag.expiry_date.asc())

        result = await self.db.execute(query)
        blood_bags = result.scalars().all()

        return [BloodBagResponse.model_validate(b) for b in blood_bags]

    async def update_blood_bag_status(
            self,
            current_user: User,
            blood_bag_id: int,
            status: StatusBlood
    ) -> Optional[BloodBagResponse]:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может обновлять статус пакетов крови")
        blood_bag = await self.db.get(BloodBag, blood_bag_id)
        if not blood_bag:
            return None
        blood_bag.status = status
        await self.db.commit()
        await self.db.refresh(blood_bag)
        return BloodBagResponse.model_validate(blood_bag)