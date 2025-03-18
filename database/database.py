from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, BigInteger, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
import config

DATABASE_URL = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    first_name = Column(String, nullable=True)  # Ism
    last_name = Column(String, nullable=True)   # Familiya
    username = Column(String, nullable=True)    # Username
    referral_code = Column(String, unique=True)
    phone_number = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    card_number = Column(String, nullable=True)
    invited_by = Column(BigInteger, nullable=True)  # Taklif qilgan foydalanuvchi IDsi
    vote = Column(Integer, default=0)  # ✅ Yangi ustun - ovoz berganlar soni

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Yangi jadvallarni yaratish

async def get_referral_stats(telegram_id: int):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.invited_by == telegram_id))
        invited_users = result.scalars().all()
        return len(invited_users)  # Taklif qilingan foydalanuvchilar sonini qaytarish
    
async def select_all_invited_user_count():
    async with SessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        stats = []
        for user in users:
            invited_count = await get_referral_stats(user.telegram_id)
            stats.append({
                "full_name": user.username or "Noma'lum",
                "invited_user_count": invited_count
            })
        
        return stats
