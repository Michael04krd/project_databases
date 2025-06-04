from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from starlette import status

from ..models.med_work import MedicalWorkerInfo
from ..models.user import User, UserRole
from ..shemas.shem_med_work import MedicalWorkerCreate, MedicalWorkerResponse
from ..shemas.shem_users import UserCreate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminServices:
    def __init__(self,db:AsyncSession):
        self.db=db

    async def create_medical_worker(
            self,
            current_user: User,
            email_new: str,
            password_new: str,
            surname_new: str,
            name_new: str,
            namedad_new: Optional[str],
            hospital_new: str,
            position_new: str,
            phone_new: str
    ) -> tuple[User, MedicalWorkerInfo]:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Только админ может создавать мед. работников")
        existing_user = await self.db.execute(
            select(User).where(User.email == email_new)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Работник с таким email уже зарегистрирован в системе")

        user=User(
            email=email_new,
            surname=surname_new,
            name=name_new,
            namedad=namedad_new,
            role=UserRole.MEDICAL,
            is_active=True
        )
        user.set_password(password_new)
        self.db.add(user)
        await self.db.flush()

        med_info=MedicalWorkerInfo(
            user_id=user.id,
            job_title=position_new,
            hospital=hospital_new,
            phone=phone_new
        )
        self.db.add(med_info)
        await self.db.commit()
        return user,med_info

    async def get_all_medical_workers(self,current_user: User) -> List[MedicalWorkerResponse]:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Только админ может просматривать список мед. работников")
        result = await self.db.execute(
            select(MedicalWorkerInfo)
            .options(selectinload(MedicalWorkerInfo.user))
        )

        medical_workers = result.scalars().all()

        return [
            MedicalWorkerResponse(
                id=mw.id,
                user_id=mw.user_id,
                job_title=mw.job_title,
                hospital=mw.hospital,
                phone=mw.phone,
                user=UserResponse(
                    id=mw.user.id,
                    surname=mw.user.surname,
                    name=mw.user.name,
                    namedad=mw.user.namedad,
                    email=mw.user.email,
                    role=mw.user.role,
                    is_active=mw.user.is_active,
                    created_at=mw.user.created_at
                )
            )
            for mw in medical_workers
        ]

    async def delete_medical_worker(self,current_user: User ,user_id: int) -> bool:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Только админ может удалять мед. работников")

        user=await self.db.get(User,user_id)
        if not user or user.role!=UserRole.MEDICAL:
            return False

        await self.db.execute(
            delete(MedicalWorkerInfo)
            .where(MedicalWorkerInfo.user_id==user_id)
        )
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def update_medical_worker(
        self,
        current_user: User,
        user_id: int,
        job_title: Optional[str] = None,
        hospital: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Optional[MedicalWorkerInfo]:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Только админ может обновлять данные мед. работников")

        med_info=await self.db.get(MedicalWorkerInfo,user_id)
        if not med_info:
            return None
        if job_title is not None:
            med_info.job_title=job_title

        if hospital is not None:
            med_info.hospital = hospital
        if phone is not None:
            med_info.phone = phone

        await self.db.commit()
        await self.db.refresh(med_info)
        return med_info




