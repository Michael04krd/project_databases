from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum
from backend.app.models.DonorInfo import BloodGroup

from ..database import Base,intpk


class StatusBlood(str, PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"

class BloodBag(Base):
    __tablename__ = "blood_bags"
    id: Mapped[intpk]
    blood_group:Mapped[BloodGroup]
    volume:Mapped[int]
    collected_date:Mapped[datetime]=mapped_column(default=datetime.utcnow())
    expiry_date:Mapped[datetime]
    status:Mapped[StatusBlood]=mapped_column(SAEnum(StatusBlood,name="status blood"),default=StatusBlood.ACTIVE)

    donation=relationship("Donation", back_populates="blood_bag")