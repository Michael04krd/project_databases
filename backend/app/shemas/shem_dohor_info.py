from typing import Annotated, Optional

from pydantic import BaseModel, AfterValidator, Field, EmailStr, ConfigDict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from backend.app.models.DonorInfo import BloodGroup

MIN_AGE=18
def validate_date_birth(value : date)->date:
    now_date=date.today()

    if value>now_date:
        raise ValueError("Дата рождения не может быть в будущем")

    age=relativedelta(now_date,value).years
    if age<MIN_AGE:
        raise ValueError(f"Донор должен быть старше {MIN_AGE} лет")

    return value

def validate_phone(value:str)->str:
    if not value.isdigit() or len(value)!=11:
        raise ValueError("Требуется 11 цифр")

    return value

BirthDate = Annotated[date, AfterValidator(validate_date_birth)]
PhoneNumber = Annotated[str, AfterValidator(validate_phone)]

class DonorInfoBase(BaseModel):
    blood_group: BloodGroup
    height: int = Field(..., gt=0)
    weight: int = Field(..., gt=0)
    phone: PhoneNumber = Field(..., example="79189998877")
    date_birth: BirthDate = Field(..., example="1990-01-01")
    diseases: Optional[str] = Field(None, max_length=500)
    contraindications: Optional[str] = Field(None, max_length=500)



class DonorInfoCreate(DonorInfoBase):
    user_id: int

class DonorInfoUpdate(BaseModel):
    blood_group: Optional[BloodGroup] = None
    height: Optional[int] = Field(None, gt=0)
    weight: Optional[int] = Field(None, gt=0)
    phone: Optional[str] = Field(None, max_length=15)
    date_birth:Optional[BirthDate]=Field(None)
    diseases: Optional[str] = Field(None, max_length=500)
    contraindications: Optional[str] = Field(None, max_length=500)


class DonorInfoResponse(DonorInfoBase):
    id: int
    user_id: int
    is_verified: bool
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)