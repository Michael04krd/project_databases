from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from backend.app.models import User
from backend.app.service.serv_auth import AuthService
from backend.app.service.serv_med_work import MedWorkService
from backend.app.shemas.shem_dohor_info import DonorInfoResponse, DonorInfoCreate, DonorInfoUpdate, DonorListResponse
from fastapi.security import OAuth2PasswordBearer

from ..models.DonorInfo import BloodGroup
from ..service.serv_bloodBags import BloodBagsService
from ..service.serv_donations import DonationService
from ..shemas.shem_bloodbags import BloodBagResponse, BloodBagUpdate
from ..shemas.shem_dohor_info import DonorInfoCreate
from ..shemas.shem_donations import DonationResponse,DonationCreate,DonationStatus,DonationUpdate

med_work_router=APIRouter(prefix="/med_work",tags=["Workers"])



# Мед. работники (role=medical)
# Управление донорами:
#
#     GET /medical/donors – список доноров с фильтрами:
#
#         Группа крови
#
#         Статус верификации (is_verified)
#
#         ФИО (поиск)
#
#         Дата последней донации
#
#     POST /medical/donors – добавление донора (полная форма)
#
#     PUT /medical/donors/{id} – редактирование донора
#
#     DELETE /medical/donors/{id} – удаление донора
#
#     POST /medical/donors/{id}/verify – подтверждение/отклонение донора (обновляет is_verified, verified_by, verified_at)
#
# Управление донациями:
#
#     POST /medical/donations – регистрация новой донации
#
# Управление запасами крови:
#
#     GET /medical/blood-bags – список запасов крови:
#
#         Сортировка по сроку годности
#
#         Фильтры: группа крови, статус (активные/просроченные)
#
#     PUT /medical/blood-bags/{id}/status – обновление статуса крови

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    return await AuthService(db).get_current_user(token)

@med_work_router.get(
    "donors",
    response_model=DonorInfoResponse
)
async def get_donors(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        blood_type: Optional[str] = None,
        is_verified: Optional[bool] = None,
        search_query: Optional[str] = None,
        last_donation_date: Optional[datetime] = None,
):
    service=MedWorkService(db)

    try:
        return await service.get_donor(current_user,blood_type,
                                       is_verified,search_query,
                                       last_donation_date)
    except ValueError as e:
         raise HTTPException(status_code=404, detail=str(e))


@med_work_router.post(
    "create_donor",
response_model=DonorInfoResponse
)
async def create_donor(
    data:DonorInfoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service=MedWorkService(db)

    try:
        return await service.create_donor(current_user,data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@med_work_router.put("/donors/{donor_id}",
                     response_model=DonorInfoResponse)
async def update_donor(
    donor_id: int,
    donor_data: DonorInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service=MedWorkService(db)

    result=await service.update_donor(current_user,donor_id,donor_data)
    if not result:
        raise HTTPException(status_code=404,detail="Донор не найден")

    return result

@med_work_router.delete("/delete_donor/{donor_id}")
async def delete_donor(
    donor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service=MedWorkService(db)
    res=service.delete_donor(current_user,donor_id)
    if not res:
        raise HTTPException(status_code=404, detail="Донор не найден")
    return {"message":"Donor deleted"}

@med_work_router.post(
    "/donors/{donor_id}/verify",
    response_model=DonorInfoResponse
)
async def verify_donor(
    donor_id: int,
    status: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await MedWorkService(db).verify_donor(
        current_user=current_user,
        donor_id=donor_id,
        medical_worker_id=current_user.id,
        status=status
    )
    if not result:
        raise HTTPException(status_code=404, detail="Donor not found")
    return result

@med_work_router.post(
    "/donations",
response_model=DonationResponse
)
async def create_donat(
        donation_data:DonationCreate,
        current_user:User=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service=DonationService(db)
    try:
        return await service.create_donation(current_user,donation_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@med_work_router.get(
    "/bloodbags",
    response_model=List[BloodBagResponse]
)
async def get_blood_bags(
    blood_type: Optional[str] = None,
    is_expired: Optional[bool] = None,
    sort_by_expiry: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await BloodBagsService(db).get_blood_bags(
            current_user=current_user,
            blood_type=blood_type,
            is_expired=is_expired,
            sort_by_expiry=sort_by_expiry
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@med_work_router.put(
    "/blood-bags/{blood_bag_id}/status",
    response_model=BloodBagResponse
)
async def update_blood_bag_status(
    blood_bag_id: int,
    status_update: BloodBagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service=BloodBagsService(db)
    result = await service.update_blood_bag_status(
        current_user=current_user,
        blood_bag_id=blood_bag_id,
        status=status_update.status
    )
    if not result:
        raise HTTPException(status_code=404, detail="Blood bag not found")
    return result



@med_work_router.get(
    "/get_all_donors",
    response_model=List[DonorListResponse],
    summary="Получить список всех доноров",
    description="Возвращает список доноров с возможностью фильтрации"
)
async def get_all_donors(
    blood_type: Optional[BloodGroup] = Query(None, description="Фильтр по группе крови"),
    is_verified: Optional[bool] = Query(None, description="Фильтр по статусу верификации"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности аккаунта"),
    search_query: Optional[str] = Query(None, description="Поиск по ФИО, email или телефону"),
    last_donation_date: Optional[datetime] = Query(None, description="Фильтр по дате последней донации"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MedWorkService(db)
        return await service.get_all_donors(
            current_user=current_user,
            blood_type=blood_type,
            is_verified=is_verified,
            is_active=is_active,
            search_query=search_query,
            last_donation_date=last_donation_date
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@med_work_router.get("/me_info", response_model=dict)
async def get_my_medical_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = MedWorkService(db)
    try:
        result = await service.get_med_worker_info(current_user.id)
        if not result.get('medical_info'):
            raise HTTPException(
                status_code=404,
                detail="Информация о медицинском работнике не заполнена"
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )