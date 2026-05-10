import os
import json
import re
from google import genai
from google.genai import types

is_google=True

from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)
GEMINI_MODEL = getattr(settings, "gemini_model", "gemini-2.5-flash")

LLM_CALL_COUNT = 0

VALID_SIDO = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
]

VALID_KIND = ["개", "고양이"]

VALID_COLORS = [
    "갈색, 노란색, 흰색",
    "갈색",
    "검정색, 흰색",
    "흰색",
    "노란색, 흰색",
    "평행전체부분줄 무늬",
    "갈색, 검정색, 흰색",
    "검정색, 회색, 흰색",
    "검정색",
    "갈색, 노란색",
    "갈색, 흰색",
    "갈색, 검정색, 노란색, 회색, 흰색",
    "회색, 흰색",
    "갈색, 검정색",
    "고등어태비",
    "노란색, 주황색",
    "회색",
    "갈색, 검정색, 노란색",
    "갈색, 검정색, 노란색, 흰색",
    "검정색, 노란색",
    "삼색",
    "노란색",
    "검정색, 회색",
    "갈색, 회색",
    "카오스",
    "턱시도",
    "노란색, 주황색, 흰색",
    "호반색호랑이 무늬",
    "갈색, 회색, 흰색",
    "갈색, 검정색, 회색",
    "거북이",
    "검정색, 노란색, 흰색",
    "호피 무늬",
    "하얀 의 반점",
    "얼룩 무늬",
    "믹스",
    "호반 무늬",
    "노란색, 회색",
    "호구",
    "브린들"
]

BASE_COLORS = ["갈색", "검정색", "노란색", "주황색", "회색", "흰색"]

# 긴 표현을 먼저 치환하기 위해 길이 긴 순서로 정렬해서 쓰는 걸 권장
REGION_ALIASES = {
    "서울": [
        "서울특별시", "서울시", "서울"
    ],
    "부산": [
        "부산광역시", "부산시", "부산"
    ],
    "대구": [
        "대구광역시", "대구시", "대구"
    ],
    "인천": [
        "인천광역시", "인천시", "인천"
    ],
    "광주": [
        "광주광역시", "광주시", "광주"
    ],
    "대전": [
        "대전광역시", "대전시", "대전"
    ],
    "울산": [
        "울산광역시", "울산시", "울산"
    ],
    "세종": [
        "세종특별자치시", "세종시", "세종"
    ],
    "경기": [
        "경기도", "경기"
    ],
    "강원": [
        "강원특별자치도", "강원도", "강원"
    ],
    "충북": [
        "충청북도", "충북"
    ],
    "충남": [
        "충청남도", "충남"
    ],
    "전북": [
        "전북특별자치도", "전라북도", "전북"
    ],
    "전남": [
        "전라남도", "전남"
    ],
    "경북": [
        "경상북도", "경북"
    ],
    "경남": [
        "경상남도", "경남"
    ],
    "제주": [
        "제주특별자치도", "제주도", "제주"
    ],
}

