from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# ---------------------------------------------------------------------
# 색상: 한국어 표현 -> 색상 의미 그룹
# ---------------------------------------------------------------------

KO_COLOR_ALIASES: dict[str, list[str]] = {
    # 검정 계열
    "검정": ["black_family"],
    "검정색": ["black_family"],
    "검은": ["black_family"],
    "검은색": ["black_family"],
    "까만": ["black_family"],
    "까만색": ["black_family"],
    "블랙": ["black_family"],
    "흑색": ["black_family"],

    # 흰색 계열
    "흰": ["white_family"],
    "흰색": ["white_family"],
    "하얀": ["white_family"],
    "하얀색": ["white_family"],
    "화이트": ["white_family"],
    "백색": ["white_family"],
    "아이보리": ["white_family", "cream_family"],
    "상아색": ["white_family", "cream_family"],

    # 회색 / 은색 계열
    "회색": ["gray_family"],
    "그레이": ["gray_family"],
    "잿빛": ["gray_family"],
    "은색": ["silver_family", "gray_family"],
    "실버": ["silver_family", "gray_family"],
    "쥐색": ["gray_family"],

    # 갈색 / 초콜릿 / 간색 계열
    "갈색": ["brown_family"],
    "브라운": ["brown_family"],
    "초콜릿": ["chocolate_family", "brown_family"],
    "초코": ["chocolate_family", "brown_family"],
    "밤색": ["chestnut_family", "brown_family"],
    "체스트넛": ["chestnut_family"],
    "간색": ["liver_family", "brown_family"],
    "리버": ["liver_family"],

    # 빨강 / 적갈색 / 루비 계열
    "빨강": ["red_family"],
    "빨간": ["red_family"],
    "빨간색": ["red_family"],
    "붉은": ["red_family"],
    "붉은색": ["red_family"],
    "레드": ["red_family"],
    "적색": ["red_family"],
    "적갈색": ["mahogany_family", "red_family", "brown_family"],
    "마호가니": ["mahogany_family"],
    "루비": ["ruby_family", "red_family"],

    # 노랑 / 골드 / 크림 계열
    "노랑": ["yellow_family"],
    "노란": ["yellow_family"],
    "노란색": ["yellow_family"],
    "옐로우": ["yellow_family"],
    "금색": ["gold_family"],
    "골드": ["gold_family"],
    "황금색": ["gold_family"],
    "크림": ["cream_family"],
    "크림색": ["cream_family"],
    "베이지": ["beige_family", "cream_family"],
    "베이지색": ["beige_family", "cream_family"],

    # 주황 / 살구 / 복숭아 계열
    "주황": ["orange_family"],
    "주황색": ["orange_family"],
    "오렌지": ["orange_family"],
    "살구색": ["apricot_family"],
    "살구": ["apricot_family"],
    "애프리콧": ["apricot_family"],
    "복숭아색": ["peach_family", "cream_family"],
    "피치": ["peach_family", "cream_family"],

    # 황갈색 / 모래색 / 사슴색 계열
    "황갈색": ["tan_family", "fawn_family"],
    "탄": ["tan_family"],
    "탠": ["tan_family"],
    "사슴색": ["fawn_family"],
    "폰": ["fawn_family"],
    "엷은 갈색": ["fawn_family", "tan_family"],
    "모래색": ["sand_family"],
    "샌드": ["sand_family"],
    "샌디": ["sand_family"],
    "밀색": ["wheaten_family"],
    "휘튼": ["wheaten_family"],

    # 파랑 계열
    "파랑": ["blue_family"],
    "파란": ["blue_family"],
    "파란색": ["blue_family"],
    "블루": ["blue_family"],
    "청색": ["blue_family"],

    # 복합/패턴 계열
    "얼룩": ["spotted_pattern", "patched_pattern", "merle_pattern", "roan_pattern"],
    "얼룩무늬": ["spotted_pattern", "patched_pattern", "merle_pattern", "roan_pattern"],
    "점박이": ["spotted_pattern"],
    "반점": ["spotted_pattern"],
    "패치": ["patched_pattern"],
    "반점 있는": ["patched_pattern", "spotted_pattern"],
    "무늬": ["patterned_family"],
    "무늬 있는": ["patterned_family"],
    "줄무늬": ["brindle_family"],
    "호랑이무늬": ["brindle_family"],
    "브린들": ["brindle_family"],
    "멀": ["merle_pattern"],
    "멀색": ["merle_pattern"],
    "멀무늬": ["merle_pattern"],
    "멀 패턴": ["merle_pattern"],
    "로안": ["roan_pattern"],
    "틱": ["ticked_pattern"],
    "틱킹": ["ticked_pattern"],
    "세이블": ["sable_family"],
    "참깨": ["sesame_family"],
    "세서미": ["sesame_family"],
    "파티": ["parti_pattern"],
    "파티컬러": ["parti_pattern"],
    "피발드": ["piebald_pattern"],
    "파이드": ["pied_pattern"],
    "삼색": ["tricolor_pattern"],
    "트라이": ["tricolor_pattern"],
    "트라이컬러": ["tricolor_pattern"],
    "두가지색": ["bicolor_pattern"],
    "두 가지 색": ["bicolor_pattern"],
    "바이컬러": ["bicolor_pattern"],

    # 명시적 복합 색상
    "검정 갈색": ["black_brown_combo"],
    "검정 흰색": ["black_white_combo"],
    "흑백": ["black_white_combo"],
    "블랙앤화이트": ["black_white_combo"],
    "검정 황갈색": ["black_tan_combo"],
    "블랙탄": ["black_tan_combo"],
    "블랙 앤 탄": ["black_tan_combo"],
    "갈색 흰색": ["brown_white_combo"],
    "갈백": ["brown_white_combo"],
    "빨강 흰색": ["red_white_combo"],
    "레드화이트": ["red_white_combo"],
    "파랑 황갈색": ["blue_tan_combo"],
    "블루탄": ["blue_tan_combo"],
}


