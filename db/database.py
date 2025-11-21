from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

# asyncpg 예외 처리
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 구성 (비동기용 asyncpg 드라이버 사용)
DATABASE_URL_ORIGINAL = os.getenv(
    "DATABASE_URL",
)

# 원본 URL 저장 (동기 엔진용)
SYNC_DATABASE_URL = DATABASE_URL_ORIGINAL

# 비동기용 URL 변환 (postgresql:// → postgresql+asyncpg://)
DATABASE_URL = DATABASE_URL_ORIGINAL
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

# 동기 SQLAlchemy 엔진 생성 (saju.py 등에서 사용)
# postgresql+asyncpg:// → postgresql+psycopg2:// 변환
sync_database_url = SYNC_DATABASE_URL
if sync_database_url.startswith("postgresql+asyncpg://"):
    sync_database_url = sync_database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
elif sync_database_url.startswith("postgresql://"):
    # psycopg2 사용 시도
    try:
        import psycopg2
        sync_database_url = sync_database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    except ImportError:
        # psycopg2가 없으면 기본 postgresql:// 사용 (psycopg2 설치 필요)
        print("⚠️  [DB] psycopg2가 설치되지 않았습니다. 동기 엔진 사용을 위해 'pip install psycopg2-binary'를 실행하세요.")

try:
    sync_engine = create_engine(
        sync_database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False  # 동기 엔진은 로깅 비활성화 (비동기 엔진만 로깅)
    )
except Exception as e:
    print(f"⚠️  [DB] 동기 엔진 생성 실패: {e}")
    sync_engine = None

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
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"데이터베이스 작업 중 오류가 발생했습니다: {str(e)}"
                )
            except Exception as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"예상치 못한 오류가 발생했습니다: {str(e)}"
                )
            finally:
                await session.close()
    except Exception as e:
        # 데이터베이스 연결 자체가 실패한 경우
        error_msg = str(e)
        error_type = type(e).__name__
        
        # asyncpg 예외 처리
        if ASYNCPG_AVAILABLE and isinstance(e, (asyncpg.exceptions.InvalidAuthorizationSpecificationError,
                                                asyncpg.exceptions.InvalidPasswordError,
                                                asyncpg.exceptions.InvalidCatalogNameError)):
            if "does not exist" in error_msg or "role" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="데이터베이스 연결에 실패했습니다. 데이터베이스 사용자 또는 설정을 확인해주세요."
                )
            elif "password" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="데이터베이스 인증에 실패했습니다. 비밀번호를 확인해주세요."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"데이터베이스 연결 오류: {error_msg}"
                )
        
        # 일반적인 연결 오류 처리
        if "does not exist" in error_msg or "role" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결에 실패했습니다. 데이터베이스 사용자 또는 설정을 확인해주세요."
            )
        elif "connection" in error_msg.lower() or "refused" in error_msg.lower() or "Connection" in error_type:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 서버에 연결할 수 없습니다. 데이터베이스가 실행 중인지 확인해주세요."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"데이터베이스 연결 오류: {error_msg}"
            )


# 데이터베이스 연결 확인 함수
async def ping_db():
    """데이터베이스 연결 상태를 확인하고 정보를 출력합니다."""
    try:
        async with engine.begin() as conn:
            row = (await conn.execute(text(
                "select current_user, current_database(), inet_server_addr(), inet_server_port();"
            ))).one()
            print(f"✅ [DB] connected as user={row[0]} db={row[1]} host={row[2]} port={row[3]}")
            return True
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "role" in error_msg.lower():
            print(f"⚠️  [DB] 연결 실패: 데이터베이스 사용자가 존재하지 않습니다. (오류: {error_msg})")
        elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
            print(f"⚠️  [DB] 연결 실패: 데이터베이스 서버에 연결할 수 없습니다. (오류: {error_msg})")
        else:
            print(f"⚠️  [DB] 연결 실패: {error_msg}")
        # 애플리케이션은 계속 실행되도록 예외를 다시 발생시키지 않음
        # 대신 False를 반환하여 연결 실패를 알림
        return False

