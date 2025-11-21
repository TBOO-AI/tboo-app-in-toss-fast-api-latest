from fastapi import APIRouter

from api.v1.saju import Saju
from schemas.saju import SajuRequest, SajuResponse


router = APIRouter(prefix="/saju", tags=["saju"])


@router.post("/", response_model=SajuResponse)
def calculate_saju(payload: SajuRequest) -> SajuResponse:
    """
    사주 계산 API

    요청으로 받은 출생 시각/성별/경도를 기반으로 사주 전체 정보를 계산합니다.
    """
    saju = Saju(
        birth=payload.birth,
        gender=payload.gender,
        birth_longitude=payload.birth_longitude,
    )

    return SajuResponse(
        spti=saju.spti,
        stem_branch=saju.stem_branch,
        five_elements=saju.five_elements,
        yin_yang=saju.yin_yang,
        major_luck_start_age=saju.major_luck_start_age,
        major_luck_set=saju.major_luck_set,
    )


