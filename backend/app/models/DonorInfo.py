from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum

from ..database import Base,intpk,str_200


class BloodGroup(str, PyEnum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class DonorInfo(Base):
    __tablename__ = "donor_info"
    id:Mapped[intpk]
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    blood_group: Mapped[BloodGroup] = mapped_column(
        SAEnum(BloodGroup, name="blood_group_enum")
    )
    phone:Mapped[Optional[str]] = mapped_column(String(15))
    height:Mapped[int]
    weight:Mapped[int]
    date_birth: Mapped[datetime]
    diseases:Mapped[str]=mapped_column(String(500),nullable=True)
    contraindications:Mapped[str]=mapped_column(String(500),nullable=True)
    is_verified:Mapped[bool]=mapped_column(default=False)
    verified_by:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    user = relationship("User", back_populates="donor_info", foreign_keys=[user_id])
    verified_by_user = relationship("User", foreign_keys=[verified_by])