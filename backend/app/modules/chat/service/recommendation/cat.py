from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal
from urllib.parse import quote

from google.genai import types
from pydantic import BaseModel, Field

from app.modules.chat.repository.connector.mysql import get_mysql_connection
from app.modules.chat.service.llm.google import GEMINI_MODEL, client, safe_parse_json
from app.modules.others.util.cat_breed_mapper import match_cat_breed


NUMERIC_FIELDS = {
    "shedding",
    "playfulness",
    "other_pets_friendly",
    "intelligence",
    "grooming",
    "general_health",
    "family_friendly",
    "children_friendly",
}

CAT_TRAIT_NUMERIC_HINTS = {
    "장모": {"grooming": 5, "shedding": 4},
    "긴 털": {"grooming": 5, "shedding": 4},
    "털이 긴": {"grooming": 5, "shedding": 4},
    "풍성한 털": {"grooming": 5, "shedding": 4},
    "복슬복슬": {"grooming": 4, "shedding": 4},
    "털 많은": {"shedding": 5, "grooming": 4},
    "털이 많이 빠지는": {"shedding": 5},
    "털빠짐 심한": {"shedding": 5},
    "털이 적게 빠지는": {"shedding": 2},
    "털이 안 빠지는": {"shedding": 1},
    "털 관리 쉬운": {"grooming": 1},
    "관리 쉬운": {"grooming": 1},
    "빗질 자주 필요한": {"grooming": 5},
    "단모": {"grooming": 1, "shedding": 2},
    "짧은 털": {"grooming": 1, "shedding": 2},
    "털이 짧은": {"grooming": 1, "shedding": 2},
    "장난기": {"playfulness": 5},
    "장난기 많은": {"playfulness": 5},
    "애교 많은": {"playfulness": 4, "family_friendly": 5},
    "활발한": {"playfulness": 5},
    "엄청 활발한": {"playfulness": 5},
    "에너지 넘치는": {"playfulness": 5},
    "놀기 좋아하는": {"playfulness": 5},
    "호기심 많은": {"playfulness": 4, "intelligence": 4},
    "뛰어다니는 걸 좋아하는": {"playfulness": 5},
    "얌전한": {"playfulness": 2},
    "조용한": {"playfulness": 1},
    "차분한": {"playfulness": 2},
    "온순한": {"playfulness": 2, "family_friendly": 4},
    "독립적인": {"playfulness": 2},
    "똑똑한": {"intelligence": 5},
    "영리한": {"intelligence": 5},
    "머리 좋은": {"intelligence": 5},
    "학습 능력이 좋은": {"intelligence": 5},
    "훈련이 쉬운": {"intelligence": 4},
    "말을 잘 듣는": {"intelligence": 4},
    "가족과 잘 지내는": {"family_friendly": 5},
    "가족 친화적인": {"family_friendly": 5},
    "사람 좋아하는": {"family_friendly": 5},
    "사교적인": {"family_friendly": 5, "other_pets_friendly": 4},
    "아이와 잘 지내는": {"children_friendly": 5, "family_friendly": 5},
    "아이 친화적인": {"children_friendly": 5},
    "아이를 좋아하는": {"children_friendly": 5},
    "순한": {"children_friendly": 4, "family_friendly": 4},
    "다른 고양이와 잘 지내는": {"other_pets_friendly": 5},
    "다른 강아지와 잘 지내는": {"other_pets_friendly": 5},
    "다른 동물과 잘 지내는": {"other_pets_friendly": 5},
    "합사가 쉬운": {"other_pets_friendly": 5},
    "사회성 좋은": {"other_pets_friendly": 4, "family_friendly": 5},
    "건강한": {"general_health": 5},
    "튼튼한": {"general_health": 5},
    "잔병치레 없는": {"general_health": 5},
    "병치레 적은": {"general_health": 5},
    "관리 편한": {"general_health": 4, "grooming": 2},
    "너무 활발하지 않은": {"playfulness": 2},
    "조용했으면 좋겠는": {"playfulness": 1},
    "털 안 날리는": {"shedding": 1},
    "털날림 적은": {"shedding": 2},
    "손이 많이 안 가는": {"grooming": 1, "general_health": 4},
}


