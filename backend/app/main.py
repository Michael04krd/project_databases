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
from backend.app.models import User, DonorInfo, BloodBag, Donation, MedicalWorkerInfo
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
                    hash_password=pwd_context.hash("Admin12345"),
                    is_active=True
                ),
                User(
                    surname="Смирнова",
                    name="Ольга",
                    namedad="Сергеевна",
                    email="admin2@example.com",
                    role=UserRole.ADMIN,
                    hash_password=pwd_context.hash("OlgaAdmin2023"),
                    is_active=True
                ),
                User(
                    surname="Петров",
                    name="Петр",
                    namedad="Петрович",
                    email="donor@example.com",
                    role=UserRole.DONOR,
                    hash_password=pwd_context.hash("PetrovDonor1"),
                    is_active=True
                ),
                User(
                    surname="Васильева",
                    name="Мария",
                    namedad="Игоревна",
                    email="donor2@example.com",
                    role=UserRole.DONOR,
                    hash_password=pwd_context.hash("MariaDonor2"),
                    is_active=True
                ),
                User(
                    surname="Николаев",
                    name="Алексей",
                    namedad="Дмитриевич",
                    email="donor3@example.com",
                    role=UserRole.DONOR,
                    hash_password=pwd_context.hash("AlexeyDonor3"),
                    is_active=True
                ),
                User(
                    surname="Фролова",
                    name="Екатерина",
                    namedad="Андреевна",
                    email="donor4@example.com",
                    role=UserRole.DONOR,
                    hash_password=pwd_context.hash("FrolovaKatya4"),
                    is_active=True
                )
            ]

            session.add_all(test_users)
            await session.flush()

            additional_medical_workers = [
                User(
                    surname="Козлова",
                    name="Анна",
                    namedad="Владимировна",
                    email="surgeon@example.com",
                    role=UserRole.MEDICAL,
                    hash_password=pwd_context.hash("Surgeon456"),
                    is_active=True
                ),
                User(
                    surname="Сидоров",
                    name="Дмитрий",
                    namedad="Алексеевич",
                    email="nurse@example.com",
                    role=UserRole.MEDICAL,
                    hash_password=pwd_context.hash("Nurse789"),
                    is_active=True
                )
            ]

            session.add_all(additional_medical_workers)
            await session.flush()

            for user in additional_medical_workers:
                mw_info = MedicalWorkerInfo(
                    user_id=user.id,
                    job_title="Хирург" if "surgeon" in user.email else "Медсестра",
                    hospital="Городская больница №1",
                    phone="79001234562"
                )
                session.add(mw_info)

            donors_info = [
                DonorInfo(
                    user_id=test_users[2].id,
                    blood_group=BloodGroup.A_POSITIVE,
                    phone="79001234567",
                    height=180,
                    weight=75,
                    date_birth=datetime(1990, 1, 1),
                    diseases="Нет",
                    contraindications="Нет",
                    is_verified=True,
                    verified_by=test_users[0].id,
                    verified_at=datetime.utcnow()
                ),
                DonorInfo(
                    user_id=test_users[3].id,
                    blood_group=BloodGroup.B_NEGATIVE,
                    phone="79011234567",
                    height=165,
                    weight=58,
                    date_birth=datetime(1995, 5, 15),
                    diseases="Аллергия на пенициллин",
                    contraindications="Нет",
                    is_verified=True,
                    verified_by=test_users[0].id,
                    verified_at=datetime.utcnow()
                ),
                DonorInfo(
                    user_id=test_users[4].id,
                    blood_group=BloodGroup.AB_POSITIVE,
                    phone="79021234567",
                    height=175,
                    weight=70,
                    date_birth=datetime(1985, 7, 22),
                    diseases="Нет",
                    contraindications="Гипертония",
                    is_verified=True,
                    verified_by=test_users[1].id,
                    verified_at=datetime.utcnow()
                ),
                DonorInfo(
                    user_id=test_users[5].id,
                    blood_group=BloodGroup.O_NEGATIVE,
                    phone="79031234567",
                    height=170,
                    weight=60,
                    date_birth=datetime(1992, 3, 10),
                    diseases="Нет",
                    contraindications="Нет",
                    is_verified=False,
                    verified_by=None,
                    verified_at=None
                )
            ]
            session.add_all(donors_info)

            blood_bags = [
                BloodBag(
                    blood_group=BloodGroup.A_POSITIVE,
                    volume=450,
                    collected_date=datetime.utcnow(),
                    expiry_date=datetime.utcnow() + timedelta(days=42),
                    status=StatusBlood.ACTIVE
                ),
                BloodBag(
                    blood_group=BloodGroup.B_NEGATIVE,
                    volume=450,
                    collected_date=datetime.utcnow() - timedelta(days=10),
                    expiry_date=datetime.utcnow() + timedelta(days=32),
                    status=StatusBlood.ACTIVE
                ),
                BloodBag(
                    blood_group=BloodGroup.AB_POSITIVE,
                    volume=450,
                    collected_date=datetime.utcnow() - timedelta(days=5),
                    expiry_date=datetime.utcnow() + timedelta(days=37),
                    status=StatusBlood.ACTIVE
                )
            ]
            session.add_all(blood_bags)
            await session.flush()

            donations = [
                Donation(
                    donor_id=test_users[3].id,
                    medical_id=additional_medical_workers[0].id,
                    donation_date=datetime.utcnow(),
                    next_donation_date=datetime.utcnow() + timedelta(days=90),
                    status=DonationStatus.APPROVED,
                    blood_bag_id=blood_bags[0].id
                ),
                Donation(
                    donor_id=test_users[4].id,
                    medical_id=additional_medical_workers[1].id,
                    donation_date=datetime.utcnow() - timedelta(days=30),
                    next_donation_date=datetime.utcnow() + timedelta(days=60),
                    status=DonationStatus.APPROVED,
                    blood_bag_id=blood_bags[1].id
                ),
                Donation(
                    donor_id=test_users[5].id,
                    medical_id=test_users[2].id,  # Первый медработник
                    donation_date=datetime.utcnow() - timedelta(days=15),
                    next_donation_date=datetime.utcnow() + timedelta(days=75),
                    status=DonationStatus.APPROVED,
                    blood_bag_id=blood_bags[2].id
                ),

            ]
            session.add_all(donations)

            print("✅ Тестовые данные успешно добавлены!")