# 도시/구/군/시 이름을 광역단위로 정규화
REGION_SUB_ALIASES = {
    "서울": [
        "강남", "강남구", "강동", "강동구", "강북", "강북구", "강서", "강서구",
        "관악", "관악구", "광진", "광진구", "구로", "구로구", "금천", "금천구",
        "노원", "노원구", "도봉", "도봉구", "동대문", "동대문구", "동작", "동작구",
        "마포", "마포구", "서대문", "서대문구", "서초", "서초구", "성동", "성동구",
        "성북", "성북구", "송파", "송파구", "양천", "양천구", "영등포", "영등포구",
        "용산", "용산구", "은평", "은평구", "종로", "종로구", "중구", "중랑", "중랑구"
    ],
    "부산": [
        "부산진구", "해운대", "해운대구", "수영구", "남구", "동래구", "사하구",
        "금정구", "사상구", "기장군", "서구", "중구", "영도구", "강서구", "북구",
        "연제구", "동구"
    ],
    "대구": [
        "수성구", "달서구", "달성군", "중구", "동구", "서구", "남구", "북구"
    ],
    "인천": [
        "연수구", "남동구", "부평구", "계양구", "서구", "중구", "동구", "미추홀구",
        "강화군", "옹진군"
    ],
    "광주": [
        "광산구", "북구", "서구", "남구", "동구"
    ],
    "대전": [
        "유성구", "서구", "중구", "동구", "대덕구"
    ],
    "울산": [
        "남구", "중구", "동구", "북구", "울주군"
    ],
    "세종": [
        "세종시", "세종"
    ],
    "경기": [
        "수원", "수원시", "성남", "성남시", "고양", "고양시", "용인", "용인시",
        "부천", "부천시", "안산", "안산시", "안양", "안양시", "남양주", "남양주시",
        "화성", "화성시", "평택", "평택시", "의정부", "의정부시", "시흥", "시흥시",
        "파주", "파주시", "김포", "김포시", "광명", "광명시", "광주", "광주시",
        "군포", "군포시", "하남", "하남시", "오산", "오산시", "이천", "이천시",
        "안성", "안성시", "구리", "구리시", "의왕", "의왕시", "포천", "포천시",
        "양주", "양주시", "동두천", "동두천시", "과천", "과천시", "가평", "가평군",
        "양평", "양평군", "여주", "여주시", "연천", "연천군"
    ],
    "강원": [
        "춘천", "춘천시", "원주", "원주시", "강릉", "강릉시", "동해", "동해시",
        "태백", "태백시", "속초", "속초시", "삼척", "삼척시", "홍천", "홍천군",
        "횡성", "횡성군", "영월", "영월군", "평창", "평창군", "정선", "정선군",
        "철원", "철원군", "화천", "화천군", "양구", "양구군", "인제", "인제군",
        "고성", "고성군", "양양", "양양군"
    ],
    "충북": [
        "청주", "청주시", "충주", "충주시", "제천", "제천시", "보은", "보은군",
        "옥천", "옥천군", "영동", "영동군", "증평", "증평군", "진천", "진천군",
        "괴산", "괴산군", "음성", "음성군", "단양", "단양군"
    ],
    "충남": [
        "천안", "천안시", "공주", "공주시", "보령", "보령시", "아산", "아산시",
        "서산", "서산시", "논산", "논산시", "계룡", "계룡시", "당진", "당진시",
        "금산", "금산군", "부여", "부여군", "서천", "서천군", "청양", "청양군",
        "홍성", "홍성군", "예산", "예산군", "태안", "태안군"
    ],
    "전북": [
        "전주", "전주시", "군산", "군산시", "익산", "익산시", "정읍", "정읍시",
        "남원", "남원시", "김제", "김제시", "완주", "완주군", "진안", "진안군",
        "무주", "무주군", "장수", "장수군", "임실", "임실군", "순창", "순창군",
        "고창", "고창군", "부안", "부안군"
    ],
    "전남": [
        "목포", "목포시", "여수", "여수시", "순천", "순천시", "나주", "나주시",
        "광양", "광양시", "담양", "담양군", "곡성", "곡성군", "구례", "구례군",
        "고흥", "고흥군", "보성", "보성군", "화순", "화순군", "장흥", "장흥군",
        "강진", "강진군", "해남", "해남군", "영암", "영암군", "무안", "무안군",
        "함평", "함평군", "영광", "영광군", "장성", "장성군", "완도", "완도군",
        "진도", "진도군", "신안", "신안군"
    ],
    "경북": [
        "포항", "포항시", "경주", "경주시", "김천", "김천시", "안동", "안동시",
        "구미", "구미시", "영주", "영주시", "영천", "영천시", "상주", "상주시",
        "문경", "문경시", "경산", "경산시", "군위", "군위군", "의성", "의성군",
        "청송", "청송군", "영양", "영양군", "영덕", "영덕군", "청도", "청도군",
        "고령", "고령군", "성주", "성주군", "칠곡", "칠곡군", "예천", "예천군",
        "봉화", "봉화군", "울진", "울진군", "울릉", "울릉군"
    ],
    "경남": [
        "창원", "창원시", "진주", "진주시", "통영", "통영시", "사천", "사천시",
        "김해", "김해시", "밀양", "밀양시", "거제", "거제시", "양산", "양산시",
        "의령", "의령군", "함안", "함안군", "창녕", "창녕군", "고성", "고성군",
        "남해", "남해군", "하동", "하동군", "산청", "산청군", "함양", "함양군",
        "거창", "거창군", "합천", "합천군"
    ],
    "제주": [
        "제주시", "서귀포", "서귀포시"
    ],
}

KIND_ALIASES = {
    "개": [
        "강아지", "멍멍이", "댕댕이", "견공", "반려견", "애견", "도그", "dog"
    ],
    "고양이": [
        "고양이", "냥이", "야옹이", "반려묘", "캣", "cat", "네코"
    ],
}

