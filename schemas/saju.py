from datetime import datetime
from typing import Literal, Dict, Any, List

from pydantic import BaseModel, Field


class SajuRequest(BaseModel):
    """
    사주 계산 요청 스키마

    - birth: 출생 시각 (타임존 포함 ISO8601, 예: 1997-01-01T12:30:00+09:00)
    - gender: "male" 또는 "female"
    - birth_longitude: 출생지 경도 (도 단위, 예: 127.0)
    """

    birth: datetime = Field(..., description="출생 시각 (타임존 포함)")
    gender: Literal["male", "female"] = Field(..., description="성별")
    birth_longitude: float = Field(..., description="출생지 경도 (도 단위)")


class SajuResponse(BaseModel):
    """
    사주 계산 결과 스키마

    깊이 있는 해석용 전체 정보를 그대로 반환합니다.
    """

    spti: str
    stem_branch: Dict[str, Any]
    five_elements: Dict[str, int]
    yin_yang: Dict[str, int]
    major_luck_start_age: int
    major_luck_set: List[Dict[str, Any]]