# ---------------------------------------------------------------------
# 색상 의미 그룹 -> 실제 영어 태그들
# ---------------------------------------------------------------------

COLOR_GROUP_TO_TAGS: dict[str, list[str]] = {
    "black_family": [
        "black", "solid black", "glossy solid black",
        "black with white", "black with tan", "black with rust",
        "black and tan", "black and white", "black and brown",
        "black and gray", "black and gold", "black and silver",
        "black and mahogany", "black roan", "black saddle",
        "black spots", "black stripes", "black-tipped",
        "black/white", "black/tan", "black/gray",
    ],
    "white_family": [
        "white", "solid white", "pure white", "off-white",
        "white with patches", "white with black", "white with brown",
        "white with tan", "white with gray", "white with lemon",
        "white with orange", "white with red", "white with liver",
        "white with cream", "white and black", "white and brown",
        "white and tan", "white and orange", "white and lemon",
        "white and fawn", "white and chestnut",
    ],
    "gray_family": [
        "gray", "grey", "blue-gray", "silver-gray", "steel gray",
        "iron gray", "mouse-gray", "wolf gray", "wolf grey",
        "yellow-gray", "gray-brown", "gray and white",
        "gray roan", "gray sable", "gray with tan",
        "black-gray", "red-gray",
    ],
    "silver_family": [
        "silver", "silver-gray", "silver sable", "black and silver",
        "brindle silver",
    ],
    "brown_family": [
        "brown", "dark brown", "light brown", "gray-brown",
        "reddish-brown", "brown and white", "brown and tan",
        "brown roan", "brown/white", "brown and grey",
        "chestnut brown", "black and brown",
    ],
    "chocolate_family": [
        "chocolate", "chocolate and tan",
    ],
    "chestnut_family": [
        "chestnut", "rich chestnut", "chestnut brown",
        "chestnut and white", "chestnut ticking",
    ],
    "liver_family": [
        "liver", "solid liver", "golden liver",
        "liver and tan", "liver and white", "liver roan",
        "liver spots", "liver with patches", "liver with white",
    ],
    "red_family": [
        "red", "dark red", "deep red", "light red", "rich red",
        "fox red", "golden red", "wolf red", "red and white",
        "red with white", "red with black", "red-black",
        "black-red", "red roan", "red merle", "red sesame",
        "red tick", "redtick", "red speckle", "red wheaten",
        "red and rust", "solid red", "red bi-color",
    ],
    "mahogany_family": [
        "mahogany", "black and mahogany",
    ],
    "ruby_family": [
        "ruby",
    ],
    "yellow_family": [
        "yellow", "pale yellow", "yellow-gray",
    ],
    "gold_family": [
        "gold", "golden", "golden red", "golden rust",
        "golden liver", "gold and white", "black and gold",
        "brindle gold",
    ],
    "cream_family": [
        "cream", "pale cream", "biscuit", "white with cream",
        "ivory", "off-white", "beige", "peach",
    ],
    "beige_family": [
        "beige", "cream", "pale cream",
    ],
    "orange_family": [
        "orange", "orange-red", "orange and white", "orange roan",
        "white with orange", "white and orange",
    ],
    "apricot_family": [
        "apricot",
    ],
    "peach_family": [
        "peach",
    ],
    "tan_family": [
        "tan", "tan-pointed", "tan and white", "tan points",
        "tan trim", "black and tan", "black with tan",
        "brown and tan", "chocolate and tan", "liver and tan",
        "blue and tan", "gray with tan", "grizzle and tan",
        "tricolor with tan",
    ],
    "fawn_family": [
        "fawn", "light fawn", "fawn and white", "fawn roan",
        "fawn with black", "fawn with mask", "fawn with white",
        "white and fawn",
    ],
    "sand_family": [
        "sand", "sandy",
    ],
    "wheaten_family": [
        "wheaten", "red wheaten",
    ],
    "blue_family": [
        "blue", "blue-gray", "blue and tan", "blue and gold",
        "blue and rust", "blue merle", "blue mottled",
        "blue mottle", "blue roan", "blue speckle",
        "blue tick", "bluetick", "bluetic",
    ],
    "sable_family": [
        "sable", "wolf sable", "silver sable", "gray sable",
        "sable and white", "sable spots",
    ],
    "sesame_family": [
        "sesame", "red sesame",
    ],

    # patterns
    "brindle_family": [
        "brindle", "brindle and white", "brindle shades",
        "brindle gold", "brindle silver",
    ],
    "spotted_pattern": [
        "spotted", "leopard", "leopard spotted",
        "black spots", "liver spots", "sable spots",
    ],
    "patched_pattern": [
        "patched", "white with patches", "liver with patches",
        "roan with patches",
    ],
    "merle_pattern": [
        "merle", "merle patterns", "blue merle", "red merle",
    ],
    "roan_pattern": [
        "roan", "roan patterns", "roan with patches",
        "blue roan", "brown roan", "gray roan",
        "liver roan", "orange roan", "red roan", "black roan",
    ],
    "ticked_pattern": [
        "ticked", "ticking", "chestnut ticking",
    ],
    "parti_pattern": [
        "parti", "parti-color", "particolor",
    ],
    "piebald_pattern": [
        "piebald",
    ],
    "pied_pattern": [
        "pied",
    ],
    "tricolor_pattern": [
        "tri", "tri-color", "tricolor", "tricolor with tan",
    ],
    "bicolor_pattern": [
        "bicolor", "bi-color", "bi-black", "bi-blue",
    ],
    "patterned_family": [
        "brindle", "spotted", "patched", "piebald", "pied",
        "merle", "roan", "ticked", "ticking", "parti",
        "parti-color", "particolor", "tricolor", "bicolor",
        "harlequin", "dapple", "mantle", "domino",
    ],

    # explicit combos
    "black_brown_combo": ["black and brown"],
    "black_white_combo": ["black and white", "black/white", "black with white", "white and black", "white with black"],
    "black_tan_combo": ["black and tan", "black/tan", "black with tan", "tan points"],
    "brown_white_combo": ["brown and white", "brown/white", "white and brown", "white with brown"],
    "red_white_combo": ["red and white", "red with white", "white with red"],
    "blue_tan_combo": ["blue and tan"],
}


