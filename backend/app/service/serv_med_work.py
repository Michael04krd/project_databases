
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..models.user import User, UserRole
from ..models.DonorInfo import DonorInfo,BloodGroup
from ..models.Donation import Donation, DonationStatus
from ..shemas.shem_dohor_info import DonorInfoResponse, DonorInfoCreate, DonorInfoUpdate


class MedWorkService:
    def __init__(self,db:AsyncSession):
        self.db=db

    async def get_donor(self,
                        current_user: User,
                        blood_type: Optional[BloodGroup] = None,
                        is_verified: Optional[bool] = None,
                        search_query: Optional[str] = None,
                        last_donation_date: Optional[datetime] = None
                        ) -> List[DonorInfoResponse]:

        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может просматривать доноров")
        query=select(DonorInfo).options(
            selectinload(DonorInfo.user)
        )
        filters = []
        if blood_type:
            filters.append(DonorInfo.blood_group == blood_type)
        if is_verified is not None:
            filters.append(DonorInfo.is_verified == is_verified)
        if search_query:
            filters.append(or_(
                User.surname.ilike(f"%{search_query}%"),
                User.name.ilike(f"%{search_query}%")
            ))
        if last_donation_date:
            subquery = select(Donation.donor_id).where(
                Donation.donation_date >= last_donation_date
            ).distinct()
            filters.append(DonorInfo.user_id.in_(subquery))

        if filters:
            query = query.join(User).where(and_(*filters))

        result = await self.db.execute(query)
        donors = result.scalars().all()

        return [DonorInfoResponse.model_validate(d) for d in donors]

    async def create_donor(self,current_user: User,data:DonorInfoCreate)->DonorInfoResponse:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может регистрировать доноров")
        user = await self.db.get(User, data.user_id)
        if not user or user.role != UserRole.DONOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a donor"
            )
        donor=DonorInfo(**data.model_dump())
        self.db.add(donor)
        await self.db.commit()
        await  self.db.refresh(donor)
        return DonorInfoResponse.model_validate(donor)


    async def update_donor(self,  current_user: User,donor_id: int, data: DonorInfoUpdate) -> Optional[DonorInfoResponse]:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может обновлять данные доноров")
        donor=await self.db.get(DonorInfo,donor_id)
        if not donor:
            return None
        update_data=data.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(donor,key,value)

        await self.db.commit()
        await self.db.refresh(donor)
        return DonorInfoResponse.model_validate(donor)


    async def delete_donor(self, current_user: User, donor_id: int) -> bool:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может удалять доноров")
        result = await self.db.execute(
            delete(DonorInfo).where(DonorInfo.id == donor_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def verify_donor(
            self,
            current_user: User,
            donor_id: int,
            medical_worker_id: int,
            status: bool
    ) -> Optional[DonorInfoResponse]:
        if current_user.role != UserRole.MEDICAL:
            raise HTTPException(status_code=403, detail="Только мед. работник может верифицировать доноров")
        donor = await self.db.get(DonorInfo, donor_id)
        if not donor:
            return None

        donor.is_verified = status
        donor.verified_by = medical_worker_id
        donor.verified_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(donor)
        return DonorInfoResponse.model_validate(donor)