COLOR_ALIASES = {
    "흰색": [
        "흰색", "하얀색", "하양", "하얀", "화이트", "white", "백색", "새하얀",
        "흰", "하얗", "하얀 털", "흰 털", "백색 털", "흰색 털", "하얀빛"
    ],
    "검정색": [
        "검정색", "검은색", "까만색", "까만", "검정", "블랙", "black", "새까만",
        "검은", "흑색", "검은 털", "검정 털", "검정색 털", "까만 털", "검은빛", '까맣', "까만빛"
        ,"까만 빛", "까미"
    ],
    "갈색": [
        "갈색", "갈색빛", "브라운", "brown", "밤색", "갈돌", "초코색", "초콜릿색",
        "갈색 털", "갈 털", "갈색빛 털", "브라운 털", "밤색 털", "초코 털", "초콜릿 털",
        "갈색 계열", "갈색빛이 도는"
    ],
    "노란색": [
        "노란색", "노랑", "누런색", "누렁", "옐로우", "yellow", "치즈색",
        "노란", "누런", "노란 털", "누런 털", "노랑 털", "노란빛", "치즈빛", "치즈 털"
    ],
    "주황색": [
        "주황색", "주황", "오렌지", "orange", "귤색",
        "주황 털", "주황색 털", "오렌지 털", "주황빛", "귤빛"
    ],
    "회색": [
        "회색", "회색빛", "그레이", "gray", "grey", "잿빛",
        "회색 털", "회색빛 털", "그레이 털", "잿색", "잿빛 털", "회색 계열"
    ],
    "삼색": [
        "삼색", "삼색이", "트리컬러", "삼색무늬", "삼색 털", "삼색 고양이"
    ],
    "턱시도": [
        "턱시도", "턱시", "턱시냥", "턱시고양이", "턱시도 무늬", "턱시도 털"
    ],
    "카오스": [
        "카오스", "카오스무늬", "카오스 털", "카오스 색"
    ],
    "거북이": [
        "거북이", "토터셸", "tortoiseshell", "토티", "거북이 무늬", "토티 무늬"
    ],
    "고등어태비": [
        "고등어태비", "고등어", "태비", "고등어무늬", "고등어냥",
        "태비무늬", "고등어 태비", "고등어 줄무늬"
    ],
    "브린들": [
        "브린들", "brindle", "브린들무늬", "브린들 털"
    ],
    "호피 무늬": [
        "호피 무늬", "호피", "표범무늬", "호피 털", "호피무늬"
    ],
    "호반 무늬": [
        "호반 무늬", "호반", "호반냥", "호반무늬"
    ],
    "호반색호랑이 무늬": [
        "호반색호랑이 무늬", "호랑이무늬", "호랑이", "타이거", "tiger tabby",
        "호랑이 털", "호랑이 같은 무늬"
    ],
    "얼룩 무늬": [
        "얼룩 무늬", "얼룩", "점박이", "스팟", "spot",
        "얼룩털", "얼룩 무늬 털", "점박이 무늬"
    ],
    "평행전체부분줄 무늬": [
        "평행전체부분줄 무늬", "줄무늬", "스트라이프", "stripe", "줄무늬 전체",
        "줄 있는", "줄무늬 털", "줄이 있는 털"
    ],
    "하얀 의 반점": [
        "하얀 의 반점", "하얀반점", "흰반점", "백반점",
        "하얀 반점", "흰색 반점", "하얀 점", "흰 점"
    ],
    "호구": [
        "호구"
    ],
    "믹스": [
        "믹스", "믹스견", "믹스묘", "잡종", "혼종", "믹스 털"
    ],

    # 복합 색상
    "검정색, 흰색": [
        "검정 흰색", "검흰", "흑백", "블랙앤화이트", "검정색 흰색", "검은색 흰색",
        "검정과 흰색", "검은색과 흰색", "검정 흰", "검은 흰", "검정 흰 털", "검은 털 흰 털",
        "검정색과 흰 털", "검은 털과 흰 털", "블랙 화이트"
    ],
    "갈색, 흰색": [
        "갈흰", "갈색 흰색", "브라운 화이트",
        "갈색과 흰색", "갈색 흰", "갈색 흰 털", "갈 털 흰 털"
    ],
    "갈색, 검정색": [
        "갈검", "갈색 검정색",
        "갈색과 검정색", "갈색 검정", "갈 털 검은 털"
    ],
    "회색, 흰색": [
        "회흰", "회색 흰색", "그레이 화이트",
        "회색과 흰색", "회색 흰", "회색 흰 털", "회색 털 흰 털"
    ],
    "검정색, 회색": [
        "검회", "검정 회색", "검은색 회색",
        "검정색과 회색", "검은색과 회색", "검정 회색 털", "검은 털 회색 털"
    ],
    "검정색, 노란색": [
        "검노", "검정 노랑", "검정 노란색",
        "검정색과 노란색", "검은색과 노란색", "검정 노란 털"
    ],
    "노란색, 흰색": [
        "노흰", "노란 흰색", "치즈화이트", "치즈 흰색",
        "노란색과 흰색", "노란 흰", "노란 털 흰 털", "치즈와 흰색",
        "치즈", "치즈색", "치즈 털", "치즈냥이", "치즈냥", "치즈빛"
    ],
    "노란색, 주황색": [
        "노주", "노란 주황", "치즈오렌지",
        "노란색과 주황색", "노랑 주황", "노란 털 주황 털"
    ],
    "노란색, 회색": [
        "노회", "노란 회색",
        "노란색과 회색", "노란 털 회색 털"
    ],
    "갈색, 노란색": [
        "갈노", "갈색 노랑",
        "갈색과 노란색", "갈색 노란 털", "갈 털 누런 털"
    ],
    "갈색, 회색": [
        "갈회", "갈색 회색",
        "갈색과 회색", "갈색 회색 털"
    ],
    "갈색, 검정색, 흰색": [
        "갈검흰", "갈색 검정색 흰색",
        "갈색 검정색 흰색 털", "갈색과 검정색과 흰색"
    ],
    "검정색, 회색, 흰색": [
        "검회흰", "검정 회색 흰색",
        "검정 회색 흰 털", "검정색과 회색과 흰색"
    ],
    "갈색, 검정색, 노란색": [
        "갈검노", "갈색 검정 노랑",
        "갈색 검정 노란 털", "갈색과 검정색과 노란색"
    ],
    "갈색, 회색, 흰색": [
        "갈회흰", "갈색 회색 흰색",
        "갈색 회색 흰 털", "갈색과 회색과 흰색"
    ],
    "갈색, 검정색, 회색": [
        "갈검회", "갈색 검정 회색",
        "갈색 검정 회색 털", "갈색과 검정색과 회색"
    ],
    "검정색, 노란색, 흰색": [
        "검노흰", "검정 노랑 흰색",
        "검정 노란 흰 털", "검정색과 노란색과 흰색"
    ],
    "노란색, 주황색, 흰색": [
        "노주흰", "노란 주황 흰색",
        "노란 주황 흰 털", "노란색과 주황색과 흰색"
    ],
    "갈색, 노란색, 흰색": [
        "갈노흰", "갈색 노랑 흰색",
        "갈색 노란 흰 털", "갈색과 노란색과 흰색"
    ],
    "갈색, 검정색, 노란색, 흰색": [
        "갈검노흰",
        "갈색 검정 노란 흰 털", "갈색과 검정색과 노란색과 흰색"
    ],
    "갈색, 검정색, 노란색, 회색, 흰색": [
        "오색", "갈검노회흰",
        "다섯색", "오색 털", "갈색 검정 노란 회색 흰색"
    ],
}

def normalize_color_stems(text: str) -> str:
    patterns = [
        (r"까맣(?:고|은|은색|은 털|은빛)?", "검정색"),
        (r"검(?:고|은|은색|은 털|은빛)?", "검정색"),
        (r"하얗(?:고|은|은색|은 털|은빛)?", "흰색"),
        (r"흰(?:색| 털|빛)?", "흰색"),
        (r"노랗(?:고|은|은색|은 털|은빛)?", "노란색"),
        (r"누렇(?:고|은|은색|은 털|은빛)?", "노란색"),
        (r"갈(?:색|색의|색 털| 털)?", "갈색"),
        (r"주황(?:색|빛| 털)?", "주황색"),
        (r"회(?:색|색의|색 털|빛)?", "회색"),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)

    return text

