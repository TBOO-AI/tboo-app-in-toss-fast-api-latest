import calendar
import datetime
from functools import cached_property
from zoneinfo import ZoneInfo

from app.solar_term.models import SolarTerm, SolarTermKindChoices, SolarTermNameChoices


def sin_sal(name):
    """신살 이름을 함수에 저장하는 데코레이터"""

    def decorator(func):
        func.sin_sal = name
        return func

    return decorator


stem_list = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
branch_list = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

# stem_to_color = {
#     "甲": "green",
#     "乙": "green",
#     "丙": "red",
#     "丁": "red",
#     "戊": "yellow",
#     "己": "yellow",
#     "庚": "white",
#     "辛": "white",
#     "壬": "blue",
#     "癸": "blue",
# }
# branch_to_animal = {
#     "子": "rat",
#     "丑": "ox",
#     "寅": "tiger",
#     "卯": "rabbit",
#     "辰": "dragon",
#     "巳": "snake",
#     "午": "horse",
#     "未": "sheep",
#     "申": "monkey",
#     "酉": "rooster",
#     "戌": "dog",
#     "亥": "pig",
# }

stem_to_color = {
    "甲": "green",
    "乙": "green",
    "丙": "red",
    "丁": "red",
    "戊": "yellow",
    "己": "yellow",
    "庚": "white",
    "辛": "white",
    "壬": "blue",
    "癸": "blue",
}
branch_to_animal = {
    "子": "rat",
    "丑": "ox",
    "寅": "tiger",
    "卯": "rabbit",
    "辰": "dragon",
    "巳": "snake",
    "午": "horse",
    "未": "sheep",
    "申": "monkey",
    "酉": "rooster",
    "戌": "dog",
    "亥": "pig",
}

stem_ko_cn_map = {
    "갑": "甲",
    "을": "乙",
    "병": "丙",
    "정": "丁",
    "무": "戊",
    "기": "己",
    "경": "庚",
    "신": "辛",
    "임": "壬",
    "계": "癸",
}
branch_ko_cn_map = {
    "자": "子",
    "축": "丑",
    "인": "寅",
    "묘": "卯",
    "진": "辰",
    "사": "巳",
    "오": "午",
    "미": "未",
    "신": "申",
    "유": "酉",
    "술": "戌",
    "해": "亥",
}

# 월지: 절기 - 월지 매핑
jeolgi_to_branch = {
    "소한": "축",  # 12월 (축월)
    "입춘": "인",  # 1월 (인월)
    "경칩": "묘",  # 2월 (묘월)
    "청명": "진",  # 3월 (진월)
    "입하": "사",  # 4월 (사월)
    "망종": "오",  # 5월 (오월)
    "소서": "미",  # 6월 (미월)
    "입추": "신",  # 7월 (신월)
    "백로": "유",  # 8월 (유월)
    "한로": "술",  # 9월 (술월)
    "입동": "해",  # 10월 (해월)
    "대설": "자",  # 11월 (자월)
}
# 월간: 월간 계산 공식 (갑기년과 기갑년은 정월이 병인월부터 시작)
year_stem_to_first_month_stem = {
    "갑": "병",
    "기": "병",  # 갑기년 -> 정월이 병인
    "을": "무",
    "경": "무",  # 을경년 -> 정월이 무인
    "병": "경",
    "신": "경",  # 병신년 -> 정월이 경인
    "정": "임",
    "임": "임",  # 정임년 -> 정월이 임인
    "무": "갑",
    "계": "갑",  # 무계년 -> 정월이 갑인
}
# 시지: 시간대 - 시지 매핑
hour_to_branch = {
    23: "자",
    0: "자",  # 23시-01시 자시
    1: "축",
    2: "축",  # 01시-03시 축시
    3: "인",
    4: "인",  # 03시-05시 인시
    5: "묘",
    6: "묘",  # 05시-07시 묘시
    7: "진",
    8: "진",  # 07시-09시 진시
    9: "사",
    10: "사",  # 09시-11시 사시
    11: "오",
    12: "오",  # 11시-13시 오시
    13: "미",
    14: "미",  # 13시-15시 미시
    15: "신",
    16: "신",  # 15시-17시 신시
    17: "유",
    18: "유",  # 17시-19시 유시
    19: "술",
    20: "술",  # 19시-21시 술시
    21: "해",
    22: "해",  # 21시-23시 해시
}
# 시간: 일간 - 시간 매핑
day_stem_to_ja_stem = {
    "갑": "갑",
    "기": "갑",  # 갑기일 -> 자시가 갑자
    "을": "병",
    "경": "병",  # 을경일 -> 자시가 병자
    "병": "무",
    "신": "무",  # 병신일 -> 자시가 무자
    "정": "경",
    "임": "경",  # 정임일 -> 자시가 경자
    "무": "임",
    "계": "임",  # 무계일 -> 자시가 임자
}
# 간 - 오행 맵핑
stem_to_five_elements = {
    "갑": "목",
    "을": "목",
    "병": "화",
    "정": "화",
    "무": "토",
    "기": "토",
    "경": "금",
    "신": "금",
    "임": "수",
    "계": "수",
}
# 간 - 음양 맵핑
stem_to_yin_yang = {
    "갑": "양",
    "을": "음",
    "병": "양",
    "정": "음",
    "무": "양",
    "기": "음",
    "경": "양",
    "신": "음",
    "임": "양",
    "계": "음",
}
# 지 - 오행 맵핑
branch_to_five_elements = {
    "인": "목",
    "묘": "목",
    "사": "화",
    "오": "화",
    "진": "토",
    "술": "토",
    "축": "토",
    "미": "토",
    "신": "금",
    "유": "금",
    "해": "수",
    "자": "수",
}
# 지 - 음양 맵핑
branch_to_yin_yang = {
    "자": "양",
    "축": "음",
    "인": "양",
    "묘": "음",
    "진": "양",
    "사": "음",
    "오": "양",
    "미": "음",
    "신": "양",
    "유": "음",
    "술": "양",
    "해": "음",
}
# 지지의 주기(主氣) 매핑 - 지지를 간으로 변환
branch_main_stem = {
    "자": "계",
    "축": "기",
    "인": "갑",
    "묘": "을",
    "진": "무",
    "사": "병",
    "오": "정",
    "미": "기",
    "신": "경",
    "유": "신",
    "술": "무",
    "해": "임",
}
# 오행 관계 매핑
five_elements_relations = {
    "목": {"생": "화", "극": "토", "피생": "수", "피극": "금"},
    "화": {"생": "토", "극": "금", "피생": "목", "피극": "수"},
    "토": {"생": "금", "극": "수", "피생": "화", "피극": "목"},
    "금": {"생": "수", "극": "목", "피생": "토", "피극": "화"},
    "수": {"생": "목", "극": "화", "피생": "금", "피극": "토"},
}
# 지장간
hidden_stem_map = {
    "자": {"residual": {"name": "임", "value": 10}, "middle": None, "primary": {"name": "계", "value": 20}},
    "축": {
        "residual": {"name": "계", "value": 9},
        "middle": {"name": "신", "value": 3},
        "primary": {"name": "기", "value": 18},
    },
    "인": {
        "residual": {"name": "무", "value": 7},
        "middle": {"name": "병", "value": 7},
        "primary": {"name": "갑", "value": 16},
    },
    "묘": {"residual": {"name": "갑", "value": 10}, "middle": None, "primary": {"name": "을", "value": 20}},
    "진": {
        "residual": {"name": "을", "value": 9},
        "middle": {"name": "계", "value": 3},
        "primary": {"name": "무", "value": 18},
    },
    "사": {
        "residual": {"name": "무", "value": 7},
        "middle": {"name": "경", "value": 7},
        "primary": {"name": "병", "value": 16},
    },
    "오": {
        "residual": {"name": "병", "value": 10},
        "middle": {"name": "기", "value": 9},
        "primary": {"name": "정", "value": 11},
    },
    "미": {
        "residual": {"name": "정", "value": 9},
        "middle": {"name": "을", "value": 3},
        "primary": {"name": "기", "value": 18},
    },
    "신": {
        "residual": {"name": "무", "value": 7},
        "middle": {"name": "임", "value": 7},
        "primary": {"name": "경", "value": 16},
    },
    "유": {"residual": {"name": "경", "value": 10}, "middle": None, "primary": {"name": "신", "value": 20}},
    "술": {
        "residual": {"name": "신", "value": 9},
        "middle": {"name": "정", "value": 3},
        "primary": {"name": "무", "value": 18},
    },
    "해": {
        "residual": {"name": "무", "value": 7},
        "middle": {"name": "갑", "value": 7},
        "primary": {"name": "임", "value": 16},
    },
}
# 천간별 12운성 매핑
twelve_stage_map = {
    "갑": {
        "해": "장생",
        "자": "목욕",
        "축": "관대",
        "인": "건록",
        "묘": "제왕",
        "진": "쇠",
        "사": "병",
        "오": "사",
        "미": "묘",
        "신": "절",
        "유": "태",
        "술": "양",
    },
    "을": {
        "오": "장생",
        "사": "목욕",
        "진": "관대",
        "묘": "건록",
        "인": "제왕",
        "축": "쇠",
        "자": "병",
        "해": "사",
        "술": "묘",
        "유": "절",
        "신": "태",
        "미": "양",
    },
    "병": {
        "인": "장생",
        "묘": "목욕",
        "진": "관대",
        "사": "건록",
        "오": "제왕",
        "미": "쇠",
        "신": "병",
        "유": "사",
        "술": "묘",
        "해": "절",
        "자": "태",
        "축": "양",
    },
    "정": {
        "유": "장생",
        "신": "목욕",
        "미": "관대",
        "오": "건록",
        "사": "제왕",
        "진": "쇠",
        "묘": "병",
        "인": "사",
        "축": "묘",
        "자": "절",
        "해": "태",
        "술": "양",
    },
    "무": {
        "인": "장생",
        "묘": "목욕",
        "진": "관대",
        "사": "건록",
        "오": "제왕",
        "미": "쇠",
        "신": "병",
        "유": "사",
        "술": "묘",
        "해": "절",
        "자": "태",
        "축": "양",
    },
    "기": {
        "유": "장생",
        "신": "목욕",
        "미": "관대",
        "오": "건록",
        "사": "제왕",
        "진": "쇠",
        "묘": "병",
        "인": "사",
        "축": "묘",
        "자": "절",
        "해": "태",
        "술": "양",
    },
    "경": {
        "사": "장생",
        "오": "목욕",
        "미": "관대",
        "신": "건록",
        "유": "제왕",
        "술": "쇠",
        "해": "병",
        "자": "사",
        "축": "묘",
        "인": "절",
        "묘": "태",
        "진": "양",
    },
    "신": {
        "자": "장생",
        "해": "목욕",
        "술": "관대",
        "유": "건록",
        "신": "제왕",
        "미": "쇠",
        "오": "병",
        "사": "사",
        "진": "묘",
        "묘": "절",
        "인": "태",
        "축": "양",
    },
    "임": {
        "신": "장생",
        "유": "목욕",
        "술": "관대",
        "해": "건록",
        "자": "제왕",
        "축": "쇠",
        "인": "병",
        "묘": "사",
        "진": "묘",
        "사": "절",
        "오": "태",
        "미": "양",
    },
    "계": {
        "묘": "장생",
        "인": "목욕",
        "축": "관대",
        "자": "건록",
        "해": "제왕",
        "술": "쇠",
        "유": "병",
        "신": "사",
        "미": "묘",
        "오": "절",
        "사": "태",
        "진": "양",
    },
}

