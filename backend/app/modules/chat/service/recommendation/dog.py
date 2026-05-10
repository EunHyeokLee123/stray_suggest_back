from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Iterable, Literal
from urllib.parse import quote

from google.genai import types
from pydantic import BaseModel, Field

from app.modules.chat.repository.connector.mysql import get_mysql_connection
from app.modules.chat.service.llm.google import GEMINI_MODEL, client, safe_parse_json
from app.modules.chat.service.recommendation.dog_segments import (
    COLOR_GROUP_TO_TAGS,
    TEMPERAMENT_GROUP_TO_TAGS,
    extract_query_tags,
)


TEMPERAMENT_NUMERIC_HINTS = {
    "calm_family": {
        "energy": 2,
        "exercise_needs": 2,
        "playfulness": 2,
        "barking": 2,
        "apartment_friendly": 4,
    },
    "gentle_family": {
        "energy": 2,
        "playfulness": 2,
        "novice_owner_friendly": 4,
    },
    "friendly_family": {
        "playfulness": 3,
        "novice_owner_friendly": 4,
    },
    "affectionate_family": {
        "playfulness": 3,
        "apartment_friendly": 4,
    },
    "energetic_family": {
        "energy": 5,
        "exercise_needs": 5,
        "playfulness": 5,
    },
    "active_family": {
        "energy": 4,
        "exercise_needs": 4,
    },
    "playful_family": {
        "playfulness": 5,
        "energy": 4,
    },
    "trainable_family": {
        "trainability": 5,
        "novice_owner_friendly": 4,
    },
    "obedient_family": {
        "trainability": 4,
    },
    "intelligent_family": {
        "trainability": 4,
    },
    "smart_family": {
        "trainability": 4,
    },
    "protective_family": {
        "barking": 3,
        "novice_owner_friendly": 2,
    },
    "watchful_family": {
        "barking": 3,
    },
    "alert_family": {
        "barking": 3,
    },
    "wary_family": {
        "good_with_strangers": 2,
        "barking": 3,
    },
    "reserved_family": {
        "energy": 2,
        "playfulness": 2,
    },
    "aloof_family": {
        "energy": 2,
        "playfulness": 2,
    },
}

NUMERIC_FIELDS = {
    "shedding",
    "grooming",
    "apartment_friendly",
    "novice_owner_friendly",
    "children_friendly",
    "good_with_other_dogs",
    "good_with_strangers",
    "energy",
    "exercise_needs",
    "playfulness",
    "trainability",
    "barking",
    "cold_tolerance",
    "heat_tolerance",
}


