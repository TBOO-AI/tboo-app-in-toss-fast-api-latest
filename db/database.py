from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, text
from sqlalchemy.engine.url import make_url
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 구성 (비동기용 asyncpg 드라이버 사용)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

# postgresql:// → postgresql+asyncpg:// 변환
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# DATABASE_URL 마스킹하여 출력
try:
    _url = make_url(DATABASE_URL)
    print("🔌 [DB] URL =", _url.set(password="***"))
except Exception:
    print("🔌 [DB] URL 파싱 실패(형식 확인 필요)")

# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 연결이 끊어졌을 때 자동으로 재연결
    pool_size=10,
    max_overflow=20,
    echo=True  # SQL 쿼리 로깅 활성화
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base 클래스 생성 (모델들이 상속받을 클래스)
Base = declarative_base()


# 의존성 주입을 위한 비동기 데이터베이스 세션 생성 함수
async def get_db():
    """
    FastAPI의 의존성 주입을 위한 비동기 데이터베이스 세션 생성 함수
    
    사용 예시:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            items = result.scalars().all()
            return items
        
        @app.post("/items/")
        async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
            db_item = Item(**item.model_dump())
            db.add(db_item)
            await db.commit()
            await db.refresh(db_item)
            return db_item
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 데이터베이스 연결 확인 함수
async def ping_db():
    """데이터베이스 연결 상태를 확인하고 정보를 출력합니다."""
    try:
        async with engine.begin() as conn:
            row = (await conn.execute(text(
                "select current_user, current_database(), inet_server_addr(), inet_server_port();"
            ))).one()
            print(f"✅ [DB] connected as user={row[0]} db={row[1]} host={row[2]} port={row[3]}")
    except Exception as e:
        print(f"❌ [DB] 연결 실패: {e}")
        raise

