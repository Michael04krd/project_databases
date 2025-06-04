from typing import Optional, Annotated

from pydantic import BaseModel, Field, ConfigDict, AfterValidator

from backend.app.shemas.shem_users import UserResponse


def validate_phone(value:str)->str:
    if not value.isdigit() or len(value)!=11:
        raise ValueError("Требуется 11 цифр")

    return value

PhoneNumber = Annotated[str, AfterValidator(validate_phone)]


class MedicalWorkerBase(BaseModel):
    job_title: str = Field(..., max_length=200, example="Врач-гематолог")
    hospital: str = Field(..., max_length=200, example="Городская больница №1")
    phone: PhoneNumber = Field(..., example="79189998877")


class MedicalWorkerCreate(MedicalWorkerBase):
    user_id: int

class MedWorkUpdate(BaseModel):
    job_title: Optional[str] = Field(None, max_length=200, example="Терапевт")
    phone: Optional[PhoneNumber]
    hospital: Optional[str] = Field(None, max_length=200, example="ЦРБ")

class MedicalWorkerResponse(MedicalWorkerBase):
    id: int
    user_id: int
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)