class DogSearchIntent(BaseModel):
    colors_ko: list[str] = Field(default_factory=list)
    temperaments_ko: list[str] = Field(default_factory=list)
    negative_colors_ko: list[str] = Field(default_factory=list)
    negative_temperaments_ko: list[str] = Field(default_factory=list)
    size_category: Literal["toy", "small", "medium", "large", "giant"] | None = None
    shedding: int | None = Field(default=None, ge=1, le=5)
    grooming: int | None = Field(default=None, ge=1, le=5)
    apartment_friendly: int | None = Field(default=None, ge=1, le=5)
    novice_owner_friendly: int | None = Field(default=None, ge=1, le=5)
    children_friendly: int | None = Field(default=None, ge=1, le=5)
    good_with_other_dogs: int | None = Field(default=None, ge=1, le=5)
    good_with_strangers: int | None = Field(default=None, ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    exercise_needs: int | None = Field(default=None, ge=1, le=5)
    playfulness: int | None = Field(default=None, ge=1, le=5)
    trainability: int | None = Field(default=None, ge=1, le=5)
    barking: int | None = Field(default=None, ge=1, le=5)
    cold_tolerance: int | None = Field(default=None, ge=1, le=5)
    heat_tolerance: int | None = Field(default=None, ge=1, le=5)


@dataclass(frozen=True)
class DogQueryMappingResult:
    original_input: str
    colors_ko: list[str]
    temperaments_ko: list[str]
    negative_colors_ko: list[str]
    negative_temperaments_ko: list[str]
    color_groups: list[str]
    color_tags: list[str]
    temperament_groups: list[str]
    temperament_tags: list[str]
    negative_color_groups: list[str]
    negative_color_tags: list[str]
    negative_temperament_groups: list[str]
    negative_temperament_tags: list[str]
    size_category: str | None = None
    shedding: int | None = None
    grooming: int | None = None
    apartment_friendly: int | None = None
    novice_owner_friendly: int | None = None
    children_friendly: int | None = None
    good_with_other_dogs: int | None = None
    good_with_strangers: int | None = None
    energy: int | None = None
    exercise_needs: int | None = None
    playfulness: int | None = None
    trainability: int | None = None
    barking: int | None = None
    cold_tolerance: int | None = None
    heat_tolerance: int | None = None


def search_dog_breed_recommendations(
    user_input: str,
    *,
    limit: int = 12,
    use_llm: bool = True,
    include_debug: bool = False,
):
    mapping = map_dog_query(user_input, use_llm=use_llm)
    payload = build_filter_payload(mapping)
    sql, params = build_dog_breed_query(payload, limit=limit)
    rows = _fetch_rows(sql, params)

    response = {
        "kind": "dog",
        "query": user_input,
        "limit": limit,
        "filters": _public_filters(payload),
        "recommendations": [
            _normalize_dog_row(row, rank=index + 1)
            for index, row in enumerate(rows)
        ],
    }

    if include_debug:
        response["debug"] = {
            "mapping": asdict(mapping),
            "payload": payload,
            "sql": sql,
            "params": params,
        }

    return response


def extract_intent_with_gemini(user_input: str) -> DogSearchIntent:
    system_instruction = """
너는 강아지 품종 추천 조건 추출기다.

목표:
사용자의 한국어 자연어 입력에서 강아지 품종 추천 조건만 추출한다.

중요 규칙:
- 사용자가 명시하거나 강하게 암시한 조건만 추출한다.
- 입력에 근거가 없는 값은 절대 추측하지 말고 null 또는 빈 배열로 둔다.
- 품종명, 가격, 지역, 분양 여부, 성별, 나이는 제외한다.
- colors_ko, temperaments_ko는 한국어 표현 그대로 추출한다.
- 색상과 성격을 섞지 않는다.
- 부정 조건은 negative_* 필드에 넣는다.

성격 표현은 가능한 한 형용사형으로 정규화한다.
예: 차분함 -> 차분한
예: 충성심 강함 -> 충성스러운
예: 활발함 -> 활발한

size_category:
- 반드시 다음 중 하나만 사용한다: toy, small, medium, large, giant
- 아주 작은, 초소형, 토이 -> toy
- 작은, 소형 -> small
- 중간, 중형 -> medium
- 큰, 대형 -> large
- 아주 큰, 초대형, 거대한 -> giant
- 크기 언급이 없으면 null

1~5 숫자 필드 규칙:
- 1 = 매우 낮음 / 매우 적음 / 매우 쉬움
- 2 = 낮음
- 3 = 보통
- 4 = 높음
- 5 = 매우 높음

필드별 해석:
- shedding: 털빠짐. "털이 거의 안 빠짐"=1, "털빠짐 적음"=2, "털 많이 빠짐"=4~5
- grooming: 미용관리난이도. "관리 쉬움"=1~2, "미용 자주 필요"=4~5
- apartment_friendly: 아파트생활적합도. "아파트에서 키우기 좋음"=4~5
- novice_owner_friendly: 초보보호자적합도. "초보자에게 좋음"=4~5, "경험자용"=1~2
- children_friendly: 아이 친화도. "아이와 잘 지냄"=4~5
- good_with_other_dogs: 다른 개와의 친화도. "다른 강아지와 잘 지냄"=4~5
- good_with_strangers: 낯선 사람 친화도. "낯선 사람에게 친절"=4~5, "낯가림/경계"=1~2
- energy: 에너지 수준. "활발함"=4~5, "차분함"=1~2
- exercise_needs: 운동필요량. "산책 많이 필요"=4~5, "운동량 적음"=1~2
- playfulness: 장난기. "장난기 많음"=4~5
- trainability: 훈련 용이성. "훈련 쉬움/잘 배움"=4~5, "훈련 어려움"=1~2
- barking: 짖음 정도. "잘 안 짖음"=1~2, "많이 짖음"=4~5
- cold_tolerance: 추위 적응력. "추위에 강함"=4~5, "추위에 약함"=1~2
- heat_tolerance: 더위 적응력. "더위에 강함"=4~5, "더위에 약함"=1~2

출력은 반드시 JSON 스키마를 따른다.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"사용자 입력:\n{user_input}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=DogSearchIntent,
            temperature=0.1,
        ),
    )

    parsed = getattr(response, "parsed", None)

    if isinstance(parsed, DogSearchIntent):
        return parsed

    if isinstance(parsed, dict):
        return DogSearchIntent.model_validate(parsed)

    return DogSearchIntent.model_validate(safe_parse_json(response.text))


def map_dog_query(user_input: str, *, use_llm: bool = True) -> DogQueryMappingResult:
    if use_llm:
        intent = extract_intent_with_gemini(user_input)
    else:
        intent = DogSearchIntent(
            colors_ko=[user_input],
            temperaments_ko=[user_input],
            negative_colors_ko=[],
            negative_temperaments_ko=[],
        )

    positive_text = merge_phrases(intent.colors_ko + intent.temperaments_ko)
    positive_tags = extract_query_tags(positive_text)

    numeric_filters = {
        "shedding": intent.shedding,
        "grooming": intent.grooming,
        "apartment_friendly": intent.apartment_friendly,
        "novice_owner_friendly": intent.novice_owner_friendly,
        "children_friendly": intent.children_friendly,
        "good_with_other_dogs": intent.good_with_other_dogs,
        "good_with_strangers": intent.good_with_strangers,
        "energy": intent.energy,
        "exercise_needs": intent.exercise_needs,
        "playfulness": intent.playfulness,
        "trainability": intent.trainability,
        "barking": intent.barking,
        "cold_tolerance": intent.cold_tolerance,
        "heat_tolerance": intent.heat_tolerance,
    }

    numeric_filters = apply_temperament_numeric_hints(
        positive_tags.temperament_groups,
        numeric_filters,
    )

    negative_color_text = merge_phrases(intent.negative_colors_ko)
    negative_color_groups = []
    if negative_color_text:
        negative_color_groups = extract_query_tags(negative_color_text).color_groups

    negative_temperament_text = merge_phrases(intent.negative_temperaments_ko)
    negative_temperament_groups = []
    if negative_temperament_text:
        negative_temperament_groups = extract_query_tags(negative_temperament_text).temperament_groups

    return DogQueryMappingResult(
        original_input=user_input,
        colors_ko=dedupe(intent.colors_ko),
        temperaments_ko=dedupe(intent.temperaments_ko),
        negative_colors_ko=dedupe(intent.negative_colors_ko),
        negative_temperaments_ko=dedupe(intent.negative_temperaments_ko),
        color_groups=positive_tags.color_groups,
        color_tags=positive_tags.color_tags,
        temperament_groups=positive_tags.temperament_groups,
        temperament_tags=positive_tags.temperament_tags,
        negative_color_groups=negative_color_groups,
        negative_color_tags=expand_groups(negative_color_groups, COLOR_GROUP_TO_TAGS),
        negative_temperament_groups=negative_temperament_groups,
        negative_temperament_tags=expand_groups(
            negative_temperament_groups,
            TEMPERAMENT_GROUP_TO_TAGS,
        ),
        size_category=intent.size_category,
        shedding=numeric_filters["shedding"],
        grooming=numeric_filters["grooming"],
        apartment_friendly=numeric_filters["apartment_friendly"],
        novice_owner_friendly=numeric_filters["novice_owner_friendly"],
        children_friendly=numeric_filters["children_friendly"],
        good_with_other_dogs=numeric_filters["good_with_other_dogs"],
        good_with_strangers=numeric_filters["good_with_strangers"],
        energy=numeric_filters["energy"],
        exercise_needs=numeric_filters["exercise_needs"],
        playfulness=numeric_filters["playfulness"],
        trainability=numeric_filters["trainability"],
        barking=numeric_filters["barking"],
        cold_tolerance=numeric_filters["cold_tolerance"],
        heat_tolerance=numeric_filters["heat_tolerance"],
    )


def build_filter_payload(result: DogQueryMappingResult) -> dict:
    return {
        "include": {
            "colors": result.color_tags,
            "temperaments": result.temperament_tags,
        },
        "exclude": {
            "colors": result.negative_color_tags,
            "temperaments": result.negative_temperament_tags,
        },
        "numeric_filters": {
            "size_category": result.size_category,
            "shedding": result.shedding,
            "grooming": result.grooming,
            "apartment_friendly": result.apartment_friendly,
            "novice_owner_friendly": result.novice_owner_friendly,
            "children_friendly": result.children_friendly,
            "good_with_other_dogs": result.good_with_other_dogs,
            "good_with_strangers": result.good_with_strangers,
            "energy": result.energy,
            "exercise_needs": result.exercise_needs,
            "playfulness": result.playfulness,
            "trainability": result.trainability,
            "barking": result.barking,
            "cold_tolerance": result.cold_tolerance,
            "heat_tolerance": result.heat_tolerance,
        },
        "debug": {
            "colors_ko": result.colors_ko,
            "temperaments_ko": result.temperaments_ko,
            "negative_colors_ko": result.negative_colors_ko,
            "negative_temperaments_ko": result.negative_temperaments_ko,
            "color_groups": result.color_groups,
            "temperament_groups": result.temperament_groups,
            "negative_color_groups": result.negative_color_groups,
            "negative_temperament_groups": result.negative_temperament_groups,
        },
    }


def build_dog_breed_query(payload: dict, limit: int = 12) -> tuple[str, list]:
    hard_where = []
    exclude_where = []
    score_parts = []
    score_params = []
    where_params = []

    include = payload.get("include", {})
    exclude = payload.get("exclude", {})
    numeric = payload.get("numeric_filters", {})
    size_category = numeric.get("size_category")

    if size_category:
        hard_where.append("db.size_category = %s")
        where_params.append(size_category)
        score_parts.append("CASE WHEN db.size_category = %s THEN 20 ELSE 0 END")
        score_params.append(size_category)

    for tag in include.get("colors", []):
        tag = tag.lower()
        score_parts.append("CASE WHEN LOWER(db.colors) LIKE %s THEN 8 ELSE 0 END")
        score_params.append(f"%{tag}%")

    for tag in include.get("temperaments", []):
        tag = tag.lower()
        score_parts.append("CASE WHEN LOWER(db.temperament) LIKE %s THEN 10 ELSE 0 END")
        score_params.append(f"%{tag}%")

    for field, value in numeric.items():
        if value is None or field == "size_category" or field not in NUMERIC_FIELDS:
            continue

        operator = get_numeric_operator(int(value))
        score_parts.append(f"CASE WHEN db.{field} {operator} %s THEN 6 ELSE 0 END")
        score_params.append(value)

    for tag in exclude.get("colors", []):
        tag = tag.lower()
        exclude_where.append("LOWER(db.colors) NOT LIKE %s")
        where_params.append(f"%{tag}%")

    for tag in exclude.get("temperaments", []):
        tag = tag.lower()
        exclude_where.append("LOWER(db.temperament) NOT LIKE %s")
        where_params.append(f"%{tag}%")

    score_sql = " + ".join(score_parts) if score_parts else "0"
    where_parts = ["di.img IS NOT NULL", "di.img != ''"]

    if hard_where:
        where_parts.append("(" + " AND ".join(hard_where) + ")")

    if exclude_where:
        where_parts.append("(" + " AND ".join(exclude_where) + ")")

    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    sql = f"""
SELECT
    db.breed_key,
    di.img
FROM dog_breeds db
INNER JOIN dog_image di
    ON db.breed_key = di.breed_key
{where_sql}
ORDER BY ({score_sql}) DESC, db.breed_key ASC
LIMIT %s
"""

    return sql, score_params + where_params + [limit]


def get_numeric_operator(value: int) -> str:
    if value <= 2:
        return "<="
    return ">="


def apply_temperament_numeric_hints(
    temperament_groups: list[str],
    numeric_filters: dict,
) -> dict:
    result = dict(numeric_filters)

    for group in temperament_groups:
        hints = TEMPERAMENT_NUMERIC_HINTS.get(group)

        if not hints:
            continue

        for field, value in hints.items():
            if result.get(field) is None:
                result[field] = value

    return result


def dedupe(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []

    for item in items:
        item = str(item).strip().lower()
        if item and item not in seen:
            seen.add(item)
            result.append(item)

    return result


def expand_groups(groups: Iterable[str], group_to_tags: dict[str, list[str]]) -> list[str]:
    tags = []

    for group in groups:
        tags.extend(group_to_tags.get(group, []))

    return dedupe(tags)


def merge_phrases(values: Iterable[str]) -> str:
    return " ".join(dedupe(values))


def _fetch_rows(sql: str, params: list):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def _normalize_dog_row(row: dict, *, rank: int):
    breed_name = row.get("breed_key")

    return {
        "rank": rank,
        "kind": "dog",
        "breed_name": breed_name,
        "display_name": breed_name,
        "image_url": row.get("img"),
        "detail_route": _build_detail_route("dog", breed_name),
        "detail_api": _build_detail_api("dog", breed_name),
    }


def _public_filters(payload: dict):
    return {
        "include": payload.get("include", {}),
        "exclude": payload.get("exclude", {}),
        "numeric_filters": {
            key: value
            for key, value in payload.get("numeric_filters", {}).items()
            if value is not None
        },
    }


def _build_detail_route(kind: str, breed_name: str | None):
    if not breed_name:
        return None

    return f"/breeds/{kind}/{quote(str(breed_name), safe='')}"


def _build_detail_api(kind: str, breed_name: str | None):
    if not breed_name:
        return None

    return (
        "/api/detail/breeds/detail"
        f"?kind={quote(kind, safe='')}"
        f"&breed_name={quote(str(breed_name), safe='')}"
    )