class CatSearchIntent(BaseModel):
    name: str | None = None
    length: Literal[
        "Small",
        "Small to medium",
        "Medium",
        "Medium to large",
        "Large",
    ] | None = None
    shedding: int | None = Field(default=None, ge=1, le=5)
    playfulness: int | None = Field(default=None, ge=1, le=5)
    other_pets_friendly: int | None = Field(default=None, ge=1, le=5)
    intelligence: int | None = Field(default=None, ge=1, le=5)
    grooming: int | None = Field(default=None, ge=1, le=5)
    general_health: int | None = Field(default=None, ge=1, le=5)
    family_friendly: int | None = Field(default=None, ge=1, le=5)
    children_friendly: int | None = Field(default=None, ge=1, le=5)
    negative_traits: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class CatQueryResult:
    original_input: str
    name: str | None
    length: str | None
    shedding: int | None
    playfulness: int | None
    other_pets_friendly: int | None
    intelligence: int | None
    grooming: int | None
    general_health: int | None
    family_friendly: int | None
    children_friendly: int | None
    negative_traits: list[str]


def search_cat_breed_recommendations(
    user_input: str,
    *,
    limit: int = 12,
    use_llm: bool = True,
    include_debug: bool = False,
):
    query = extract_cat_query(user_input, use_llm=use_llm)
    payload = build_filter_payload(query)
    sql, params = build_cat_breed_query(payload, limit=limit)
    rows = _fetch_rows(sql, params)

    response = {
        "kind": "cat",
        "query": user_input,
        "limit": limit,
        "filters": _public_filters(payload),
        "recommendations": [
            _normalize_cat_row(row, rank=index + 1)
            for index, row in enumerate(rows)
        ],
    }

    if include_debug:
        response["debug"] = {
            "query_result": asdict(query),
            "payload": payload,
            "sql": sql,
            "params": params,
        }

    return response


def extract_cat_query(user_input: str, *, use_llm: bool = True) -> CatQueryResult:
    if use_llm:
        parsed = extract_cat_intent_with_gemini(user_input)
    else:
        parsed = CatSearchIntent()

    mapped_name = _resolve_cat_name(parsed.name, user_input)

    numeric_filters = {
        "shedding": parsed.shedding,
        "playfulness": parsed.playfulness,
        "other_pets_friendly": parsed.other_pets_friendly,
        "intelligence": parsed.intelligence,
        "grooming": parsed.grooming,
        "general_health": parsed.general_health,
        "family_friendly": parsed.family_friendly,
        "children_friendly": parsed.children_friendly,
    }

    numeric_filters = apply_cat_trait_numeric_hints(user_input, numeric_filters)

    return CatQueryResult(
        original_input=user_input,
        name=mapped_name,
        length=parsed.length,
        shedding=numeric_filters["shedding"],
        playfulness=numeric_filters["playfulness"],
        other_pets_friendly=numeric_filters["other_pets_friendly"],
        intelligence=numeric_filters["intelligence"],
        grooming=numeric_filters["grooming"],
        general_health=numeric_filters["general_health"],
        family_friendly=numeric_filters["family_friendly"],
        children_friendly=numeric_filters["children_friendly"],
        negative_traits=parsed.negative_traits,
    )