# ---------------------------------------------------------------------
# 색상 태그 확장 강도 설정
# ---------------------------------------------------------------------
# 기존 COLOR_GROUP_TO_TAGS는 전체 후보를 보관합니다.
# 아래 COLOR_GROUP_EXPANSION_OVERRIDES는 검색 정확도를 위해
# 각 색상 그룹을 primary / related로 나눕니다.
#
# mode="primary": 가장 직접적인 색상 태그만 반환
# mode="related": primary + 관련 복합/확장 태그 반환
# mode="all": related와 동일하게 전체 확장 반환

ColorExpansion = dict[str, dict[str, list[str]]]

COLOR_GROUP_EXPANSION_OVERRIDES: ColorExpansion = {
    "black_family": {
        "primary": ["black", "solid black"],
        "related": [
            "glossy solid black", "black with white", "black with tan",
            "black with rust", "black and tan", "black and white",
            "black and brown", "black and gray", "black and gold",
            "black and silver", "black and mahogany", "black roan",
            "black saddle", "black spots", "black stripes", "black-tipped",
            "black/white", "black/tan", "black/gray",
        ],
    },
    "white_family": {
        "primary": ["white", "solid white", "pure white"],
        "related": [
            "off-white", "white with patches", "white with black",
            "white with brown", "white with tan", "white with gray",
            "white with lemon", "white with orange", "white with red",
            "white with liver", "white with cream", "white and black",
            "white and brown", "white and tan", "white and orange",
            "white and lemon", "white and fawn", "white and chestnut",
        ],
    },
    "gray_family": {
        "primary": ["gray", "grey"],
        "related": [
            "blue-gray", "silver-gray", "steel gray", "iron gray",
            "mouse-gray", "wolf gray", "wolf grey", "yellow-gray",
            "gray-brown", "gray and white", "gray roan", "gray sable",
            "gray with tan", "black-gray", "red-gray",
        ],
    },
    "silver_family": {
        "primary": ["silver"],
        "related": ["silver-gray", "silver sable", "black and silver", "brindle silver"],
    },
    "brown_family": {
        "primary": ["brown"],
        "related": [
            "dark brown", "light brown", "gray-brown", "reddish-brown",
            "brown and white", "brown and tan", "brown roan", "brown/white",
            "brown and grey", "chestnut brown", "black and brown",
        ],
    },
    "chocolate_family": {
        "primary": ["chocolate"],
        "related": ["chocolate and tan"],
    },
    "chestnut_family": {
        "primary": ["chestnut", "chestnut brown"],
        "related": ["rich chestnut", "chestnut and white", "chestnut ticking"],
    },
    "liver_family": {
        "primary": ["liver", "solid liver"],
        "related": [
            "golden liver", "liver and tan", "liver and white", "liver roan",
            "liver spots", "liver with patches", "liver with white",
        ],
    },
    "red_family": {
        "primary": ["red", "solid red"],
        "related": [
            "dark red", "deep red", "light red", "rich red", "fox red",
            "golden red", "wolf red", "red and white", "red with white",
            "red with black", "red-black", "black-red", "red roan",
            "red merle", "red sesame", "red tick", "redtick", "red speckle",
            "red wheaten", "red and rust", "red bi-color",
        ],
    },
    "tan_family": {
        "primary": ["tan", "tan points"],
        "related": [
            "tan-pointed", "tan and white", "tan trim", "black and tan",
            "black with tan", "brown and tan", "chocolate and tan",
            "liver and tan", "blue and tan", "gray with tan",
            "grizzle and tan", "tricolor with tan",
        ],
    },
    "fawn_family": {
        "primary": ["fawn"],
        "related": [
            "light fawn", "fawn and white", "fawn roan", "fawn with black",
            "fawn with mask", "fawn with white", "white and fawn",
        ],
    },
    "blue_family": {
        "primary": ["blue"],
        "related": [
            "blue-gray", "blue and tan", "blue and gold", "blue and rust",
            "blue merle", "blue mottled", "blue mottle", "blue roan",
            "blue speckle", "blue tick", "bluetick", "bluetic",
        ],
    },
    "cream_family": {
        "primary": ["cream", "pale cream"],
        "related": ["biscuit", "white with cream", "ivory", "off-white", "beige", "peach"],
    },

    # 패턴 계열은 primary에서도 대표 패턴 태그를 유지합니다.
    "brindle_family": {
        "primary": ["brindle"],
        "related": ["brindle and white", "brindle shades", "brindle gold", "brindle silver"],
    },
    "spotted_pattern": {
        "primary": ["spotted"],
        "related": ["leopard", "leopard spotted", "black spots", "liver spots", "sable spots"],
    },
    "patched_pattern": {
        "primary": ["patched"],
        "related": ["white with patches", "liver with patches", "roan with patches"],
    },
    "merle_pattern": {
        "primary": ["merle"],
        "related": ["merle patterns", "blue merle", "red merle"],
    },
    "roan_pattern": {
        "primary": ["roan"],
        "related": [
            "roan patterns", "roan with patches", "blue roan", "brown roan",
            "gray roan", "liver roan", "orange roan", "red roan", "black roan",
        ],
    },
    "tricolor_pattern": {
        "primary": ["tricolor", "tri-color", "tri"],
        "related": ["tricolor with tan"],
    },
    "bicolor_pattern": {
        "primary": ["bicolor", "bi-color"],
        "related": ["bi-black", "bi-blue"],
    },

    # 명시적 복합색은 primary에서 바로 정확한 복합 태그를 반환합니다.
    "black_brown_combo": {
        "primary": ["black and brown"],
        "related": [],
    },
    "black_white_combo": {
        "primary": ["black and white", "black/white"],
        "related": ["black with white", "white and black", "white with black"],
    },
    "black_tan_combo": {
        "primary": ["black and tan", "black/tan"],
        "related": ["black with tan", "tan points"],
    },
    "brown_white_combo": {
        "primary": ["brown and white", "brown/white"],
        "related": ["white and brown", "white with brown"],
    },
    "red_white_combo": {
        "primary": ["red and white"],
        "related": ["red with white", "white with red"],
    },
    "blue_tan_combo": {
        "primary": ["blue and tan"],
        "related": [],
    },
}


