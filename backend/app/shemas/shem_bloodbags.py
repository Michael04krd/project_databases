from typing import Optional, Annotated, Self

from pydantic import BaseModel, Field, ConfigDict, AfterValidator, field_validator, model_validator
from datetime import datetime, timedelta

from ..models.BloodBags import StatusBlood,BloodGroup

def validate_collection_date(value: datetime) -> datetime:
    if value > datetime.utcnow():
        raise ValueError("Дата сбора крови не может быть в будущем")
    return value

CollectionDate = Annotated[datetime, AfterValidator(validate_collection_date)]

class BloodBagBase(BaseModel):
    blood_group:BloodGroup
    volume:int=Field(...,gt=0)
    collected_date:CollectionDate = Field(
        default_factory=datetime.utcnow,
        description="Дата сбора крови"
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="Дата истечения срока годности (автоматически рассчитывается +30 дней если не указана)"
    )
    status:StatusBlood=StatusBlood.ACTIVE



    @field_validator('expiry_date')
    def validate_expiry_date(cls, v: Optional[datetime], values: dict) -> datetime:
        if v is not None and 'collected_date' in values and v <= values['collected_date']:
            raise ValueError("Срок годности должен быть позже даты сбора")
        return v

    @model_validator(mode='after')
    def calculate_expiry_date(self) -> Self:
        if self.expiry_date is None:
            self.expiry_date = self.collected_date + timedelta(days=30)
        return self

    @field_validator('status')
    def check_status(cls, v: StatusBlood, values: dict) -> StatusBlood:
        if 'expiry_date' in values and values['expiry_date'] < datetime.utcnow():
            return StatusBlood.EXPIRED
        return v

class BloodBagCreate(BloodBagBase):
    donor_id: int = Field(..., description="ID донора")

class BloodBagUpdate(BaseModel):
    status: Optional[StatusBlood] = None
    volume: Optional[int] = Field(None, gt=0)

class BloodBagResponse(BloodBagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DonorSimple(BaseModel):
    id: int
    surname: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class BloodBagWithDonorResponse(BloodBagResponse):
    donor: DonorSimple