def normalize_spaces(text: str) -> str:
    text = re.sub(r"[,\./|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# def replace_aliases(text: str, alias_map: dict) -> str:
#     all_pairs = []
#     for canonical, aliases in alias_map.items():
#         for alias in aliases:
#             all_pairs.append((alias, canonical))

#     all_pairs.sort(key=lambda x: len(x[0]), reverse=True)

#     for alias, canonical in all_pairs:
#         pattern = rf"(?<![가-힣A-Za-z0-9]){re.escape(alias)}(?![가-힣A-Za-z0-9])"
#         text = re.sub(pattern, canonical, text, flags=re.IGNORECASE)

#     return text

_COMPILED_ALIAS_CACHE = {}

def get_compiled_alias_patterns(alias_map_name: str, alias_map: dict):
    if alias_map_name in _COMPILED_ALIAS_CACHE:
        return _COMPILED_ALIAS_CACHE[alias_map_name]

    all_pairs = []

    for canonical, aliases in alias_map.items():
        for alias in aliases:
            all_pairs.append((alias, canonical))

    all_pairs.sort(key=lambda x: len(x[0]), reverse=True)

    compiled_patterns = []

    for alias, canonical in all_pairs:
        pattern = re.compile(
            rf"(?<![가-힣A-Za-z0-9]){re.escape(alias)}(?![가-힣A-Za-z0-9])",
            flags=re.IGNORECASE
        )
        compiled_patterns.append((pattern, canonical))

    _COMPILED_ALIAS_CACHE[alias_map_name] = compiled_patterns
    return compiled_patterns

def replace_aliases(text: str, alias_map: dict, alias_map_name: str) -> str:
    compiled_patterns = get_compiled_alias_patterns(alias_map_name, alias_map)

    for pattern, canonical in compiled_patterns:
        text = pattern.sub(canonical, text)

    return text

def normalize_region_text(text: str) -> str:
    text = replace_aliases(text, REGION_ALIASES, "REGION_ALIASES")
    text = replace_aliases(text, REGION_SUB_ALIASES, "REGION_SUB_ALIASES")
    return text

def normalize_kind_text(text: str) -> str:
    return replace_aliases(text, KIND_ALIASES, "KIND_ALIASES")

def normalize_color_text(text: str) -> str:
    return replace_aliases(text, COLOR_ALIASES, "COLOR_ALIASES")

def normalize_color_phrases(text: str) -> str:
    phrase_replacements = {
        " 털을 가진": " ",
        " 털 가진": " ",
        " 털의": " ",
        " 털": " ",
        " 색상": " ",
        " 컬러": " ",
        " 무늬를 가진": " ",
        " 무늬의": " ",
        " 섞인": " ",
        " 섞여 있는": " ",
        " 섞여있는": " ",
        " 가진": " ",
        "과": " ",
        "와": " ",
        "이랑": " ",
        "랑": " ",
        "하고": " ",
    }

    for old, new in phrase_replacements.items():
        text = text.replace(old, new)

    return normalize_spaces(text)

def normalize_user_text(text: str) -> str:
    text = text.strip()
    text = text.lower()

    # 특수문자/여러 공백 정리
    text = normalize_spaces(text)

    # 자주 나오는 조사/불필요 표현 단순화
    replacements = {
        "쪽에서": " ",
        "쪽에": " ",
        "근처에서": " ",
        "근처": " ",
        "지역에서": " ",
        "지역": " ",
        "사는": " ",
        "있는": " ",
        "보호중인": " ",
        "보호 중인": " ",
        "유기된": " ",
        "유기": " ",
        "찾아줘": " ",
        "찾아줘요": " ",
        "찾아주세요": " ",
        "보여줘": " ",
        "보여줘요": " ",
        "보여주세요": " ",
        "있어?": " ",
        "있나요": " ",
        "있니": " ",
        "조회해줘": " ",
        "검색해줘": " ",
        "과": " ",
        "와": " ",
        "이랑": " ",
        "랑": " ",
        "하고": " ",
        "섞인": " ",
        "섞여 있는": " ",
        "섞여있는": " ",
        "털": " ",
        "털을": " ",
        "털이": " ",
        "랑": " ",
        "하고": " ",
        "털": " ",
        "털을": " ",
        "털의": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = normalize_spaces(text)
    text = normalize_color_phrases(text)   # 있으면 먼저
    text = normalize_color_stems(text)     # 새로 추가
    #text = normalize_region_text(text)
    text = normalize_kind_text(text)
    text = normalize_color_text(text)
    text = normalize_spaces(text)
    
    return text

def detect_base_colors(text: str):
    found = []
    for color in BASE_COLORS:
        if color in text:
            found.append(color)
    return sorted(set(found))

def detect_composite_color_from_text(text: str):
    found = detect_base_colors(text)
    if not found:
        return None

    for valid_color in VALID_COLORS:
        parts = [p.strip() for p in valid_color.split(",")]
        # 무늬/단일명칭(턱시도, 삼색 등)은 제외하고 순수 색 조합만 비교
        if all(part in BASE_COLORS for part in parts):
            if sorted(parts) == found:
                return valid_color
    return None

def detect_color_from_text(text: str):
    # 1차: 복합 색상/패턴 alias 결과 우선
    sorted_colors = sorted(
        VALID_COLORS,
        key=lambda c: ("," not in c, -len(c))
    )

    for color in sorted_colors:
        if color in text:
            return color

    # 2차: base color 조합
    composite = detect_composite_color_from_text(text)
    if composite:
        return composite

    return None

def get_region(sido):
    region_mapping = {
        "서울": ["서울특별시"],
        "부산": ["부산광역시"],
        "대구": ["대구광역시"],
        "인천": ["인천광역시"],
        "광주": ["광주광역시"],
        "대전": ["대전광역시"],
        "울산": ["울산광역시"],
        "세종": ["세종특별자치시", "세종시"],
        "경기": ["경기도"],
        "강원": ["강원도", "강원특별자치도"],
        "충북": ["충청북도"],
        "충남": ["충청남도"],
        "전북": ["전라북도", "전북특별자치도"],
        "전남": ["전라남도"],
        "경북": ["경상북도"],
        "경남": ["경상남도"],
        "제주": ["제주특별자치도", "제주도"],
    }
    return region_mapping.get(sido)

def strip_korean_postposition(token: str) -> str:
    # 자주 붙는 조사/어미만 뒤에서 제거
    suffixes = [
        "에서", "으로", "에게", "한테", "까지", "부터", "처럼",
        "에", "은", "는", "이", "가", "을", "를", "도", "만", "쪽", "부근"
    ]

    for suffix in sorted(suffixes, key=len, reverse=True):
        if token.endswith(suffix) and len(token) > len(suffix):
            return token[:-len(suffix)]
    return token

AMBIGUOUS_REGION_ALIASES = {
    "중구", "서구", "남구", "북구", "동구", "강서구"
}

def tokenize_with_postposition_cleanup(text: str):
    tokens = text.split()
    results = []

    for idx, token in enumerate(tokens):
        stripped = strip_korean_postposition(token)
        results.append({
            "index": idx,
            "raw": token,
            "stripped": stripped
        })

    return results

def collect_region_evidence(text: str):
    """
    지역 관련 증거를 모두 수집한다.
    - direct_sido: 서울, 경기 같은 광역시도 직접 언급
    - sub_region_unique: 수원, 구미, 전주처럼 사실상 한 시도에만 연결되는 하위 지명
    - sub_region_ambiguous: 중구, 서구처럼 여러 시도에 걸칠 수 있는 지명
    """
    evidences = []

    token_infos = tokenize_with_postposition_cleanup(text)

    for token_info in token_infos:
        raw = token_info["raw"]
        stripped = token_info["stripped"]
        token_idx = token_info["index"]

        # 1) 광역시도 직접 매칭
        if stripped in VALID_SIDO:
            evidences.append({
                "entity": "region",
                "token": raw,
                "normalized": stripped,
                "token_index": token_idx,
                "matched_by": "direct_sido",
                "candidates": [stripped],
                "weight": 3,
                "ambiguous": False
            })
            continue

        # 2) REGION_ALIASES 직접 매칭 (서울시, 경기도 등)
        matched_sidos = []
        for sido, aliases in REGION_ALIASES.items():
            if stripped in aliases:
                matched_sidos.append(sido)

        if matched_sidos:
            unique_sidos = sorted(set(matched_sidos))
            evidences.append({
                "entity": "region",
                "token": raw,
                "normalized": stripped,
                "token_index": token_idx,
                "matched_by": "region_alias",
                "candidates": unique_sidos,
                "weight": 3 if len(unique_sidos) == 1 else 1,
                "ambiguous": len(unique_sidos) > 1
            })

        # 3) 하위 지역명 매칭
        matched_sidos = []
        for sido, aliases in REGION_SUB_ALIASES.items():
            if stripped in aliases:
                matched_sidos.append(sido)

        if matched_sidos:
            unique_sidos = sorted(set(matched_sidos))
            alias_ambiguous = (
                len(unique_sidos) > 1 or stripped in AMBIGUOUS_REGION_ALIASES
            )

            evidences.append({
                "entity": "region",
                "token": raw,
                "normalized": stripped,
                "token_index": token_idx,
                "matched_by": "sub_region",
                "candidates": unique_sidos,
                "weight": 2 if not alias_ambiguous and len(unique_sidos) == 1 else 0,
                "ambiguous": alias_ambiguous
            })

    return deduplicate_region_evidence(evidences)

def deduplicate_region_evidence(evidences):
    """
    같은 토큰/같은 normalized/같은 matched_by/같은 candidates 중복 제거
    """
    seen = set()
    deduped = []

    for ev in evidences:
        key = (
            ev["token_index"],
            ev["normalized"],
            ev["matched_by"],
            tuple(ev["candidates"])
        )
        if key not in seen:
            seen.add(key)
            deduped.append(ev)

    return deduped

def resolve_region_from_evidence(evidences):
    """
    evidence를 점수화해서 region을 결정한다.
    반환:
    {
        "sido": "경기" or None,
        "scores": {"경기": 5, "서울": 3},
        "ambiguous_evidence": [...],
        "used_evidence": [...]
    }
    """
    scores = {}
    ambiguous_evidence = []
    used_evidence = []

    # 같은 normalized surface가 같은 시도를 중복 가산하지 않도록 제어
    credited = set()

    for ev in evidences:
        if ev["ambiguous"] or len(ev["candidates"]) != 1:
            ambiguous_evidence.append(ev)
            continue

        sido = ev["candidates"][0]
        credit_key = (ev["normalized"], sido)

        if credit_key in credited:
            continue

        credited.add(credit_key)
        scores[sido] = scores.get(sido, 0) + ev["weight"]
        used_evidence.append(ev)

    if not scores:
        return {
            "sido": None,
            "scores": {},
            "ambiguous_evidence": ambiguous_evidence,
            "used_evidence": used_evidence
        }

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_sido, top_score = ranked[0]

    # 1위와 2위 차이가 충분할 때만 확정
    if len(ranked) == 1:
        final_sido = top_sido
    else:
        second_score = ranked[1][1]
        final_sido = top_sido if top_score >= second_score + 2 else None

    return {
        "sido": final_sido,
        "scores": scores,
        "ambiguous_evidence": ambiguous_evidence,
        "used_evidence": used_evidence
    }

def build_region_hint_from_resolution(resolution: dict):
    final_sido = resolution.get("sido")
    scores = resolution.get("scores", {})
    ambiguous_evidence = resolution.get("ambiguous_evidence", [])
    used_evidence = resolution.get("used_evidence", [])

    lines = []

    if final_sido:
        lines.append(f"룰기반 지역 확정 후보: {final_sido}")

    if scores:
        lines.append("지역 점수:")
        for sido, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {sido}: {score}")

    if used_evidence:
        lines.append("사용된 지역 증거:")
        for ev in used_evidence[:10]:
            lines.append(
                f"- token={ev['token']} normalized={ev['normalized']} -> {ev['candidates'][0]} ({ev['matched_by']})"
            )

    if ambiguous_evidence:
        lines.append("모호한 지역 증거:")
        for ev in ambiguous_evidence[:10]:
            cands = ", ".join(ev["candidates"])
            lines.append(
                f"- token={ev['token']} normalized={ev['normalized']} -> [{cands}] ({ev['matched_by']})"
            )

    if not lines:
        return "지역 참고 후보 없음"

    return "\n".join(lines)

def detect_sido_from_text(text: str):
    for sido in VALID_SIDO:
        if sido in text:
            return sido
    # 2차: 하위 지역명 직접 substring 탐지
    for sido, aliases in REGION_SUB_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            if alias in text:
                return sido

    # 3차: 토큰 단위 조사 제거 후 비교
    tokens = text.split()
    cleaned_tokens = [strip_korean_postposition(token) for token in tokens]

    for sido, aliases in REGION_SUB_ALIASES.items():
        for alias in aliases:
            if alias in cleaned_tokens:
                return sido

    return None

def get_region_candidates_from_text(text: str):
    candidates = []

    for sido, aliases in REGION_SUB_ALIASES.items():
        matched_aliases = []

        for alias in aliases:
            if alias in text:
                matched_aliases.append(alias)

        if matched_aliases:
            candidates.append({
                "sido": sido,
                "aliases": sorted(set(matched_aliases), key=len, reverse=True)
            })

    return candidates

def build_region_hint(text: str):
    candidates = get_region_candidates_from_text(text)

    if not candidates:
        return "지역 참고 후보 없음"

    lines = ["지역 참고 후보:"]
    for item in candidates:
        sido = item["sido"]
        aliases = ", ".join(item["aliases"][:5])  # 너무 길어지지 않게 상위 5개만
        lines.append(f"- {sido}: {aliases}")

    return "\n".join(lines)

def detect_kind_from_text(text: str):
    if re.search(r"(고양이|냥이|야옹이|반려묘|묘)", text):
        return "고양이"
    if re.search(r"(^|[^가-힣A-Za-z0-9])(개|강아지|멍멍이|댕댕이|반려견|애견|견공)([^가-힣A-Za-z0-9]|$)", text):
        return "개"
    return None


# =========================
# 세부종 후보/별칭
# =========================

DOG_COLUMNS = [
    "beagle","bichon_frise","border_collie","boston_bull","chihuahua","chow",
    "cocker_spaniel","dachshund","french_bulldog","german_shepherd",
    "golden_retriever","italian_greyhound","jindo_dog","labrador_retriever",
    "maltese_dog","papillon","pekinese","pomeranian","poodle","pug",
    "samoyed","schnauzer","shiba_inu","shih_tzu","siberian_husky",
    "welsh_corgi","yorkshire_terrier"
]

CAT_COLUMNS = [
    "abyssinian","american_shorthair","bengal","birman","bombay",
    "british_shorthair","cornish_rex","devon_rex","domestic","maine_coon",
    "munchkin","norwegian_forest_cat","persian","ragdoll","russian_blue",
    "scottish_fold","siamese","sphynx","turkish_angora","turkish_van"
]

VALID_BREEDS = DOG_COLUMNS + CAT_COLUMNS + ["other"]

BREED_ALIASES = {

# ================= DOG =================
"beagle": ["비글","beagle"],
"bichon_frise": ["비숑","비숑프리제","비숑 프리제","bichon frise"],
"border_collie": ["보더콜리","보더 콜리","border collie"],
"boston_bull": ["보스턴불","보스턴테리어","보스턴 테리어","boston terrier"],
"chihuahua": ["치와와","chihuahua"],
"chow": ["차우","차우차우","chow"],
"cocker_spaniel": ["코커스패니얼","코카스파니엘","cocker spaniel"],
"dachshund": ["닥스훈트","닥스","dachshund"],
"french_bulldog": ["프렌치불독","프렌치 불독","french bulldog"],
"german_shepherd": ["저먼셰퍼드","셰퍼드","german shepherd"],
"golden_retriever": ["골든리트리버","리트리버","golden retriever"],
"italian_greyhound": ["이탈리안그레이하운드","italian greyhound"],
"jindo_dog": ["진돗개","진도개","jindo"],
"labrador_retriever": ["라브라도리트리버","래브라도","labrador retriever"],
"maltese_dog": ["말티즈","maltese"],
"papillon": ["파피용","papillon"],
"pekinese": ["페키니즈","pekingese"],
"pomeranian": ["포메라니안","포메","pomeranian"],
"poodle": ["푸들","토이푸들","poodle"],
"pug": ["퍼그","pug"],
"samoyed": ["사모예드","samoyed"],
"schnauzer": ["슈나우저","schnauzer"],
"shiba_inu": ["시바견","시바이누","shiba"],
"shih_tzu": ["시츄","시추","shih tzu"],
"siberian_husky": ["허스키","husky"],
"welsh_corgi": ["웰시코기","코기","corgi"],
"yorkshire_terrier": ["요크셔테리어","요키","yorkshire terrier"],

# ================= CAT =================
"abyssinian": ["아비시니안","abyssinian"],
"american_shorthair": ["아메리칸숏헤어","american shorthair"],
"bengal": ["벵갈","bengal"],
"birman": ["버먼","birman"],
"bombay": ["봄베이","bombay"],
"british_shorthair": ["브리티시숏헤어","british shorthair"],
"cornish_rex": ["코니시렉스","cornish rex"],
"devon_rex": ["데본렉스","devon rex"],
"domestic": ["코숏","코리안숏헤어","집고양이","domestic"],
"maine_coon": ["메인쿤","maine coon"],
"munchkin": ["먼치킨","munchkin"],
"norwegian_forest_cat": ["노르웨이숲","노르웨이숲고양이","norwegian forest"],
"persian": ["페르시안","persian"],
"ragdoll": ["랙돌","ragdoll"],
"russian_blue": ["러시안블루","russian blue"],
"scottish_fold": ["스코티시폴드","scottish fold"],
"siamese": ["샴","샴고양이","siamese"],
"sphynx": ["스핑크스","sphynx"],
"turkish_angora": ["터키쉬앙고라","angora"],
"turkish_van": ["터키쉬반","turkish van"],
"other": ["믹스견", "믹스묘", "믹스", "잡종", "혼종", "기타", "others", "other"],
}

BREED_TO_KIND = {
    **{breed: "개" for breed in DOG_COLUMNS},
    **{breed: "고양이" for breed in CAT_COLUMNS},
    "other": None,
}

def detect_breed_from_text(text: str):
    lower_text = text.lower()

    for breed, aliases in BREED_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_text:
                return breed

    return None


def detect_colors_from_text(text: str):
    """
    사용자 문장에서 기준 6개 색상만 배열로 추출한다.
    예:
    - "갈색 닥스훈트" -> ["갈색"]
    - "검흰 강아지" -> ["검정색", "흰색"]
    - "브라운 화이트" -> ["갈색", "흰색"]
    """
    found = []

    # 1차: 정규화된 텍스트에 base color가 직접 포함된 경우
    for color in BASE_COLORS:
        if color in text:
            found.append(color)

    # 2차: COLOR_ALIASES 기반으로 복합 표현/별칭 처리
    lower_text = text.lower()

    for canonical, aliases in COLOR_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_text:
                parts = [p.strip() for p in canonical.split(",")]

                for part in parts:
                    if part in BASE_COLORS:
                        found.append(part)

    return sorted(set(found))


def safe_parse_json(content: str):
    content = (content or "").strip()

    if not content:
        return {}

    if content.startswith("```"):
        lines = content.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1 or end < start:
        return {}

    try:
        return json.loads(content[start:end + 1])
    except json.JSONDecodeError:
        return {}


def extract_filters_google(user_text: str, use_llm=True, verbose=True):
    """
    사용자 채팅 문장에서 4가지 값만 추출한다.

    반환:
    {
        "sido": "경기" or None,
        "kind": "개" or "고양이" or None,
        "breed": "dachshund" or None,
        "colors": ["갈색", "흰색"],
        "normalized_text": "...",
        "source": "rule" or "rule+llm",
        "region_debug": {...}
    }
    """
    normalized_text = normalize_user_text(user_text)

    region_evidences = collect_region_evidence(user_text)
    region_resolution = resolve_region_from_evidence(region_evidences)

    rule_sido = region_resolution["sido"]
    rule_kind = detect_kind_from_text(normalized_text) or detect_kind_from_text(user_text)
    rule_breed = detect_breed_from_text(normalized_text) or detect_breed_from_text(user_text)
    rule_colors = detect_colors_from_text(normalized_text)

    # 세부종이 개 품종이면 kind는 개로 보정
    if rule_breed:
        rule_kind = BREED_TO_KIND.get(rule_breed)

    rule_result = {
        "sido": rule_sido,
        "kind": rule_kind,
        "breed": rule_breed,
        "colors": rule_colors
    }

    if verbose:
        print("===== 룰 기반 추출 =====")
        print("원문:", user_text)
        print("정규화:", normalized_text)
        print(json.dumps(rule_result, ensure_ascii=False, indent=2))
        print()

    # 룰 결과가 충분하면 LLM 호출하지 않음
    # 지역은 없을 수도 있으므로 sido 없음 자체는 LLM 호출 사유로 보지 않는다.
    needs_llm = (
        use_llm and (
            # 종/세부종/색상 중 사용자가 뭔가 말했는데 룰이 놓쳤을 가능성이 있는 경우
            (not rule_kind and not rule_breed)
            or ("색" in user_text and not rule_colors)
            or ("털" in user_text and not rule_colors)
            or bool(region_resolution.get("ambiguous_evidence"))
        )
    )

    if not needs_llm:
        return {
            **rule_result,
            "normalized_text": normalized_text,
            "source": "rule",
            "region_debug": region_resolution
        }

    llm_result = extract_filters_with_gemini_v2(
        normalized_text=normalized_text,
        original_text=user_text,
        region_resolution=region_resolution,
        rule_result=rule_result
    )

    final_breed = rule_breed or llm_result.get("breed")
    final_kind = rule_kind or llm_result.get("kind")

    if rule_breed:
        rule_kind = BREED_TO_KIND.get(rule_breed)

    return {
        "sido": rule_sido or llm_result.get("sido"),
        "kind": final_kind,
        "breed": final_breed,
        "colors": rule_colors or llm_result.get("colors") or [],
        "normalized_text": normalized_text,
        "source": "rule+llm",
        "region_debug": region_resolution,
        "breed_before_llm": rule_breed,
        "origin": user_text
    }


def extract_filters_with_gemini_v2(
    normalized_text: str,
    original_text: str,
    region_resolution=None,
    rule_result=None
):
    global LLM_CALL_COUNT

    if region_resolution is None:
        region_hint = build_region_hint(normalized_text)
    else:
        region_hint = build_region_hint_from_resolution(region_resolution)

    LLM_CALL_COUNT += 1

    system_prompt = f"""
너는 유기동물 검색 조건 추출기다.

사용자 문장에서 아래 4개 값을 추출한다.

- sido: 지역. 없으면 null.
- kind: "개" 또는 "고양이". 없으면 null.
- breed: 세부종. 없으면 null.
- colors: 색상 배열. 없으면 [].

반드시 후보 중에서만 선택한다.

sido 후보:
{VALID_SIDO}

kind 후보:
{VALID_KIND}

breed 후보:
{VALID_BREEDS}

color 후보:
{BASE_COLORS}

지역 판단 참고:
{region_hint}

중요: 설명 문장, 마크다운, 코드블록을 절대 출력하지 말고 JSON 객체 하나만 출력한다.

규칙:
1. 반드시 JSON만 출력한다.
2. 룰 결과가 사용자 문장과 일치하면 유지한다.
3. 룰 결과가 누락되었거나 명백히 틀리면 수정한다.
4. 닥스훈트, 푸들, 치와와, 웰시코기, 비글, 셰퍼드 같은 세부종이 있으면 kind는 "개"로 본다.
5. "강아지", "댕댕이", "멍멍이", "반려견"은 kind="개"다.
6. "고양이", "냥이", "야옹이", "반려묘"는 kind="고양이"다.
7. 사용자가 세부종을 말하지 않으면 breed=null이다.
8. 색상은 여러 개 가능하다.
9. "갈색 흰색", "갈흰", "브라운 화이트"는 colors=["갈색","흰색"]이다.
10. "하얀색", "하얀", "화이트"는 "흰색"이다.
11. "까만색", "검은색", "블랙"은 "검정색"이다.
12. "브라운", "초코색", "밤색"은 "갈색"이다.
13. "치즈색", "노란색", "누런색"은 "노란색"이다.
14. "그레이", "잿빛"은 "회색"이다.
15. "오렌지", "귤색"은 "주황색"이다.
16. 지역은 하위 지역명을 광역 시도로 변환한다.
17. 지역이 없으면 sido=null이다.
18. 모호한 지역명은 확실한 근거가 없으면 null로 둔다.
19. 사용자가 세부종을 말했는데 breed 후보에 정확히 없으면, 의미상 가장 가까운 후보를 선택한다.
20. 단, 후보 중 유사한 품종이 전혀 없거나 믹스/잡종/기타 의미이면 breed="other"를 선택한다.
21. 예:
- "말라뮤트"는 후보에 없으므로 가장 가까운 "siberian_husky"로 선택한다.
- "시고르자브종", "믹스견", "잡종", "혼종"은 breed="other"로 선택한다.
- "불독"은 후보 중 가장 가까운 "french_bulldog"로 선택한다.
- "리트리버"는 후보 중 "golden_retriever" 또는 "labrador_retriever" 중 문맥상 더 가까운 것을 선택한다. 문맥이 없으면 null 또는 other가 아니라 더 일반적으로 많이 쓰이는 "golden_retriever"를 선택한다.
22. breed가 "other"이고 kind가 없으면 문맥에 따라 "개" 또는 "고양이"를 판단한다. "믹스견"이면 kind="개", "믹스묘"면 kind="고양이"다.
"""

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sido": {
                "anyOf": [
                    {"type": "string", "enum": VALID_SIDO},
                    {"type": "null"}
                ]
            },
            "kind": {
                "anyOf": [
                    {"type": "string", "enum": VALID_KIND},
                    {"type": "null"}
                ]
            },
            "breed": {
                "anyOf": [
                    {"type": "string", "enum": VALID_BREEDS},
                    {"type": "null"}
                ]
            },
            "colors": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": BASE_COLORS
                }
            }
        },
        "required": ["sido", "kind", "breed", "colors"]
    }

    payload = {
        "original_text": original_text,
        "normalized_text": normalized_text,
        "rule_result": rule_result,
        "region_resolution": region_resolution
    }

    user_prompt = json.dumps(payload, ensure_ascii=False)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=schema,
                temperature=0,
                max_output_tokens=512,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except TypeError:
        # google-genai SDK 버전에 따라 response_json_schema 대신 response_schema를 쓰는 경우가 있다.
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0,
                max_output_tokens=512,
            ),
        )

    data = safe_parse_json(response.text)

    sido = data.get("sido")
    kind = data.get("kind")
    breed = data.get("breed")
    colors = data.get("colors") or []

    if sido not in VALID_SIDO:
        sido = None

    if kind not in VALID_KIND:
        kind = None

    if breed not in VALID_BREEDS:
        breed = None

    colors = [c for c in colors if c in BASE_COLORS]

    if breed and not kind:
        kind = BREED_TO_KIND.get(breed)

    return {
        "sido": sido,
        "kind": kind,
        "breed": breed,
        "colors": sorted(set(colors))
    }


if __name__ == "__main__":
    while True:
        user_text = input("검색어를 입력하세요. 종료하려면 q 입력: ").strip()

        if user_text.lower() in ["q", "quit", "exit"]:
            break

        result = extract_filters_google(
            user_text,
            use_llm=True,
            verbose=True
        )

        print("===== 최종 추출 결과 =====")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"LLM 호출 횟수: {LLM_CALL_COUNT}")
        print()
