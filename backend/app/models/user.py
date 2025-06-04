from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum
from ..database import Base,intpk,str_200
from passlib.context import CryptContext

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")


class UserRole(str, PyEnum):
    ADMIN = "admin"
    MEDICAL = "medical"
    DONOR = "donor"

class User(Base):
    __tablename__ = "users"
    id:Mapped[intpk]
    surname:Mapped[str_200]
    name:Mapped[str_200]
    namedad:Mapped[str_200|None]
    email:Mapped[str_200]=mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role_enum"),
        default=UserRole.DONOR
    )
    is_active:Mapped[bool]=mapped_column(default=True)
    created_at:Mapped[datetime]=mapped_column(default=datetime.utcnow)

    donor_info = relationship(
        "DonorInfo",
        back_populates="user",
        uselist=False,
        foreign_keys="[DonorInfo.user_id]"
    )
    donations = relationship(
        "Donation",
        back_populates="donor",
        foreign_keys="Donation.donor_id")
    medical_info = relationship(
        "MedicalWorkerInfo",
        back_populates="user",
        uselist=False,
        foreign_keys="MedicalWorkerInfo.user_id"
    )
    hash_password:Mapped[str]

    def set_password(self, password: str):
        self.hash_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        if not self.hash_password:
            return False
        return pwd_context.verify(password, self.hash_password)