def extract_cat_intent_with_gemini(user_input: str) -> CatSearchIntent:
    system_prompt = """
너는 고양이 품종 추천 조건 추출기다.

목표:
사용자의 한국어 입력에서 고양이 품종 추천 조건만 추출한다.

중요 규칙:
- 사용자가 명시하거나 강하게 암시한 조건만 추출한다.
- 근거 없는 값은 절대 추측하지 않는다.
- 값이 없으면 null 사용.
- 반드시 JSON만 출력.

name:
- 사용자가 특정 품종명을 말한 경우만 채운다.
- 가능하면 영어 품종명으로 쓴다. 예: 랙돌 -> Ragdoll Cats, 샴 -> Siamese Cat.

length 규칙:
반드시 아래 값 중 하나만 사용:
- Small
- Small to medium
- Medium
- Medium to large
- Large

크기 매핑:
- 아주 작은 / 초소형 -> Small
- 작은 / 소형 -> Small
- 중간 / 보통 -> Medium
- 약간 큰 / 중대형 -> Medium to large
- 큰 / 대형 -> Large

숫자 필드 규칙:
1 = 매우 낮음
2 = 낮음
3 = 보통
4 = 높음
5 = 매우 높음

필드 해석:
- shedding: 털빠짐 정도. "털이 거의 안 빠짐"=1, "털 많이 빠짐"=5
- playfulness: 장난기. "장난 많음"=5, "얌전함"=1~2
- other_pets_friendly: 다른 반려동물 친화도. "다른 고양이/강아지와 잘 지냄"=4~5
- intelligence: 지능. "영리함", "똑똑함"=4~5
- grooming: 미용관리 난이도. "관리 쉬움"=1~2, "빗질 자주 필요"=4~5
- general_health: 건강함. "튼튼함", "건강한 품종"=4~5
- family_friendly: 가족 친화도. "가족과 잘 지냄"=4~5
- children_friendly: 아이 친화도. "아이와 잘 지냄"=4~5

negative_traits:
사용자가 원하지 않는 특성을 한국어로 넣는다.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_input,
        config=types.GenerateContentConfig(
            temperature=0.1,
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=CatSearchIntent,
        ),
    )

    parsed = getattr(response, "parsed", None)

    if isinstance(parsed, CatSearchIntent):
        return parsed

    if isinstance(parsed, dict):
        return CatSearchIntent.model_validate(parsed)

    return CatSearchIntent.model_validate(safe_parse_json(response.text))


def build_filter_payload(result: CatQueryResult) -> dict:
    return {
        "name": result.name,
        "numeric_filters": {
            "length": result.length,
            "shedding": result.shedding,
            "playfulness": result.playfulness,
            "other_pets_friendly": result.other_pets_friendly,
            "intelligence": result.intelligence,
            "grooming": result.grooming,
            "general_health": result.general_health,
            "family_friendly": result.family_friendly,
            "children_friendly": result.children_friendly,
        },
        "negative_traits": result.negative_traits,
        "debug": asdict(result),
    }


def build_cat_breed_query(payload: dict, limit: int = 12) -> tuple[str, list]:
    score_parts = []
    params = []
    name = payload.get("name")
    numeric = payload.get("numeric_filters", {})

    if name:
        name_value = f"%{name.lower()}%"
        score_parts.append("CASE WHEN LOWER(cb.name) LIKE %s THEN 30 ELSE 0 END")
        params.append(name_value)

    length = numeric.get("length")

    if length:
        score_parts.append("CASE WHEN cb.length = %s THEN 20 ELSE 0 END")
        params.append(length)

    for field in NUMERIC_FIELDS:
        value = numeric.get(field)

        if value is None:
            continue

        operator = get_numeric_operator(int(value))
        score_parts.append(f"CASE WHEN cb.{field} {operator} %s THEN 8 ELSE 0 END")
        params.append(value)

    score_sql = " + ".join(score_parts) if score_parts else "0"

    sql = f"""
SELECT
    cb.name,
    ci.img
FROM cat_breeds cb
INNER JOIN cat_image ci
    ON cb.name = ci.breed_key
WHERE ci.img IS NOT NULL
AND ci.img != ''
ORDER BY ({score_sql}) DESC, cb.name ASC
LIMIT %s
"""

    return sql, params + [limit]


def get_numeric_operator(value: int) -> str:
    if value <= 2:
        return "<="
    return ">="


def apply_cat_trait_numeric_hints(user_input: str, numeric_filters: dict) -> dict:
    result = dict(numeric_filters)
    normalized_input = user_input.replace(" ", "")

    for phrase, hints in CAT_TRAIT_NUMERIC_HINTS.items():
        normalized_phrase = phrase.replace(" ", "")

        if normalized_phrase not in normalized_input:
            continue

        for field, value in hints.items():
            if result.get(field) is None:
                result[field] = value

    return result


def _resolve_cat_name(parsed_name: str | None, user_input: str):
    if parsed_name:
        return match_cat_breed(parsed_name) or parsed_name

    return match_cat_breed(user_input)


def _fetch_rows(sql: str, params: list):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def _normalize_cat_row(row: dict, *, rank: int):
    breed_name = row.get("name")

    return {
        "rank": rank,
        "kind": "cat",
        "breed_name": breed_name,
        "display_name": breed_name,
        "image_url": row.get("img"),
        "detail_route": _build_detail_route("cat", breed_name),
        "detail_api": _build_detail_api("cat", breed_name),
    }


def _public_filters(payload: dict):
    return {
        "name": payload.get("name"),
        "numeric_filters": {
            key: value
            for key, value in payload.get("numeric_filters", {}).items()
            if value is not None
        },
        "negative_traits": payload.get("negative_traits", []),
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
