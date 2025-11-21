import enum

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from db.database import Base


class SolarTermKindChoices(str, enum.Enum):
    """
    절기 종류

    - JEOLGI: 24절기(소한, 입춘, 경칩 등)
    """

    JEOLGI = "JEOLGI"


class SolarTermNameChoices(str, enum.Enum):
    """
    절기 이름

    `saju.py`의 `jeolgi_to_branch`에서 사용하는 절기들만 우선 정의했습니다.
    값(value)은 실제 DB에 저장될 문자열입니다.
    """

    SOHAN = "소한"
    IPCHUN = "입춘"
    GYEONGCHIP = "경칩"
    CHEONGMYEONG = "청명"
    IPHA = "입하"
    MANGJONG = "망종"
    SOSEO = "소서"
    IPCHU = "입추"
    BAEGRO = "백로"
    HANRO = "한로"
    IPDONG = "입동"
    DAESEOL = "대설"


class SolarTerm(Base):
    """
    사주 계산에 필요한 절기 정보 테이블

    - `name` : 절기 이름 (예: '입춘', '소한' …)
    - `kind` : 절기 종류 (현재는 JEOLGI 만 사용)
    - `at`   : 절기 발생 시각(UTC 또는 타임존 포함)
    """

    __tablename__ = "solar_terms"

    id = Column(Integer, primary_key=True, index=True)

    # 절기 이름 (예: '입춘', '소한' …)
    name = Column(String, nullable=False, index=True)

    # 절기 종류 (예: 'JEOLGI')
    kind = Column(String, nullable=False, index=True)

    # 절기 발생 시각 (timezone 포함)
    at = Column(DateTime(timezone=True), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