def _make_expansion_map(
    base_map: dict[str, list[str]],
    overrides: ColorExpansion,
) -> dict[str, dict[str, list[str]]]:
    """기존 list 기반 그룹을 primary/related 구조로 변환합니다."""
    expansion_map: dict[str, dict[str, list[str]]] = {}

    for group, tags in base_map.items():
        if group in overrides:
            expansion_map[group] = overrides[group]
            continue

        if not tags:
            expansion_map[group] = {"primary": [], "related": []}
        elif len(tags) == 1:
            expansion_map[group] = {"primary": tags, "related": []}
        else:
            expansion_map[group] = {"primary": [tags[0]], "related": tags[1:]}

    return expansion_map


COLOR_GROUP_TO_TAGS_EXPANDED = _make_expansion_map(
    COLOR_GROUP_TO_TAGS,
    COLOR_GROUP_EXPANSION_OVERRIDES,
)


# ---------------------------------------------------------------------
# 성격: 한국어 표현 -> 성격 의미 그룹
# ---------------------------------------------------------------------

KO_TEMPERAMENT_ALIASES: dict[str, list[str]] = {
    # 차분함 / 안정감
    "차분한": ["calm_family"],
    "얌전한": ["calm_family", "gentle_family"],
    "침착한": ["calm_family", "confident_family"],
    "조용한": ["quiet_family", "calm_family"],
    "온순한": ["gentle_family", "docile_family", "calm_family"],
    "순한": ["gentle_family", "docile_family"],
    "평온한": ["calm_family"],
    "안정적인": ["stable_family"],
    "균형잡힌": ["balanced_family", "stable_family"],
    "차분함": ["calm_family"],
    "얌전함": ["calm_family", "gentle_family"],
    "조용함": ["quiet_family", "calm_family"],

    # 충성 / 헌신
    "충성스러운": ["loyal_family"],
    "충직한": ["loyal_family"],
    "헌신적인": ["devoted_family", "loyal_family"],
    "믿음직한": ["reliable_family", "loyal_family"],
    "신뢰할 수 있는": ["reliable_family", "trustworthy_family"],

    # 애정 / 친화
    "애교있는": ["affectionate_family", "playful_family"],
    "애정있는": ["affectionate_family"],
    "다정한": ["affectionate_family", "friendly_family", "gentle_family"],
    "사랑스러운": ["loving_family", "affectionate_family"],
    "사람을 좋아하는": ["friendly_family", "social_family", "people_focused_family"],
    "친근한": ["friendly_family"],
    "친화적인": ["friendly_family", "social_family"],
    "사교적인": ["social_family", "friendly_family"],
    "사회적인": ["social_family"],
    "외향적인": ["outgoing_family", "social_family"],
    "붙임성 있는": ["friendly_family", "social_family"],

    # 활발 / 장난 / 에너지
    "활발한": ["energetic_family", "active_family", "lively_family"],
    "활동적인": ["active_family", "energetic_family"],
    "에너지 넘치는": ["energetic_family"],
    "기운찬": ["energetic_family", "vigorous_family"],
    "발랄한": ["lively_family", "playful_family"],
    "명랑한": ["cheerful_family", "happy_family"],
    "쾌활한": ["cheerful_family", "happy_family", "lively_family"],
    "장난기 많은": ["playful_family", "mischievous_family"],
    "장난스러운": ["playful_family", "mischievous_family"],
    "놀기 좋아하는": ["playful_family"],
    "유쾌한": ["happy_family", "cheerful_family", "amusing_family"],

    # 지능 / 훈련
    "똑똑한": ["intelligent_family", "smart_family"],
    "영리한": ["intelligent_family", "clever_family", "smart_family"],
    "지능적인": ["intelligent_family"],
    "눈치빠른": ["clever_family", "quick_family"],
    "학습이 빠른": ["trainable_family", "intelligent_family"],
    "훈련이 쉬운": ["trainable_family", "biddable_family"],
    "훈련 잘 되는": ["trainable_family", "biddable_family"],
    "순종적인": ["obedient_family", "biddable_family"],

    # 보호 / 경계
    "보호적인": ["protective_family"],
    "경계심 있는": ["alert_family", "watchful_family", "vigilant_family", "wary_family"],
    "경계하는": ["alert_family", "watchful_family", "vigilant_family", "wary_family"],
    "감시하는": ["watchful_family", "vigilant_family"],
    "감시견 같은": ["watchful_family", "protective_family"],
    "용감한": ["brave_family", "courageous_family", "fearless_family"],
    "겁없는": ["fearless_family", "bold_family"],
    "대담한": ["bold_family", "confident_family"],
    "자신감 있는": ["confident_family", "self_confident_family"],
    "당당한": ["confident_family", "dignified_family"],
    "위엄있는": ["dignified_family", "noble_family"],

    # 독립 / 고집 / 진지함
    "독립적인": ["independent_family"],
    "독립심 강한": ["independent_family"],
    "고집있는": ["stubborn_family", "strong_willed_family"],
    "고집 센": ["stubborn_family", "strong_willed_family"],
    "의지가 강한": ["strong_willed_family", "determined_family"],
    "단호한": ["determined_family", "decisive_family"],
    "끈질긴": ["persistent_family", "tenacious_family"],
    "집요한": ["tenacious_family", "persistent_family"],
    "진지한": ["serious_family"],

    # 예민 / 조심 / 낯가림
    "예민한": ["sensitive_family"],
    "섬세한": ["sensitive_family", "gentle_family"],
    "조심스러운": ["cautious_family", "wary_family"],
    "낯가리는": ["reserved_family", "aloof_family", "shy_family"],
    "소심한": ["shy_family", "cautious_family"],
    "수줍은": ["shy_family", "reserved_family"],
    "냉담한": ["aloof_family", "reserved_family"],
    "낯선 사람을 경계하는": ["wary_of_strangers_family", "reserved_with_strangers_family"],

    # 작업성 / 운동성
    "운동능력이 좋은": ["athletic_family", "agile_family"],
    "운동을 좋아하는": ["athletic_family", "active_family"],
    "민첩한": ["agile_family", "quick_family"],
    "빠른": ["fast_family", "quick_family", "swift_family"],
    "일 잘하는": ["hardworking_family", "diligent_family", "work_driven_family"],
    "부지런한": ["diligent_family", "hardworking_family"],
    "집중력 있는": ["focused_family", "attentive_family"],

    # 복합 성격 예시
    "차분하면서 충성스러운": ["calm_family", "loyal_family"],
    "차분하고 충성스러운": ["calm_family", "loyal_family"],
    "활발하고 친화적인": ["energetic_family", "friendly_family", "social_family"],
    "똑똑하고 훈련이 쉬운": ["intelligent_family", "trainable_family"],
    "용감하고 보호적인": ["brave_family", "protective_family"],
    "얌전하고 다정한": ["calm_family", "gentle_family", "affectionate_family"],
}


