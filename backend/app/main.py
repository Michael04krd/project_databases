from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta

from fastapi import FastAPI
from sqlalchemy import text, select
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import  AsyncSessionLocal, Base, async_engine
from backend.app.api.med_work_api import med_work_router
from backend.app.api.auth_api import auth_router
from backend.app.api.admin_api import admin_router
from backend.app.api.donor_api import donor_router
from backend.app.models import User, DonorInfo, BloodBag, Donation
from backend.app.models.BloodBags import StatusBlood
from backend.app.models.Donation import DonationStatus
from backend.app.models.DonorInfo import BloodGroup
from backend.app.models.user import pwd_context, UserRole


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await insert_initial_data()
    yield

app = FastAPI(lifespan=lifespan)



origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:63342"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Успешно созданы таблицы")


@app.get("/test-db")
async def test_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {"status": "OK", "db_response": result.scalar()}

app.include_router(med_work_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(donor_router)
async def insert_initial_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User))
            existing_users = result.scalars().all()
            if existing_users:
                print("Пользователи уже существуют. Пропуск заполнения.")
                return

            test_users = [
                User(
                    surname="Иванов",
                    name="Иван",
                    namedad="Иванович",
                    email="admin@example.com",
                    role=UserRole.ADMIN,
                    hash_password=pwd_context.hash("admin123"),
                    is_active=True
                ),
                User(
                    surname="Петров",
                    name="Петр",
                    namedad="Петрович",
                    email="donor@example.com",
                    role=UserRole.DONOR,
                    hash_password=pwd_context.hash("donor123"),
                    is_active=True
                ),
                User(
                    surname="Петров",
                    name="Петр",
                    namedad="Петрович",
                    email="medstaff@example.com",
                    role=UserRole.MEDICAL,
                    hash_password=pwd_context.hash("med123"),
                    is_active=True
                )
            ]

            session.add_all(test_users)
            await session.flush()

            donor_info = DonorInfo(
                user_id=test_users[1].id,
                blood_group=BloodGroup.A_POSITIVE,
                phone="+79001234567",
                height=180,
                weight=75,
                date_birth=datetime(1990, 1, 1),
                diseases="Нет",
                contraindications="Нет",
                is_verified=True,
                verified_by=test_users[0].id,
                verified_at=datetime.utcnow()
            )
            session.add(donor_info)

            blood_bag = BloodBag(
                blood_group=BloodGroup.A_POSITIVE,
                volume=450,
                collected_date=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(days=42),
                status=StatusBlood.ACTIVE
            )
            session.add(blood_bag)

            donation = Donation(
                donor_id=test_users[1].id,
                medical_id=test_users[0].id,
                donation_date=datetime.utcnow(),
                next_donation_date=datetime.utcnow() + timedelta(days=90),
                status=DonationStatus.APPROVED,
                blood_bag_id=blood_bag.id
            )
            session.add(donation)

            print("✅ Тестовые данные успешно добавлены!")