# 지지별 12신살 매핑 (일지 기준)
twelve_sin_sal_map = {
    "인오술": {
        "해": "겁살",
        "자": "재살",
        "축": "천살",
        "인": "지살",
        "묘": "연살",
        "진": "월살",
        "사": "망신살",
        "오": "장성살",
        "미": "반안살",
        "신": "역마살",
        "유": "육해살",
        "술": "화개살",
    },
    "신자진": {
        "사": "겁살",
        "오": "재살",
        "미": "천살",
        "신": "지살",
        "유": "연살",
        "술": "월살",
        "해": "망신살",
        "자": "장성살",
        "축": "반안살",
        "인": "역마살",
        "묘": "육해살",
        "진": "화개살",
    },
    "사유축": {
        "인": "겁살",
        "묘": "재살",
        "진": "천살",
        "사": "지살",
        "오": "연살",
        "미": "월살",
        "신": "망신살",
        "유": "장성살",
        "술": "반안살",
        "해": "역마살",
        "자": "육해살",
        "축": "화개살",
    },
    "해묘미": {
        "신": "겁살",
        "유": "재살",
        "술": "천살",
        "해": "지살",
        "자": "연살",
        "축": "월살",
        "인": "망신살",
        "묘": "장성살",
        "진": "반안살",
        "사": "역마살",
        "오": "육해살",
        "미": "화개살",
    },
}


