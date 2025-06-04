
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum

from ..database import Base,intpk


class DonationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[intpk]
    donor_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    medical_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    donation_date:Mapped[datetime]=mapped_column(default=datetime.utcnow())
    next_donation_date:Mapped[datetime]
    status:Mapped[DonationStatus]=mapped_column(SAEnum(DonationStatus,name="status donations"),default=DonationStatus.PENDING)
    blood_bag_id:Mapped[int]=mapped_column(ForeignKey("blood_bags.id"), nullable=True)

    donor = relationship(
        "User",
        back_populates="donations",
        foreign_keys=[donor_id]
    )

    medical = relationship(
        "User",
        foreign_keys=[medical_id]
    )

    blood_bag = relationship(
        "BloodBag",
        back_populates="donation",
        foreign_keys=[blood_bag_id]
    )