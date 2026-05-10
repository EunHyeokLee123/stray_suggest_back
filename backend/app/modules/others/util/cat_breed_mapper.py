"""
cat_breed_mapper.py

한국어/영어 고양이 품종 입력을 표준 영어 품종명으로 매핑합니다.

예:
    match_cat_breed("아비시니안") -> "Abyssinian"
    match_cat_breed("메인쿤") -> "Maine Coon"
    match_cat_breed("랙돌") -> "Ragdoll Cats"
    match_cat_breed("샴") -> "Siamese Cat"

정책:
- 반환값은 사용자가 제공한 영어 품종명 표기를 그대로 따릅니다.
- 한국어 별칭은 최대한 많이 포함했습니다.
- 정확 매칭을 먼저 하고, 실패하면 영문/한글 부분 매칭과 fuzzy 매칭을 시도합니다.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import get_close_matches, SequenceMatcher
from typing import Dict, Iterable, Optional


CAT_BREEDS = [
    "Abyssinian",
    "Aegean",
    "American Bobtail",
    "American Shorthair",
    "American Wirehair",
    "Aphrodite Giant",
    "Arabian Mau",
    "Asian",
    "Australian Mist",
    "Bambino",
    "Bengal Cats",
    "Birman",
    "Bombay",
    "Brazilian Shorthair",
    "British Longhair",
    "British Shorthair",
    "Burmese",
    "Burmilla",
    "California Spangled",
    "Chantilly-Tiffany",
    "Chausie",
    "Colorpoint Shorthair",
    "Cornish Rex",
    "Cyprus",
    "Devon Rex",
    "Donskoy",
    "European Shorthair",
    "Foldex",
    "German Rex",
    "Highlander",
    "Japanese Bobtail",
    "Javanese",
    "Khao Manee",
    "Kurilian Bobtail",
    "Lykoi",
    "Maine Coon",
    "Manx",
    "Mekong Bobtail",
    "Nebelung",
    "Oriental Bicolor",
    "Persian",
    "Peterbald",
    "Pixie-Bob",
    "Ragdoll Cats",
    "Russian Blue",
    "Savannah",
    "Scottish Fold",
    "Serengeti",
    "Siamese Cat",
    "Siberian",
    "Singapura",
    "Snowshoe",
    "Sokoke",
    "Somali",
    "Sphynx",
    "Tonkinese",
    "Toyger",
    "Turkish Angora",
    "Turkish Van",
    "Ukrainian Levkoy",
    "York Chocolate",
]


def _normalize(text: str) -> str:
    """비교용 문자열 정규화: 소문자화, 악센트 제거, 기호/공백 제거.

    주의: 한글은 NFKD로 분해하면 자모가 되어 [가-힣] 필터에서 사라질 수 있으므로
    NFKC를 먼저 적용하고, 라틴 문자 악센트만 별도로 제거합니다.
    """
    text = unicodedata.normalize("NFKC", str(text)).casefold()
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(ch)
    )
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"(cats?|cat|고양이|묘|품종)$", "", text).strip()
    text = re.sub(r"[^0-9a-z가-힣]+", "", text)
    return text


def _slug(text: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", text.casefold()).strip("-")


def _add_alias(mapping: Dict[str, str], breed: str, aliases: Iterable[str]) -> None:
    for alias in aliases:
        key = _normalize(alias)
        if key:
            mapping[key] = breed


def _build_mapping() -> Dict[str, str]:
    mapping: Dict[str, str] = {}

    for breed in CAT_BREEDS:
        variants = {
            breed,
            breed.replace("-", " "),
            breed.replace("-", ""),
            breed.replace(" Cats", ""),
            breed.replace(" Cat", ""),
            _slug(breed),
            _slug(breed).replace("-", ""),
        }
        _add_alias(mapping, breed, variants)

    ko_aliases = {
        "Abyssinian": ["아비시니안", "아비시니아", "아비시니안고양이"],
        "Aegean": ["에게안", "에게해", "에게안고양이", "에게해고양이"],
        "American Bobtail": ["아메리칸 밥테일", "아메리칸밥테일", "미국밥테일"],
        "American Shorthair": ["아메리칸 숏헤어", "아메리칸숏헤어", "아메숏", "미국숏헤어", "아메리칸 쇼트헤어"],
        "American Wirehair": ["아메리칸 와이어헤어", "아메리칸와이어헤어", "미국와이어헤어"],
        "Aphrodite Giant": ["아프로디테 자이언트", "아프로디테자이언트", "아프로디테 거대묘", "아프로디테"],
        "Arabian Mau": ["아라비안 마우", "아라비안마우", "아라비아 마우"],
        "Asian": ["아시안", "아시아고양이", "아시안고양이"],
        "Australian Mist": ["오스트레일리안 미스트", "오스트레일리안미스트", "호주 미스트", "호주미스트"],
        "Bambino": ["밤비노", "밤비노고양이"],
        "Bengal Cats": ["벵갈", "뱅갈", "벵갈캣", "뱅갈캣", "벵갈 고양이", "뱅갈 고양이"],
        "Birman": ["버만", "비르만", "버먼"],
        "Bombay": ["봄베이", "봄베이고양이"],
        "Brazilian Shorthair": ["브라질리안 숏헤어", "브라질리안숏헤어", "브라질 숏헤어", "브라질리안 쇼트헤어"],
        "British Longhair": ["브리티시 롱헤어", "브리티시롱헤어", "영국 롱헤어"],
        "British Shorthair": ["브리티시 숏헤어", "브리티시숏헤어", "브숏", "영국 숏헤어", "브리티시 쇼트헤어"],
        "Burmese": ["버미즈", "버마고양이", "버마즈"],
        "Burmilla": ["버밀라", "부르밀라"],
        "California Spangled": ["캘리포니아 스팽글드", "캘리포니아스팽글드", "캘리포니아 스팽글"],
        "Chantilly-Tiffany": ["샹틸리 티파니", "샹틸리티파니", "샹티이 티파니", "티파니"],
        "Chausie": ["쵸시", "차우시", "초시", "쇼시"],
        "Colorpoint Shorthair": ["컬러포인트 숏헤어", "컬러포인트숏헤어", "컬러포인트 쇼트헤어"],
        "Cornish Rex": ["코니시 렉스", "코니시렉스", "코니쉬 렉스", "코니쉬렉스"],
        "Cyprus": ["키프로스", "사이프러스", "키프로스고양이"],
        "Devon Rex": ["데본 렉스", "데본렉스"],
        "Donskoy": ["돈스코이", "돈스코이 고양이"],
        "European Shorthair": ["유러피안 숏헤어", "유러피안숏헤어", "유럽 숏헤어", "유러피안 쇼트헤어"],
        "Foldex": ["폴덱스", "폴드엑스"],
        "German Rex": ["저먼 렉스", "저먼렉스", "독일 렉스"],
        "Highlander": ["하이랜더", "하이랜더고양이"],
        "Japanese Bobtail": ["재패니즈 밥테일", "재패니즈밥테일", "일본 밥테일", "일본밥테일"],
        "Javanese": ["자바니즈", "자바고양이"],
        "Khao Manee": ["카오마니", "카오 마니", "카호마니", "카우마니"],
        "Kurilian Bobtail": ["쿠릴리안 밥테일", "쿠릴리안밥테일", "쿠릴 밥테일"],
        "Lykoi": ["라이코이", "리코이", "늑대고양이"],
        "Maine Coon": ["메인쿤", "메인 쿤", "메인쿤고양이"],
        "Manx": ["맹크스", "맨스", "맨크스"],
        "Mekong Bobtail": ["메콩 밥테일", "메콩밥테일"],
        "Nebelung": ["네벨룽", "네벨룽고양이"],
        "Oriental Bicolor": ["오리엔탈 바이컬러", "오리엔탈바이컬러", "오리엔탈 바이칼라"],
        "Persian": ["페르시안", "페르시아", "페르시안고양이"],
        "Peterbald": ["피터볼드", "피터발드"],
        "Pixie-Bob": ["픽시밥", "픽시 밥", "픽시-밥"],
        "Ragdoll Cats": ["랙돌", "렉돌", "래그돌", "랙돌고양이"],
        "Russian Blue": ["러시안 블루", "러시안블루", "러블"],
        "Savannah": ["사바나", "사바나캣", "사바나 고양이"],
        "Scottish Fold": ["스코티시 폴드", "스코티시폴드", "스코티쉬 폴드", "스코티쉬폴드"],
        "Serengeti": ["세렝게티", "세렌게티"],
        "Siamese Cat": ["샴", "샴고양이", "시암", "시암고양이", "샤미즈", "샴즈"],
        "Siberian": ["시베리안", "시베리아 고양이", "시베리안고양이"],
        "Singapura": ["싱가푸라", "싱가푸라고양이"],
        "Snowshoe": ["스노우슈", "스노슈", "스노우 슈"],
        "Sokoke": ["소코케", "소코키"],
        "Somali": ["소말리", "소말리고양이"],
        "Sphynx": ["스핑크스", "스핑스", "스핑크스고양이"],
        "Tonkinese": ["통키니즈", "톤키니즈", "통키네즈"],
        "Toyger": ["토이거", "토이거고양이"],
        "Turkish Angora": ["터키시 앙고라", "터키시앙고라", "터키 앙고라", "터키앙고라"],
        "Turkish Van": ["터키시 반", "터키시반", "터키 반", "터키반"],
        "Ukrainian Levkoy": ["우크라이나 레브코이", "우크라이니안 레브코이", "우크라이나레브코이", "레브코이"],
        "York Chocolate": ["요크 초콜릿", "요크초콜릿", "요크 초콜렛", "요크초콜렛"],
    }

    for breed, aliases in ko_aliases.items():
        _add_alias(mapping, breed, aliases)

    return mapping


CAT_BREED_ALIASES = _build_mapping()

# 한국어 fuzzy 매칭용 alias 목록
_KO_CHOICES = [
    k for k in CAT_BREED_ALIASES.keys()
    if re.search(r'[가-힣]', k)
]

# 자주 발생하는 오타 직접 보정
_KO_TYPO_INDEX = {
    '메인큰': 'Maine Coon',
    '메인쿤이': 'Maine Coon',
    '랙돌이': 'Ragdoll Cats',
    '렉돌': 'Ragdoll Cats',
    '브숏트': 'British Shorthair',
    '아메숏트': 'American Shorthair',
    '샴먀오': 'Siamese Cat',
    '러시안블르': 'Russian Blue',
    '스핑스': 'Sphynx',
}

def match_cat_breed(query: str, *, fuzzy: bool = True, cutoff: float = 0.78) -> Optional[str]:
    """
    한국어/영어 고양이 품종 입력을 표준 영어 품종명으로 변환합니다.
    """
    key = _normalize(query)
    if not key:
        return None

    # 1) 정확 매칭
    if key in CAT_BREED_ALIASES:
        return CAT_BREED_ALIASES[key]

    # 2) 자주 발생하는 오타 직접 보정
    if key in _KO_TYPO_INDEX:
        return _KO_TYPO_INDEX[key]

    # 3) 부분 포함 매칭
    contained = [
        (alias, breed)
        for alias, breed in CAT_BREED_ALIASES.items()
        if len(alias) >= 2 and (alias in key or key in alias)
    ]

    if contained:
        contained.sort(key=lambda item: len(item[0]), reverse=True)
        return contained[0][1]

    # 4) 한국어 fuzzy 보정
    if fuzzy and re.search(r'[가-힣]', key):
        ko_matches = get_close_matches(key, _KO_CHOICES, n=1, cutoff=cutoff)

        if ko_matches:
            candidate = ko_matches[0]

            similarity = SequenceMatcher(None, key, candidate).ratio()
            length_gap = abs(len(key) - len(candidate))

            if similarity >= cutoff and length_gap <= 2:
                return CAT_BREED_ALIASES[candidate]

    # 5) 영문 fuzzy 보정
    if fuzzy:
        matches = get_close_matches(
            key,
            CAT_BREED_ALIASES.keys(),
            n=1,
            cutoff=cutoff
        )

        if matches:
            return CAT_BREED_ALIASES[matches[0]]

    return None
