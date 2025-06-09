from typing import Optional, Annotated

from pydantic import BaseModel, Field, ConfigDict, AfterValidator, EmailStr, field_validator

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


class MedicalWorkerCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    surname: str = Field(..., max_length=200)
    name: str = Field(..., max_length=200)
    namedad: Optional[str] = Field(None, max_length=200)
    job_title: str = Field(..., max_length=200)
    hospital: str = Field(..., max_length=200)
    phone: str = Field(..., min_length=11, max_length=15)

    @field_validator('phone')
    def validate_phone(cls, v):
        cleaned = ''.join(c for c in v if c.isdigit())
        if len(cleaned) != 11:
            raise ValueError("Номер должен содержать 11 цифр")
        return cleaned

class MedWorkUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str] = None
    surname:Optional[str]
    name: Optional[str]
    namedad:Optional[str]=None
    job_title: Optional[str]
    hospital: Optional[str]
    phone: Optional[str]

# class MedWorkUpdate(BaseModel):
#     job_title: Optional[str] = Field(None, max_length=200, example="Терапевт")
#     phone: Optional[PhoneNumber]
#     hospital: Optional[str] = Field(None, max_length=200, example="ЦРБ")

class MedicalWorkerResponse(MedicalWorkerBase):
    id: int
    user_id: int
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)