from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base,intpk,str_200

class MedicalWorkerInfo(Base):
    __tablename__ = "medical_worker_info"
    id: Mapped[intpk]
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    job_title: Mapped[str_200]
    phone:Mapped[str] = mapped_column(String(15))
    hospital:Mapped[str_200]
    user = relationship("User", back_populates="medical_info")