# ---------------------------------------------------------------------
# 성격 의미 그룹 -> 실제 영어 태그들
# ---------------------------------------------------------------------

TEMPERAMENT_GROUP_TO_TAGS: dict[str, list[str]] = {
    "calm_family": ["calm", "mellow", "placid", "composed", "steady", "even-tempered", "stable"],
    "quiet_family": ["quiet", "calm", "reserved"],
    "gentle_family": ["gentle", "mild", "sweet", "kind", "benevolent", "pleasant"],
    "docile_family": ["docile", "obedient", "biddable", "gentle"],
    "stable_family": ["stable", "steady", "reliable", "dependable", "even-tempered"],
    "balanced_family": ["balanced", "well-balanced", "even-tempered", "stable"],

    "loyal_family": ["loyal", "faithful", "devoted", "attached", "loyal to owner", "loyal to family"],
    "devoted_family": ["devoted", "faithful", "loyal", "devoted to family"],
    "reliable_family": ["reliable", "dependable", "trustworthy", "steady"],
    "trustworthy_family": ["trustworthy", "reliable", "dependable", "faithful"],

    "affectionate_family": ["affectionate", "loving", "attached", "sweet", "gentle"],
    "loving_family": ["loving", "affectionate", "sweet"],
    "friendly_family": ["friendly", "amiable", "amicable", "genial", "pleasant", "neutral-friendly"],
    "social_family": ["social", "sociable", "outgoing", "extroverted", "companionable"],
    "people_focused_family": ["people-focused", "human-oriented", "contact-seeking"],
    "outgoing_family": ["outgoing", "extroverted", "sociable", "friendly"],

    "energetic_family": ["energetic", "active", "lively", "vigorous", "dynamic", "exuberant"],
    "active_family": ["active", "athletic", "energetic", "outdoorsy"],
    "lively_family": ["lively", "spirited", "cheerful", "playful", "bright"],
    "vigorous_family": ["vigorous", "energetic", "active"],
    "playful_family": ["playful", "funny", "amusing", "comical", "merry"],
    "mischievous_family": ["mischievous", "playful", "funny"],
    "cheerful_family": ["cheerful", "happy", "merry", "bright"],
    "happy_family": ["happy", "cheerful", "merry"],
    "amusing_family": ["amusing", "funny", "comical", "humorous", "witty"],

    "intelligent_family": ["intelligent", "smart", "bright", "clever", "resourceful", "inquisitive"],
    "smart_family": ["smart", "intelligent", "bright", "clever"],
    "clever_family": ["clever", "smart", "intelligent", "quick", "witty"],
    "quick_family": ["quick", "clever", "agile", "fast"],
    "trainable_family": ["trainable", "biddable", "obedient", "responsive", "willing", "eager"],
    "biddable_family": ["biddable", "willing", "obedient", "trainable", "responsive"],
    "obedient_family": ["obedient", "biddable", "docile", "willing"],

    "protective_family": ["protective", "watchful", "vigilant", "territorial"],
    "alert_family": ["alert", "watchful", "vigilant", "attentive", "observant"],
    "watchful_family": ["watchful", "alert", "vigilant", "observant"],
    "vigilant_family": ["vigilant", "watchful", "alert"],
    "wary_family": ["wary", "cautious", "reserved", "distrustful"],
    "brave_family": ["brave", "courageous", "fearless", "bold"],
    "courageous_family": ["courageous", "brave", "fearless", "bold"],
    "fearless_family": ["fearless", "brave", "bold", "courageous"],
    "bold_family": ["bold", "confident", "assertive", "fearless"],
    "confident_family": ["confident", "self-confident", "self-assured", "stable"],
    "self_confident_family": ["self-confident", "self-assured", "confident"],
    "dignified_family": ["dignified", "noble", "elegant", "graceful"],
    "noble_family": ["noble", "dignified", "elegant"],

    "independent_family": ["independent", "aloof", "self-confident"],
    "stubborn_family": ["stubborn", "opinionated", "headstrong", "strong-willed"],
    "strong_willed_family": ["strong-willed", "determined", "stubborn", "headstrong"],
    "determined_family": ["determined", "persistent", "tenacious", "decisive"],
    "decisive_family": ["decisive", "determined", "confident"],
    "persistent_family": ["persistent", "tenacious", "determined", "tireless"],
    "tenacious_family": ["tenacious", "persistent", "determined"],
    "serious_family": ["serious", "firm", "focused"],

    "sensitive_family": ["sensitive", "thoughtful", "intuitive"],
    "cautious_family": ["cautious", "wary", "reserved"],
    "reserved_family": ["reserved", "aloof", "quiet", "shy"],
    "aloof_family": ["aloof", "reserved", "independent"],
    "shy_family": ["shy", "reserved", "cautious"],
    "wary_of_strangers_family": ["wary of strangers", "distrustful of strangers", "reserved with strangers"],
    "reserved_with_strangers_family": ["reserved with strangers", "aloof with strangers", "cautious with strangers"],

    "athletic_family": ["athletic", "agile", "active", "swift"],
    "agile_family": ["agile", "quick", "swift", "athletic"],
    "fast_family": ["fast", "quick", "swift"],
    "swift_family": ["swift", "fast", "quick"],
    "hardworking_family": ["hardworking", "hard-working", "diligent", "work-driven", "tireless"],
    "diligent_family": ["diligent", "hardworking", "hard-working"],
    "work_driven_family": ["work-driven", "hardworking", "focused", "diligent"],
    "focused_family": ["focused", "attentive", "serious"],
    "attentive_family": ["attentive", "alert", "observant", "focused"],
}


