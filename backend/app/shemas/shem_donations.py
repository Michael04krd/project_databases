from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime, timedelta
from ..models.Donation import DonationStatus

class DonationBase(BaseModel):
    donor_id:int
    medical_id:int
    donation_date:datetime=Field(default_factory=datetime.utcnow())
    next_donation_date: datetime = Field(
        ...,
        description="Дата следующей возможной донации (автоматически +3 месяца если не указана)"
    )
    status: DonationStatus = Field(
        default=DonationStatus.PENDING,
        description="Статус донации"
    )
    blood_bag_id: Optional[int] = Field(
        None,
        description="ID связанного пакета крови"
    )

    @model_validator(mode='after')
    def validate_dates(self):
        if self.next_donation_date <= self.donation_date:
            raise ValueError("Дата следующей донации должна быть позже текущей")
        if not hasattr(self, 'next_donation_date'):
            self.next_donation_date = self.donation_date + timedelta(days=90)

        return self

class DonationCreate(DonationBase):
    pass

class DonationUpdate(BaseModel):
    status: Optional[DonationStatus] = None
    blood_bag_id: Optional[int] = None

class DonationResponse(DonationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)