class Saju:
    def __init__(self, birth, gender, birth_longitude):
        self._validate_year(birth)
        self.birth = birth
        self.gender = gender
        self.birth_longitude = round(birth_longitude)
        print("표준시: ", self.standard_longitude)
        print("출생지 경도: ", self.birth_longitude)
        print("경도조정: ", int(self.offset_minutes.total_seconds() / 60))
        print("기준시각", self.birth - self.birth.dst() + self.offset_minutes)
        print("사주: ")
        for k, v in self.stem_branch.items():
            print(k)
            print(v)
        print("대운 방향: ", "순행" if self.is_forward else "역행")
        print("대운: ")
        for ml in self.major_luck_set:
            print(ml)
        print("연운: ")
        for al in self.get_annual_luck_set(1997, 10):
            print(al)
        print("월운: ")
        for ml in self.get_monthly_luck_set(1997):
            print(ml)
        print("일진: ")
        for dp in self.get_daily_pillar_set(2024, 1):
            print(dp)

    def _validate_year(self, birth):
        start_at = datetime.datetime(year=1900, month=1, day=5, hour=8, minute=36, tzinfo=ZoneInfo("UTC"))
        end_at = datetime.datetime(year=2100, month=12, day=21, hour=19, minute=50, tzinfo=ZoneInfo("UTC"))
        if start_at > birth or birth > end_at:
            raise Exception("지원하지 않는 연도입니다.")

    @cached_property
    def standard_longitude(self):
        standard_offset = self.birth.utcoffset() - self.birth.dst()
        offset_hours = standard_offset.total_seconds() / 3600
        standard_longitude = offset_hours * 15
        return standard_longitude

    @cached_property
    def offset_minutes(self):
        return datetime.timedelta(minutes=(self.birth_longitude - self.standard_longitude) * 4)

    @cached_property
    def spti(self):
        return f"{self.sun_moon}{self.dominant_receptiveness}{self.feeling_thinking}{self.process_outcome}-{self.wealth_honor}"

    @cached_property
    def stem_branch(self):
        return {
            "hour": {
                "stem": {
                    "name": stem_ko_cn_map[self.hour_stem_branch[0]],
                    "five_elements": stem_to_five_elements[self.hour_stem_branch[0]],
                    "yin_yang": stem_to_yin_yang[self.hour_stem_branch[0]],
                    "ten_god": self._get_ten_god(self.hour_stem_branch[0]),
                    "sin_sal": self._get_sin_sal("hour_stem"),
                },
                "branch": {
                    "name": branch_ko_cn_map[self.hour_stem_branch[1]],
                    "five_elements": branch_to_five_elements[self.hour_stem_branch[1]],
                    "yin_yang": branch_to_yin_yang[self.hour_stem_branch[1]],
                    "ten_god": self._get_ten_god(branch_main_stem[self.hour_stem_branch[1]]),
                    "hidden_stem": self._get_hidden_stems(self.hour_stem_branch[1]),
                    "twelve_stage": self._get_twelve_stage(self.hour_stem_branch[1]),
                    "twelve_sin_sal": self._get_twelve_sin_sal(self.year_stem_branch[1], self.hour_stem_branch[1]),
                    "sin_sal": self._get_sin_sal("hour_branch"),
                },
            },
            "day": {
                "stem": {
                    "name": stem_ko_cn_map[self.day_stem_branch[0]],
                    "five_elements": stem_to_five_elements[self.day_stem_branch[0]],
                    "yin_yang": stem_to_yin_yang[self.day_stem_branch[0]],
                    "ten_god": self._get_ten_god(self.day_stem_branch[0]),
                    "sin_sal": self._get_sin_sal("day_stem"),
                },
                "branch": {
                    "name": branch_ko_cn_map[self.day_stem_branch[1]],
                    "five_elements": branch_to_five_elements[self.day_stem_branch[1]],
                    "yin_yang": branch_to_yin_yang[self.day_stem_branch[1]],
                    "ten_god": self._get_ten_god(branch_main_stem[self.day_stem_branch[1]]),
                    "hidden_stem": self._get_hidden_stems(self.day_stem_branch[1]),
                    "twelve_stage": self._get_twelve_stage(self.day_stem_branch[1]),
                    "twelve_sin_sal": self._get_twelve_sin_sal(self.year_stem_branch[1], self.day_stem_branch[1]),
                    "sin_sal": self._get_sin_sal("day_branch"),
                },
            },
            "month": {
                "stem": {
                    "name": stem_ko_cn_map[self.month_stem_branch[0]],
                    "five_elements": stem_to_five_elements[self.month_stem_branch[0]],
                    "yin_yang": stem_to_yin_yang[self.month_stem_branch[0]],
                    "ten_god": self._get_ten_god(self.month_stem_branch[0]),
                    "sin_sal": self._get_sin_sal("month_stem"),
                },
                "branch": {
                    "name": branch_ko_cn_map[self.month_stem_branch[1]],
                    "five_elements": branch_to_five_elements[self.month_stem_branch[1]],
                    "yin_yang": branch_to_yin_yang[self.month_stem_branch[1]],
                    "ten_god": self._get_ten_god(branch_main_stem[self.month_stem_branch[1]]),
                    "hidden_stem": self._get_hidden_stems(self.month_stem_branch[1]),
                    "twelve_stage": self._get_twelve_stage(self.month_stem_branch[1]),
                    "twelve_sin_sal": self._get_twelve_sin_sal(self.year_stem_branch[1], self.month_stem_branch[1]),
                    "sin_sal": self._get_sin_sal("month_branch"),
                },
            },
            "year": {
                "stem": {
                    "name": stem_ko_cn_map[self.year_stem_branch[0]],
                    "five_elements": stem_to_five_elements[self.year_stem_branch[0]],
                    "yin_yang": stem_to_yin_yang[self.year_stem_branch[0]],
                    "ten_god": self._get_ten_god(self.year_stem_branch[0]),
                    "sin_sal": self._get_sin_sal("year_stem"),
                },
                "branch": {
                    "name": branch_ko_cn_map[self.year_stem_branch[1]],
                    "five_elements": branch_to_five_elements[self.year_stem_branch[1]],
                    "yin_yang": branch_to_yin_yang[self.year_stem_branch[1]],
                    "ten_god": self._get_ten_god(branch_main_stem[self.year_stem_branch[1]]),
                    "hidden_stem": self._get_hidden_stems(self.year_stem_branch[1]),
                    "twelve_stage": self._get_twelve_stage(self.year_stem_branch[1]),
                    "twelve_sin_sal": self._get_twelve_sin_sal(self.day_stem_branch[1], self.year_stem_branch[1]),
                    "sin_sal": self._get_sin_sal("year_branch"),
                },
            },
        }

    @cached_property
    def year_stem_branch(self):
        solar_term = SolarTerm.objects.get(name=SolarTermNameChoices.IPCHUN, at__year=self.birth.year)
        birth_year = self.birth.year
        if solar_term.at >= self.birth:
            birth_year -= 1

        base_year = 1924  # 갑자년
        year_diff = birth_year - base_year

        stem_index = year_diff % 10
        branch_index = year_diff % 12

        return stem_list[stem_index] + branch_list[branch_index]

    @cached_property
    def month_stem_branch(self):
        """
        월주(月柱)를 구합니다. 절기를 기준으로 월이 바뀝니다.

        Returns:
            str: 월주 간지 (예: "정묘")
        """
        # 생일 이전의 가장 가까운 절기 찾기(표준시, 써머타임 적용)
        previous_jeolgi = (
            SolarTerm.objects.filter(at__lt=self.birth, kind=SolarTermKindChoices.JEOLGI).order_by("-at").first()
        )

        month_branch = jeolgi_to_branch[previous_jeolgi.name]
        if not month_branch:
            raise Exception(f"알 수 없는 절기: {previous_jeolgi.name}")

        # 월간(月干) 계산: 년간에 따라 결정
        year_stem = self.year_stem_branch[0]

        first_month_stem = year_stem_to_first_month_stem[year_stem]
        first_month_stem_index = stem_list.index(first_month_stem)

        # 월 지지에 따른 월간 계산 (인월=0, 묘월=1, ...)
        month_branch_index = branch_list.index(month_branch)
        # 인월부터 시작하므로 인월을 0으로 맞춤
        month_order = (month_branch_index - 2) % 12  # 인=0, 묘=1, 진=2, ...

        month_stem_index = (first_month_stem_index + month_order) % 10
        month_stem = stem_list[month_stem_index]

        return month_stem + month_branch

    @cached_property
    def day_stem_branch(self):
        base_date = datetime.date(1924, 2, 15)  # 갑자일
        birth = self.birth - self.birth.dst() + self.offset_minutes
        # 23시인 경우 다음날로 처리 (자시는 23시-01시이므로 23시는 다음날 자시로 계산)
        if birth.hour == 23:
            birth += datetime.timedelta(days=1)
        birth_date = birth.date()

        # 기준일로부터 경과 일수 계산
        days_diff = (birth_date - base_date).days

        # 60갑자 순환으로 일주 계산
        stem_index = days_diff % 10
        branch_index = days_diff % 12

        return stem_list[stem_index] + branch_list[branch_index]

    @cached_property
    def hour_stem_branch(self):
        """
        시주(時柱)를 구합니다. 일간과 시간에 따라 결정됩니다.

        Returns:
            str: 시주 간지 (예: "갑자")
        """
        # 시간에 따른 지지 결정 (2시간씩, 써머타임 조정)
        hour = (self.birth - self.birth.dst() + self.offset_minutes).hour

        hour_branch = hour_to_branch[hour]

        # 일간에 따른 시간의 천간 계산
        day_stem = self.day_stem_branch[0]

        ja_stem = day_stem_to_ja_stem[day_stem]
        ja_stem_index = stem_list.index(ja_stem)

        # 시지에 따른 시간 계산 (자시=0, 축시=1, ...)
        hour_branch_index = branch_list.index(hour_branch)

        # 시간의 천간 계산
        hour_stem_index = (ja_stem_index + hour_branch_index) % 10
        hour_stem = stem_list[hour_stem_index]

        return hour_stem + hour_branch

    @cached_property
    def five_elements(self):
        """
        사주팔자의 오행 분포를 계산합니다.

        Returns:
            dict: 오행별 개수
            {"목": 2, "화": 1, "토": 3, "금": 1, "수": 1}
        """

        # 카운트 초기화
        five_elements_count = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}

        # 사주팔자 각 자리별 오행과 음양 계산
        for i in range(0, 8, 2):  # 0, 2, 4, 6 (시주, 일주, 월주, 년주)
            stem = self.stem_branch[i]  # 천간
            branch = self.stem_branch[i + 1]  # 지지

            # 천간 오행 및 음양 추가
            if stem in stem_to_five_elements:
                five_elements_count[stem_to_five_elements[stem]] += 1

            # 지지 오행 및 음양 추가
            if branch in branch_to_five_elements:
                five_elements_count[branch_to_five_elements[branch]] += 1

        return five_elements_count

    @cached_property
    def yin_yang(self):
        """
        사주팔자의 음양 분포를 계산합니다.

        Returns:
            dict: 오행별 개수
            {"음": 2, "양": 1}
        """

        # 카운트 초기화
        yin_yang_count = {"양": 0, "음": 0}

        # 사주팔자 각 자리별 오행과 음양 계산
        for i in range(0, 8, 2):  # 0, 2, 4, 6 (시주, 일주, 월주, 년주)
            stem = self.stem_branch[i]  # 천간
            branch = self.stem_branch[i + 1]  # 지지

            # 천간 오행 및 음양 추가
            if stem in stem_to_five_elements:
                yin_yang_count[stem_to_yin_yang[stem]] += 1

            # 지지 오행 및 음양 추가
            if branch in branch_to_five_elements:
                yin_yang_count[branch_to_yin_yang[branch]] += 1

        return yin_yang_count

    @cached_property
    def sun_moon(self):
        """
        일간의 음양에 따른 S/M 분류를 반환합니다.
        丁巳일 경우 예외적으로 S를 반환하고, 나머지는 천간의 음양에 따라 양간=S, 음간=M를 반환합니다.

        Returns:
            str: "S" 또는 "M"
        """
        day_stem = self.day_stem_branch[0]
        day_branch = self.day_stem_branch[1]

        if day_stem == "정" and day_branch == "사":
            return "S"

        if stem_to_yin_yang[day_stem] == "양":
            return "S"
        else:
            return "M"

    @cached_property
    def dominant_receptiveness(self):
        """
        일간과 월지 조합에 따른 D/R 분류를 반환합니다.

        Returns:
            str: "D" 또는 "R"
        """
        day_stem = self.day_stem_branch[0]
        month_branch = self.month_stem_branch[1]

        # 일간과 월지 조합에 따른 J/P 매핑 테이블
        dr_mapping = {
            "갑": {
                "인": "D",
                "묘": "D",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "D",
                "유": "D",
                "술": "D",
                "해": "R",
                "자": "R",
                "축": "D",
            },
            "을": {
                "인": "D",
                "묘": "D",
                "진": "R",
                "사": "R",
                "오": "R",
                "미": "R",
                "신": "R",
                "유": "R",
                "술": "R",
                "해": "R",
                "자": "R",
                "축": "R",
            },
            "병": {
                "인": "D",
                "묘": "D",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "R",
                "유": "R",
                "술": "D",
                "해": "R",
                "자": "R",
                "축": "D",
            },
            "정": {
                "인": "R",
                "묘": "R",
                "진": "R",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "R",
                "유": "R",
                "술": "R",
                "해": "R",
                "자": "R",
                "축": "R",
            },
            "무": {
                "인": "R",
                "묘": "R",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "D",
                "유": "D",
                "술": "D",
                "해": "R",
                "자": "R",
                "축": "D",
            },
            "기": {
                "인": "R",
                "묘": "R",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "R",
                "유": "R",
                "술": "D",
                "해": "R",
                "자": "R",
                "축": "D",
            },
            "경": {
                "인": "D",
                "묘": "D",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "R",
                "신": "D",
                "유": "D",
                "술": "D",
                "해": "D",
                "자": "D",
                "축": "D",
            },
            "신": {
                "인": "D",
                "묘": "D",
                "진": "R",
                "사": "R",
                "오": "R",
                "미": "R",
                "신": "D",
                "유": "D",
                "술": "D",
                "해": "D",
                "자": "D",
                "축": "D",
            },
            "임": {
                "인": "D",
                "묘": "D",
                "진": "D",
                "사": "D",
                "오": "D",
                "미": "D",
                "신": "D",
                "유": "R",
                "술": "D",
                "해": "D",
                "자": "D",
                "축": "D",
            },
            "계": {
                "인": "R",
                "묘": "R",
                "진": "R",
                "사": "R",
                "오": "R",
                "미": "R",
                "신": "R",
                "유": "R",
                "술": "R",
                "해": "D",
                "자": "D",
                "축": "R",
            },
        }

        return dr_mapping[day_stem][month_branch]

    @cached_property
    def feeling_thinking(self):
        """
        일간과 월지 조합에 따른 F/T 분류를 반환합니다.

        Returns:
            str: "F" 또는 "T"
        """
        day_stem = self.day_stem_branch[0]
        month_branch = self.month_stem_branch[1]

        # 일간과 월지 조합에 따른 F/T 매핑 테이블
        ft_mapping = {
            "갑": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "F",
            },
            "을": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "병": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "정": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "무": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "기": {
                "인": "F",
                "묘": "F",
                "진": "F",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "F",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "경": {
                "인": "T",
                "묘": "T",
                "진": "T",
                "사": "T",
                "오": "T",
                "미": "T",
                "신": "T",
                "유": "T",
                "술": "T",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "신": {
                "인": "T",
                "묘": "T",
                "진": "T",
                "사": "T",
                "오": "T",
                "미": "T",
                "신": "T",
                "유": "T",
                "술": "T",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "임": {
                "인": "F",
                "묘": "F",
                "진": "T",
                "사": "F",
                "오": "F",
                "미": "T",
                "신": "T",
                "유": "T",
                "술": "T",
                "해": "T",
                "자": "T",
                "축": "T",
            },
            "계": {
                "인": "F",
                "묘": "F",
                "진": "T",
                "사": "F",
                "오": "F",
                "미": "F",
                "신": "T",
                "유": "T",
                "술": "T",
                "해": "T",
                "자": "T",
                "축": "T",
            },
        }

        return ft_mapping[day_stem][month_branch]

    @cached_property
    def process_outcome(self):
        """
        일간과 월지 조합에 따른 P/O 분류를 반환합니다.

        Returns:
            str: "P" 또는 "O"
        """
        day_stem = self.day_stem_branch[0]
        month_branch = self.month_stem_branch[1]

        # 일간과 월지 조합에 따른 W/H 매핑 테이블
        po_mapping = {
            "갑": {
                "인": "O",
                "묘": "O",
                "진": "O",
                "사": "P",
                "오": "P",
                "미": "O",
                "신": "O",
                "유": "O",
                "술": "O",
                "해": "P",
                "자": "P",
                "축": "O",
            },
            "을": {
                "인": "O",
                "묘": "O",
                "진": "O",
                "사": "P",
                "오": "P",
                "미": "O",
                "신": "O",
                "유": "O",
                "술": "O",
                "해": "P",
                "자": "P",
                "축": "O",
            },
            "병": {
                "인": "P",
                "묘": "P",
                "진": "P",
                "사": "O",
                "오": "O",
                "미": "P",
                "신": "O",
                "유": "O",
                "술": "P",
                "해": "O",
                "자": "O",
                "축": "P",
            },
            "정": {
                "인": "P",
                "묘": "P",
                "진": "P",
                "사": "O",
                "오": "O",
                "미": "P",
                "신": "O",
                "유": "O",
                "술": "P",
                "해": "O",
                "자": "O",
                "축": "P",
            },
            "무": {
                "인": "O",
                "묘": "O",
                "진": "O",
                "사": "P",
                "오": "P",
                "미": "O",
                "신": "P",
                "유": "P",
                "술": "O",
                "해": "O",
                "자": "O",
                "축": "O",
            },
            "기": {
                "인": "O",
                "묘": "O",
                "진": "O",
                "사": "P",
                "오": "P",
                "미": "O",
                "신": "P",
                "유": "P",
                "술": "O",
                "해": "O",
                "자": "O",
                "축": "O",
            },
            "경": {
                "인": "O",
                "묘": "O",
                "진": "P",
                "사": "O",
                "오": "O",
                "미": "P",
                "신": "O",
                "유": "O",
                "술": "P",
                "해": "P",
                "자": "P",
                "축": "P",
            },
            "신": {
                "인": "O",
                "묘": "O",
                "진": "P",
                "사": "O",
                "오": "O",
                "미": "P",
                "신": "O",
                "유": "O",
                "술": "P",
                "해": "P",
                "자": "P",
                "축": "P",
            },
            "임": {
                "인": "P",
                "묘": "P",
                "진": "O",
                "사": "O",
                "오": "O",
                "미": "O",
                "신": "P",
                "유": "P",
                "술": "O",
                "해": "O",
                "자": "O",
                "축": "O",
            },
            "계": {
                "인": "P",
                "묘": "P",
                "진": "O",
                "사": "O",
                "오": "O",
                "미": "O",
                "신": "P",
                "유": "P",
                "술": "O",
                "해": "O",
                "자": "O",
                "축": "O",
            },
        }

        return po_mapping[day_stem][month_branch]

    @cached_property
    def wealth_honor(self):
        """
        일간과 월지 조합에 따른 W/H 분류를 반환합니다.

        Returns:
            str: "W" 또는 "H"
        """
        day_stem = self.day_stem_branch[0]
        month_branch = self.month_stem_branch[1]

        # 일간과 월지 조합에 따른 W/H 매핑 테이블
        wh_mapping = {
            "갑": {
                "인": "W",
                "묘": "W",
                "진": "W",
                "사": "W",
                "오": "W",
                "미": "W",
                "신": "H",
                "유": "H",
                "술": "W",
                "해": "H",
                "자": "H",
                "축": "W",
            },
            "을": {
                "인": "W",
                "묘": "W",
                "진": "W",
                "사": "W",
                "오": "W",
                "미": "W",
                "신": "H",
                "유": "H",
                "술": "W",
                "해": "H",
                "자": "H",
                "축": "W",
            },
            "병": {
                "인": "H",
                "묘": "H",
                "진": "W",
                "사": "W",
                "오": "W",
                "미": "W",
                "신": "W",
                "유": "W",
                "술": "W",
                "해": "H",
                "자": "H",
                "축": "W",
            },
            "정": {
                "인": "H",
                "묘": "H",
                "진": "W",
                "사": "W",
                "오": "W",
                "미": "W",
                "신": "W",
                "유": "W",
                "술": "W",
                "해": "H",
                "자": "H",
                "축": "W",
            },
            "무": {
                "인": "H",
                "묘": "H",
                "진": "W",
                "사": "W",
                "오": "W",
                "미": "W",
                "신": "W",
                "유": "W",
                "술": "W",
                "해": "W",
                "자": "W",
                "축": "W",
            },
            "기": {
                "인": "H",
                "묘": "H",
                "진": "W",
                "사": "H",
                "오": "H",
                "미": "W",
                "신": "W",
                "유": "W",
                "술": "W",
                "해": "W",
                "자": "W",
                "축": "W",
            },
            "경": {
                "인": "W",
                "묘": "W",
                "진": "H",
                "사": "H",
                "오": "H",
                "미": "H",
                "신": "W",
                "유": "W",
                "술": "H",
                "해": "W",
                "자": "W",
                "축": "H",
            },
            "신": {
                "인": "W",
                "묘": "W",
                "진": "H",
                "사": "H",
                "오": "H",
                "미": "H",
                "신": "W",
                "유": "W",
                "술": "H",
                "해": "W",
                "자": "W",
                "축": "H",
            },
            "임": {
                "인": "W",
                "묘": "W",
                "진": "H",
                "사": "W",
                "오": "W",
                "미": "H",
                "신": "W",
                "유": "W",
                "술": "H",
                "해": "W",
                "자": "W",
                "축": "H",
            },
            "계": {
                "인": "W",
                "묘": "W",
                "진": "H",
                "사": "W",
                "오": "W",
                "미": "H",
                "신": "W",
                "유": "W",
                "술": "H",
                "해": "W",
                "자": "W",
                "축": "H",
            },
        }

        return wh_mapping[day_stem][month_branch]

    @cached_property
    def is_forward(self):
        year_stem = self.year_stem_branch[0]

        # 양간: 갑, 병, 무, 경, 임 / 음간: 을, 정, 기, 신, 계
        yang_stem = ["갑", "병", "무", "경", "임"]
        is_yang_year = year_stem in yang_stem

        # 대운 진행 방향 결정
        is_male = self.gender == "male"
        return (is_yang_year and is_male) or (not is_yang_year and not is_male)

    @cached_property
    def major_luck_start_age(self):
        """
        대운 시작 나이를 계산합니다.

        양간년 남성, 음간년 여성: 순행 (다음 절기까지의 일수)
        음간년 남성, 양간년 여성: 역행 (이전 절기부터의 일수)

        Returns:
            int: 대운 시작 나이 (만 나이)
        """
        if self.is_forward:
            # 순행: 생일 이후 첫 번째 절기까지의 일수
            next_solar_term = (
                SolarTerm.objects.filter(at__gt=self.birth, kind=SolarTermKindChoices.JEOLGI).order_by("at").first()
            )

            days_diff = (next_solar_term.at.date() - self.birth.date()).days
        else:
            # 역행: 생일 이전 가장 가까운 절기부터의 일수
            prev_solar_term = (
                SolarTerm.objects.filter(at__lt=self.birth, kind=SolarTermKindChoices.JEOLGI).order_by("-at").first()
            )

            days_diff = (self.birth.date() - prev_solar_term.at.date()).days

        # 3일 = 1년으로 계산 (나머지는 개월 수로 계산)
        years = days_diff // 3
        months = (days_diff % 3) * 4

        # 전통적인 반올림: 6개월 이상이면 다음 년도로 올림
        if months >= 6:
            years += 1

        return years

    @cached_property
    def major_luck_set(self):
        """
        각 대운 나이별 대운 간지를 구합니다.

        Returns:
            list: 대운 간지 목록 (예: [{"age": 3, "stem": {"name": "무진", "ten_god": "..."}, "branch": ...}, ...])
        """

        major_luck_list = []
        ages = []
        for i in range(10):
            ages.append(self.major_luck_start_age + (i * 10))

        for i, age in enumerate(ages):
            if self.is_forward:
                # 순행: 월주에서 다음 간지들
                if i == 0:
                    # 첫 번째 대운은 월주의 다음 간지
                    current_stem = self._next_stem(self.month_stem_branch[0])
                    current_branch = self._next_branch(self.month_stem_branch[1])
                else:
                    # 이후 대운들은 순차적으로 다음 간지
                    current_stem = self._next_stem(major_luck_list[i - 1]["stem"]["name"])
                    current_branch = self._next_branch(major_luck_list[i - 1]["branch"]["name"])
            else:
                # 역행: 월주에서 이전 간지들
                if i == 0:
                    # 첫 번째 대운은 월주의 이전 간지
                    current_stem = self._prev_stem(self.month_stem_branch[0])
                    current_branch = self._prev_branch(self.month_stem_branch[1])
                else:
                    # 이후 대운들은 순차적으로 이전 간지
                    current_stem = self._prev_stem(major_luck_list[i - 1]["stem"]["name"])
                    current_branch = self._prev_branch(major_luck_list[i - 1]["branch"]["name"])

            major_luck_list.append(
                {
                    "age": age,
                    "stem": {
                        "name": current_stem,
                        "five_elements": stem_to_five_elements[current_stem],
                        "yin_yang": stem_to_yin_yang[current_stem],
                        "ten_god": self._get_ten_god(current_stem),
                    },
                    "branch": {
                        "name": current_branch,
                        "five_elements": branch_to_five_elements[current_branch],
                        "yin_yang": branch_to_yin_yang[current_branch],
                        "ten_god": self._get_ten_god(branch_main_stem[current_branch]),
                        "twelve_stage": self._get_twelve_stage(current_branch),
                        "twelve_sin_sal": self._get_twelve_sin_sal(self.day_stem_branch[1], current_branch),
                    },
                }
            )

        return major_luck_list

    def get_annual_luck_set(self, start_year, limit=10):
        """
        연운(年運)을 계산합니다. 각 연도별 연간 간지를 구합니다.

        Returns:
            list: 연운 간지 목록 (예: [{"year": 2024, "stem": {"name": "갑", "ten_god": "..."}, "branch": {"name": "진", "ten_god": "...", "twelve_stage": "..."}}, ...])
        """
        annual_luck_list = []

        # 향후 20년간의 연운 계산
        for i in range(limit):
            target_year = start_year + i

            # 해당 연도의 간지 계산 (1924년 갑자년 기준)
            base_year = 1924  # 갑자년
            year_diff = target_year - base_year

            stem_index = year_diff % 10
            branch_index = year_diff % 12

            year_stem = stem_list[stem_index]
            year_branch = branch_list[branch_index]

            annual_luck_list.append(
                {
                    "year": target_year,
                    "stem": {
                        "name": year_stem,
                        "five_elements": stem_to_five_elements[year_stem],
                        "yin_yang": stem_to_yin_yang[year_stem],
                        "ten_god": self._get_ten_god(year_stem),
                    },
                    "branch": {
                        "name": year_branch,
                        "five_elements": branch_to_five_elements[year_branch],
                        "yin_yang": branch_to_yin_yang[year_branch],
                        "ten_god": self._get_ten_god(branch_main_stem[year_branch]),
                        "twelve_stage": self._get_twelve_stage(year_branch),
                        "twelve_sin_sal": self._get_twelve_sin_sal(self.day_stem_branch[1], self.day_stem_branch[1]),
                    },
                }
            )

        return annual_luck_list

    def get_monthly_luck_set(self, year):
        """
        월운(月運)을 계산합니다. 특정 연도의 절기 기준 월운 간지를 구합니다.

        Args:
            year (int): 연도

        Returns:
            list: 월운 간지 목록 (예: [{"jeolgi": "입춘", "start_date": "2024-02-04", "stem": {"name": "병", "ten_god": "..."}, "branch": {"name": "인", "ten_god": "...", "twelve_stage": "..."}}, ...])
        """
        monthly_luck_list = []

        # 해당 연도의 년간 구하기
        base_year = 1924  # 갑자년
        year_diff = year - base_year
        year_stem_index = year_diff % 10
        year_stem = stem_list[year_stem_index]

        # 년간에 따른 정월(인월)의 월간 구하기
        first_month_stem = year_stem_to_first_month_stem[year_stem]
        first_month_stem_index = stem_list.index(first_month_stem)

        # 절기별 월운 계산
        for i, (jeolgi, month_branch) in enumerate(jeolgi_to_branch.items()):
            # 월간 계산 (인월=0부터 시작)
            month_branch_index = branch_list.index(month_branch)
            month_order = (month_branch_index - 2) % 12  # 인=0, 묘=1, 진=2, ...

            month_stem_index = (first_month_stem_index + month_order) % 10
            month_stem = stem_list[month_stem_index]

            monthly_luck_list.append(
                {
                    "month": i + 1,
                    "stem": {
                        "name": month_stem,
                        "five_elements": stem_to_five_elements[month_stem],
                        "yin_yang": stem_to_yin_yang[month_stem],
                        "ten_god": self._get_ten_god(month_stem),
                    },
                    "branch": {
                        "name": month_branch,
                        "five_elements": branch_to_five_elements[month_branch],
                        "yin_yang": branch_to_yin_yang[month_branch],
                        "ten_god": self._get_ten_god(branch_main_stem[month_branch]),
                        "twelve_stage": self._get_twelve_stage(month_branch),
                        "twelve_sin_sal": self._get_twelve_sin_sal(self.day_stem_branch[1], month_branch),
                    },
                }
            )

        return monthly_luck_list

    def get_daily_pillar_set(self, year, month):
        """
        일진 달력을 생성합니다. 특정 연월의 모든 날짜에 대한 일진 간지를 구합니다.

        Args:
            year (int): 연도
            month (int): 월 (1-12)

        Returns:
            list: 일진 달력 목록 (예: [{"day": 1, "date": "2024-01-01", "stem": "갑", "branch": "자", "stem_branch": "갑자"}, ...])
        """

        daily_calendar = []

        # 해당 월의 마지막 날 구하기
        last_day = calendar.monthrange(year, month)[1]

        # 기준일 (1924년 2월 15일 갑자일)
        base_date = datetime.date(1924, 2, 15)

        for day in range(1, last_day + 1):
            target_date = datetime.date(year, month, day)

            # 기준일로부터 경과 일수 계산
            days_diff = (target_date - base_date).days

            # 60갑자 순환으로 일진 계산
            stem_index = days_diff % 10
            branch_index = days_diff % 12

            day_stem = stem_list[stem_index]
            day_branch = branch_list[branch_index]

            daily_calendar.append(
                {
                    "day": day,
                    "date": target_date.strftime("%Y-%m-%d"),
                    "stem": {
                        "name": day_stem,
                        "five_elements": stem_to_five_elements[day_stem],
                        "yin_yang": stem_to_yin_yang[day_stem],
                        "ten_god": self._get_ten_god(day_stem),
                    },
                    "branch": {
                        "name": day_branch,
                        "five_elements": branch_to_five_elements[day_branch],
                        "yin_yang": branch_to_yin_yang[day_branch],
                        "ten_god": self._get_ten_god(branch_main_stem[day_branch]),
                        "twelve_stage": self._get_twelve_stage(day_branch),
                        "twelve_sin_sal": self._get_twelve_sin_sal(self.day_stem_branch[1], day_branch),
                    },
                }
            )

        return daily_calendar

    @staticmethod
    def _prev_stem(stem):
        stem_index = (stem_list.index(stem) - 1) % 10
        return stem_list[stem_index]

    @staticmethod
    def _next_stem(stem):
        stem_index = (stem_list.index(stem) + 1) % 10
        return stem_list[stem_index]

    @staticmethod
    def _prev_branch(branch):
        branch_index = (branch_list.index(branch) - 1) % 12
        return branch_list[branch_index]

    @staticmethod
    def _next_branch(branch):
        branch_index = (branch_list.index(branch) + 1) % 12
        return branch_list[branch_index]

    def _get_target(self, kind):
        if kind == "hour_stem":
            return self.hour_stem_branch[0]
        if kind == "hour_branch":
            return self.hour_stem_branch[1]
        if kind == "day_stem":
            return self.day_stem_branch[0]
        if kind == "day_branch":
            return self.day_stem_branch[1]
        if kind == "month_stem":
            return self.month_stem_branch[0]
        if kind == "month_branch":
            return self.month_stem_branch[1]
        if kind == "year_stem":
            return self.year_stem_branch[0]
        if kind == "year_branch":
            return self.year_stem_branch[1]
        return None

    def _get_ten_god(self, target_stem):
        """
        일간과 다른 간지를 비교하여 십성을 구합니다.

        Args:
            target_stem (str): 비교할 간지 (예: "을")

        Returns:
            str: 십성 (예: "겁재")
        """

        day_five_elements = stem_to_five_elements[self.day_stem_branch[0]]
        day_yin_yang = stem_to_yin_yang[self.day_stem_branch[0]]
        target_five_elements = stem_to_five_elements[target_stem]
        target_yin_yang = stem_to_yin_yang[target_stem]

        # 같은 오행인 경우
        if day_five_elements == target_five_elements:
            if day_yin_yang == target_yin_yang:
                return "비견"  # 같은 음양
            else:
                return "겁재"  # 다른 음양

        # 일간이 생하는 오행 (식상)
        elif target_five_elements == five_elements_relations[day_five_elements]["생"]:
            if day_yin_yang == target_yin_yang:
                return "식신"  # 같은 음양
            else:
                return "상관"  # 다른 음양

        # 일간을 생하는 오행 (인성)
        elif target_five_elements == five_elements_relations[day_five_elements]["피생"]:
            if day_yin_yang == target_yin_yang:
                return "편인"  # 같은 음양
            else:
                return "정인"  # 다른 음양

        # 일간이 극하는 오행 (재성)
        elif target_five_elements == five_elements_relations[day_five_elements]["극"]:
            if day_yin_yang == target_yin_yang:
                return "편재"  # 같은 음양
            else:
                return "정재"  # 다른 음양

        # 일간을 극하는 오행 (관성)
        elif target_five_elements == five_elements_relations[day_five_elements]["피극"]:
            if day_yin_yang == target_yin_yang:
                return "편관"  # 같은 음양 (칠살)
            else:
                return "정관"  # 다른 음양

        return "알 수 없음"

    def _get_hidden_stems(self, target_branch):
        return hidden_stem_map[target_branch]

    def _get_twelve_stage(self, target_branch):
        """
        일간과 지지를 비교하여 12운성을 구합니다.

        Args:
            target_branch (str): 지지 (예: "자")

        Returns:
            str: 12운성 (예: "장생")
        """
        # 천간별 12운성 매핑
        return twelve_stage_map[self.day_stem_branch[0]][target_branch]

    def _get_twelve_sin_sal(self, from_branch, target_branch):
        """
        일지와 연지, 연지와 월지, 일지, 시지
        일지와 대상 지지를 비교하여 12신살을 구합니다.

        Args:
            target_branch (str): 대상 지지

        Returns:
            str: 12신살 (예: "역마", "도화", "공망") 또는 None
        """
        for group, mapping in twelve_sin_sal_map.items():
            if from_branch in group:
                return mapping[target_branch]
        return None

    def _get_sin_sal(self, kind):
        # sin_sal 속성을 가진 모든 메소드를 자동으로 찾기
        sin_sal_functions = []

        # 클래스의 모든 메소드를 검사 (인스턴스가 아닌 클래스에서)
        for attr_name in dir(self.__class__):
            if attr_name.startswith("_get_"):
                method = getattr(self.__class__, attr_name)
                if hasattr(method, "sin_sal"):
                    # 인스턴스 메소드로 바인딩
                    bound_method = getattr(self, attr_name)
                    sin_sal_functions.append(bound_method)

        return [func.sin_sal for func in sin_sal_functions if func(kind)]

    @sin_sal("천을귀인")
    def _get_heavenly_noble(self, kind):
        """
        천을귀인을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        day_stem = self.day_stem_branch[0]
        target = self._get_target(kind)

        # 천을귀인 매핑
        heavenly_noble_map = {
            "갑": ["축", "미"],
            "을": ["자", "신"],
            "병": ["해", "유"],
            "정": ["해", "유"],
            "무": ["축", "미"],
            "기": ["자", "신"],
            "경": ["축", "미"],
            "신": ["인", "오"],
            "임": ["묘", "사"],
            "계": ["인", "오"],
        }

        return target in heavenly_noble_map[day_stem]

    @sin_sal("천덕귀인")
    def _get_heavenly_virtue(self, kind):
        """
        천덕귀인을 구합니다.
        """
        if kind == "month_branch":
            return False

        month_branch = self.month_stem_branch[1]
        target = self._get_target(kind)

        # 천덕귀인 매핑 (월지별)
        heavenly_virtue_map = {
            "자": "사",
            "축": "경",
            "인": "정",
            "묘": "신",
            "진": "임",
            "사": "신",
            "오": "해",
            "미": "갑",
            "신": "계",
            "유": "인",
            "술": "병",
            "해": "을",
        }

        return target == heavenly_virtue_map[month_branch]

    @sin_sal("월덕귀인")
    def _get_monthly_virtue(self, kind):
        """
        월덕귀인을 구합니다.
        """
        if not kind.endswith("stem"):
            return False

        month_branch = self.month_stem_branch[1]
        target = self._get_target(kind)

        # 월덕귀인 매핑 (월지별 해당하는 천간)
        monthly_virtue_map = {
            "자": "임",  # 자월 → 임수
            "축": "경",  # 축월 → 경금
            "인": "병",  # 인월 → 병화
            "묘": "갑",  # 묘월 → 갑목
            "진": "임",  # 진월 → 임수
            "사": "경",  # 사월 → 경금
            "오": "병",  # 오월 → 병화
            "미": "갑",  # 미월 → 갑목
            "신": "임",  # 신월 → 임수
            "유": "경",  # 유월 → 경금
            "술": "병",  # 술월 → 병화
            "해": "갑",  # 해월 → 갑목
        }

        return target == monthly_virtue_map[month_branch]

    @sin_sal("월공귀인")
    def _get_monthly_kong(self, kind):
        """
        월공귀인을 구합니다.
        """
        if not kind.endswith("stem"):
            return False

        month_branch = self.month_stem_branch[1]
        target = self._get_target(kind)

        # 월공귀인 매핑 (월지별 해당하는 천간)
        monthly_kong_map = {
            "자": "병",  # 자월 → 병화
            "축": "갑",  # 축월 → 갑목
            "인": "임",  # 인월 → 임수
            "묘": "경",  # 묘월 → 경금
            "진": "병",  # 진월 → 병화
            "사": "갑",  # 사월 → 갑목
            "오": "임",  # 오월 → 임수
            "미": "경",  # 미월 → 경금
            "신": "병",  # 신월 → 병화
            "유": "갑",  # 유월 → 갑목
            "술": "임",  # 술월 → 임수
            "해": "경",  # 해월 → 경금
        }

        return target == monthly_kong_map[month_branch]

    @sin_sal("문창귀인")
    def _get_moon_chang(self, kind):
        """
        문창귀인을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        day_stem = self.day_stem_branch[0]
        target = self._get_target(kind)

        # 문창귀인 매핑 (일간별 해당하는 지지)
        moon_chang_map = {
            "갑": "사",  # 갑목 → 사화
            "을": "오",  # 을목 → 오화
            "병": "신",  # 병화 → 신금
            "정": "유",  # 정화 → 유금
            "무": "신",  # 무토 → 신금 (화토동법)
            "기": "유",  # 기토 → 유금 (화토동법)
            "경": "해",  # 경금 → 해수
            "신": "자",  # 신금 → 자수
            "임": "인",  # 임수 → 인목
            "계": "묘",  # 계수 → 묘목
        }

        return target == moon_chang_map[day_stem]

    @sin_sal("천의귀인")
    def _get_heavenly_doctor(self, kind):
        """
        천의귀인을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        month_branch = self.month_stem_branch[1]
        target = self._get_target(kind)

        # 천의귀인 매핑 (월지별 해당하는 지지)
        heavenly_doctor_map = {
            "자": "해",  # 자월 → 해지
            "축": "자",  # 축월 → 자지
            "인": "축",  # 인월 → 축지
            "묘": "인",  # 묘월 → 인지
            "진": "묘",  # 진월 → 묘지
            "사": "진",  # 사월 → 진지
            "오": "사",  # 오월 → 사지
            "미": "오",  # 미월 → 오지
            "신": "미",  # 신월 → 미지
            "유": "신",  # 유월 → 신지
            "술": "유",  # 술월 → 유지
            "해": "술",  # 해월 → 술지
        }

        return target == heavenly_doctor_map[month_branch]

    @sin_sal("암록귀인")
    def _get_hidden_fortune(self, kind):
        """
        암록귀인을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        day_stem = self.day_stem_branch[0]
        target = self._get_target(kind)

        # 암록귀인 매핑 (일간별 해당하는 지지)
        hidden_fortune_map = {
            "갑": "해",  # 갑목 → 해지
            "을": "술",  # 을목 → 술지
            "병": "신",  # 병화 → 신지
            "정": "미",  # 정화 → 미지
            "무": "신",  # 무토 → 신지 (화토동법)
            "기": "미",  # 기토 → 미지 (화토동법)
            "경": "사",  # 경금 → 사지
            "신": "진",  # 신금 → 진지
            "임": "인",  # 임수 → 인지
            "계": "축",  # 계수 → 축지
        }

        return target == hidden_fortune_map[day_stem]

    @sin_sal("학당귀인")
    def _get_academic_hall(self, kind):
        """
        학당귀인을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)
        day_stem = self.day_stem_branch[0]

        academic_hall_map = {
            "갑": "사",
            "을": "오",
            "병": "인",
            "정": "유",
            "무": "인",
            "기": "유",
            "경": "사",
            "신": "자",
            "임": "신",
            "계": "묘",
        }

        return academic_hall_map[day_stem] == target

    @sin_sal("천의성")
    def _get_heavenly_fortress(self, kind):
        """
        천의성을 구합니다.
        """
        if not kind.endswith("branch") or kind == "month_branch":
            return False

        target = self._get_target(kind)
        month_branch = self.month_stem_branch[1]

        heavenly_fortress_map = {
            "자": "해",
            "축": "자",
            "인": "축",
            "묘": "인",
            "진": "묘",
            "사": "진",
            "오": "사",
            "미": "오",
            "신": "미",
            "유": "신",
            "술": "유",
            "해": "술",
        }

        return heavenly_fortress_map[month_branch] == target

    @sin_sal("역마살")
    def _get_post_horse(self, kind):
        """
        역마살을 구합니다.
        삼합 기준으로 판단합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)

        # 역마살 매핑 (삼합별 역마살 해당 지지)
        post_horse_map = {
            "사": ["해", "묘", "미"],  # 목국 삼합 → 사화 역마살
            "신": ["인", "오", "술"],  # 화국 삼합 → 신금 역마살
            "해": ["사", "유", "축"],  # 금국 삼합 → 해수 역마살
            "인": ["신", "자", "진"],  # 수국 삼합 → 인목 역마살
        }

        # 역마살이 될 수 있는 지지인지 확인 (사, 신, 해, 인만 가능)
        if target not in post_horse_map:
            return False

        # 모든 지지 수집 (자기 자신 제외)
        all_branches = []
        if kind != "year_branch":
            all_branches.append(self.year_stem_branch[1])
        if kind != "month_branch":
            all_branches.append(self.month_stem_branch[1])
        if kind != "day_branch":
            all_branches.append(self.day_stem_branch[1])
        if kind != "hour_branch":
            all_branches.append(self.hour_stem_branch[1])

        return any(branch in post_horse_map[target] for branch in all_branches)

    @sin_sal("도화살")
    def _get_peach_blossom(self, kind):
        """
        도화살을 구합니다.
        삼합 기준으로 판단합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)

        # 도화살 맵핑
        peach_blossom_map = {
            "자": ["해", "묘", "미"],
            "묘": ["인", "오", "술"],
            "오": ["사", "유", "축"],
            "유": ["신", "자", "진"],
        }

        # 도화살이 될 수 있는 지지인지 확인 (자, 묘, 오, 유만 가능)
        if target not in peach_blossom_map:
            return False

        # 모든 지지 수집 (자기 자신 제외)
        all_branches = []
        if kind != "year_branch":
            all_branches.append(self.year_stem_branch[1])
        if kind != "month_branch":
            all_branches.append(self.month_stem_branch[1])
        if kind != "day_branch":
            all_branches.append(self.day_stem_branch[1])
        if kind != "hour_branch":
            all_branches.append(self.hour_stem_branch[1])

        return any(branch in peach_blossom_map[target] for branch in all_branches)

    @sin_sal("화개살")
    def _get_fire_canopy(self, kind):
        """
        화개살을 구합니다.
        삼합 기준으로 판단합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)

        # 화개살 매핑 (삼합별 화개살 해당 지지)
        fire_canopy_map = {
            "미": ["해", "묘", "미"],  # 목국 삼합 → 미토 화개살
            "술": ["인", "오", "술"],  # 화국 삼합 → 술토 화개살
            "축": ["사", "유", "축"],  # 금국 삼합 → 축토 화개살
            "진": ["신", "자", "진"],  # 수국 삼합 → 진토 화개살
        }

        # 화개살이 될 수 있는 지지인지 확인 (미, 술, 축, 진만 가능)
        if target not in fire_canopy_map:
            return False

        # 모든 지지 수집 (자기 자신 제외)
        all_branches = []
        if kind != "year_branch":
            all_branches.append(self.year_stem_branch[1])
        if kind != "month_branch":
            all_branches.append(self.month_stem_branch[1])
        if kind != "day_branch":
            all_branches.append(self.day_stem_branch[1])
        if kind != "hour_branch":
            all_branches.append(self.hour_stem_branch[1])

        return any(branch in fire_canopy_map[target] for branch in all_branches)

    @sin_sal("귀문관살")
    def _get_ghost_gate(self, kind):
        """
        귀문관살을 구합니다.
        """
        if kind not in ["hour_branch", "month_branch"]:
            return False

        target = self._get_target(kind)
        day_branch = self.day_stem_branch[1]

        ghost_gate_map = {
            "진": "해",
            "해": "진",
            "오": "축",
            "축": "오",
            "사": "술",
            "술": "사",
            "묘": "신",
            "신": "묘",
            "인": "미",
            "미": "인",
            "자": "유",
            "유": "자",
        }

        if day_branch not in ghost_gate_map:
            return False

        return ghost_gate_map[target] == day_branch

    @sin_sal("원진살")
    def _get_hostile_opposition(self, kind):
        """
        원진살을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)

        hostile_opposition_map = {
            "진": "해",
            "해": "진",
            "오": "축",
            "축": "오",
            "사": "술",
            "술": "사",
            "묘": "신",
            "신": "묘",
            "인": "유",
            "유": "인",
            "자": "미",
            "미": "자",
        }

        if target not in hostile_opposition_map:
            return False

        # 모든 지지 수집 (자기 자신 제외)
        all_branches = []
        if kind != "year_branch":
            all_branches.append(self.year_stem_branch[1])
        if kind != "month_branch":
            all_branches.append(self.month_stem_branch[1])
        if kind != "day_branch":
            all_branches.append(self.day_stem_branch[1])
        if kind != "hour_branch":
            all_branches.append(self.hour_stem_branch[1])

        return any(hostile_opposition_map[target] == branch for branch in all_branches)

    @sin_sal("양인살")
    def _get_yang_blade(self, kind):
        """
        양인살을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        day_stem = self.day_stem_branch[0]
        if stem_to_yin_yang[day_stem] != "양":
            return False

        target = self._get_target(kind)
        yang_blade_map = {
            "갑": "모",
            "병": "오",
            "무": "오",
            "경": "유",
            "임": "자",
        }

        return yang_blade_map[day_stem] == target

    @sin_sal("괴강살")
    def _get_strange_strong(self, kind):
        """
        괴강살을 구합니다.
        """
        strange_strong_map = {"임진", "경진", "경술", "무술"}
        if self.day_stem_branch not in strange_strong_map:
            return False
        return getattr(self, f"{kind.split('_')[0]}_stem_branch") in strange_strong_map

    @sin_sal("백호대살")
    def _get_white_tiger_great(self, kind):
        """
        백호대살을 구합니다.
        """
        white_tiger_great_map = {"갑진", "을미", "병술", "정축", "무진", "임술", "계축"}
        if self.day_stem_branch not in white_tiger_great_map:
            return False
        return getattr(self, f"{kind.split('_')[0]}_stem_branch") in white_tiger_great_map

    @sin_sal("공망살")
    def _get_empty_void(self, kind):
        """
        공망살을 구합니다.
        60갑자를 10개씩 6그룹으로 나누어 각 그룹별 공망지가 결정됩니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)
        day_stem, day_branch = self.day_stem_branch

        # 60갑자 그룹별 공망지 매핑
        # 갑자~계유 = 술해 공망
        group1 = [
            ("갑", "자"),
            ("을", "축"),
            ("병", "인"),
            ("정", "묘"),
            ("무", "진"),
            ("기", "사"),
            ("경", "오"),
            ("신", "미"),
            ("임", "신"),
            ("계", "유"),
        ]

        # 갑술~계미 = 신유 공망
        group2 = [
            ("갑", "술"),
            ("을", "해"),
            ("병", "자"),
            ("정", "축"),
            ("무", "인"),
            ("기", "묘"),
            ("경", "진"),
            ("신", "사"),
            ("임", "오"),
            ("계", "미"),
        ]

        # 갑신~계사 = 오미 공망
        group3 = [
            ("갑", "신"),
            ("을", "유"),
            ("병", "술"),
            ("정", "해"),
            ("무", "자"),
            ("기", "축"),
            ("경", "인"),
            ("신", "묘"),
            ("임", "진"),
            ("계", "사"),
        ]

        # 갑오~계묘 = 진사 공망
        group4 = [
            ("갑", "오"),
            ("을", "미"),
            ("병", "신"),
            ("정", "유"),
            ("무", "술"),
            ("기", "해"),
            ("경", "자"),
            ("신", "축"),
            ("임", "인"),
            ("계", "묘"),
        ]

        # 갑진~계축 = 인묘 공망
        group5 = [
            ("갑", "진"),
            ("을", "사"),
            ("병", "오"),
            ("정", "미"),
            ("무", "신"),
            ("기", "유"),
            ("경", "술"),
            ("신", "해"),
            ("임", "자"),
            ("계", "축"),
        ]

        # 갑인~계해 = 자축 공망
        group6 = [
            ("갑", "인"),
            ("을", "묘"),
            ("병", "진"),
            ("정", "사"),
            ("무", "오"),
            ("기", "미"),
            ("경", "신"),
            ("신", "유"),
            ("임", "술"),
            ("계", "해"),
        ]

        day_pillar = (day_stem, day_branch)

        if day_pillar in group1:
            return target in ["술", "해"]
        elif day_pillar in group2:
            return target in ["신", "유"]
        elif day_pillar in group3:
            return target in ["오", "미"]
        elif day_pillar in group4:
            return target in ["진", "사"]
        elif day_pillar in group5:
            return target in ["인", "묘"]
        elif day_pillar in group6:
            return target in ["자", "축"]

        return False

    @sin_sal("천라지망살")
    def _get_heaven_net_earth_snare(self, kind):
        """
        천라지망살을 구합니다.
        """
        if not kind.endswith("branch"):
            return False

        target = self._get_target(kind)

        heaven_net_earth_snare_map = {
            "술": "해",
            "해": "술",
            "진": "사",
            "사": "진",
        }

        if target not in heaven_net_earth_snare_map:
            return False

        # 모든 지지 수집 (자기 자신 제외)
        all_branches = []
        if kind != "year_branch":
            all_branches.append(self.year_stem_branch[1])
        if kind != "month_branch":
            all_branches.append(self.month_stem_branch[1])
        if kind != "day_branch":
            all_branches.append(self.day_stem_branch[1])
        if kind != "hour_branch":
            all_branches.append(self.hour_stem_branch[1])

        return any(heaven_net_earth_snare_map[target] == branch for branch in all_branches)

    @sin_sal("현침살")
    def _get_hanging_needle(self, kind):
        """
        현침살을 구합니다.
        """

        target = self._get_target(kind)
        hanging_needle_map = {"갑", "신", "신", "묘", "오", "미"}  # stem, branch 모두 신 존재

        return target in hanging_needle_map