# ---------------------------------------------------------------------
# 추출 유틸
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ExtractedDogQueryTags:
    color_groups: list[str]
    color_tags: list[str]
    temperament_groups: list[str]
    temperament_tags: list[str]


def _dedupe(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        item = item.strip().lower()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _match_groups(text: str, alias_map: dict[str, list[str]]) -> list[str]:
    text = text.lower().replace(" ", "")
    matched: list[str] = []

    # 긴 표현 우선 매칭
    for ko_expr in sorted(alias_map.keys(), key=len, reverse=True):
        normalized_expr = ko_expr.lower().replace(" ", "")
        if normalized_expr in text:
            matched.extend(alias_map[ko_expr])

    return _dedupe(matched)


def _expand_groups(
    groups: Iterable[str],
    group_map: dict,
    *,
    mode: str = "all",
) -> list[str]:
    """
    의미 그룹을 실제 영어 태그로 확장합니다.

    mode:
        - "primary": 가장 직접적인 태그만 반환
        - "related": primary + related 반환
        - "all": related와 동일하게 전체 반환

    group_map은 기존 list 구조와 primary/related dict 구조를 모두 지원합니다.
    """
    if mode not in {"primary", "related", "all"}:
        raise ValueError('mode must be one of: "primary", "related", "all"')

    tags: list[str] = []

    for group in groups:
        value = group_map.get(group, [])

        # 새 구조: {"primary": [...], "related": [...]}
        if isinstance(value, dict):
            tags.extend(value.get("primary", []))
            if mode in {"related", "all"}:
                tags.extend(value.get("related", []))
            continue

        # 기존 구조: ["tag1", "tag2", ...]
        if isinstance(value, list):
            if mode == "primary":
                tags.extend(value[:1])
            else:
                tags.extend(value)

    return _dedupe(tags)


def extract_query_tags(
    user_input: str,
    *,
    color_mode: str = "primary",
    temperament_mode: str = "all",
) -> ExtractedDogQueryTags:
    """
    한국어 입력을 색상/성격 의미 그룹과 영어 태그로 변환합니다.

    기본값:
        color_mode="primary"
            색상은 보수적으로 확장합니다.
            예: "검정색" -> ["black", "solid black"]

        temperament_mode="all"
            성격은 의미 유사성이 중요하므로 기존처럼 넓게 확장합니다.
            예: "차분한" -> ["calm", "mellow", "placid", ...]
    """
    color_groups = _match_groups(user_input, KO_COLOR_ALIASES)
    temperament_groups = _match_groups(user_input, KO_TEMPERAMENT_ALIASES)

    return ExtractedDogQueryTags(
        color_groups=color_groups,
        color_tags=_expand_groups(
            color_groups,
            COLOR_GROUP_TO_TAGS_EXPANDED,
            mode=color_mode,
        ),
        temperament_groups=temperament_groups,
        temperament_tags=_expand_groups(
            temperament_groups,
            TEMPERAMENT_GROUP_TO_TAGS,
            mode=temperament_mode,
        ),
    )

