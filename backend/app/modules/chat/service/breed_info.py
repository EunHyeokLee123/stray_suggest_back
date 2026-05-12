import json
from urllib.parse import quote

from google.genai import types

from app.core.config import settings
from app.modules.chat.service.llm.google import GEMINI_MODEL, client, safe_parse_json
from app.modules.others.repository.find_db import find_breed_detail
from app.modules.others.util.cat_breed_mapper import (
    CAT_BREED_ALIASES,
    _normalize as normalize_cat_text,
    match_cat_breed,
)
from app.modules.others.util.dog_breed_mapper import (
    KO_TO_EN as DOG_KO_TO_EN,
    _ko_key as dog_ko_key,
    match_dog_breed,
)


def build_breed_info_from_text(user_text: str, filters: dict):
    match = _find_requested_breed(user_text, filters)

    if not match:
        return None
    
    detail = find_breed_detail(match["detail_kind"], match["mapped_breed"])

    if not detail:
        return {
            **match,
            "search_breed": filters.get("breed"),
            "detail": None,
            "summary": None,
            "detail_button": None,
            "message": "품종백과에서 해당 품종 상세 정보를 찾을 수 없습니다.",
        }

    summary = summarize_breed_detail(
        detail_kind=match["detail_kind"],
        requested_breed_name=match["requested_breed_name"],
        mapped_breed=match["mapped_breed"],
        detail=detail,
    )

    detail_route = _build_detail_route(match["detail_kind"], match["mapped_breed"])
    detail_api = _build_detail_api(match["detail_kind"], match["mapped_breed"])

    return {
        **match,
        "search_breed": filters.get("breed"),
        "detail_route": detail_route,
        "detail_api": detail_api,
        "detail_button": {
            "label": f"{match['requested_breed_name']} 상세정보 보기",
            "route": detail_route,
            "api": detail_api,
            "kind": match["detail_kind"],
            "breed_name": match["mapped_breed"],
        },
        "summary": summary,
        "detail": detail,
    }


def summarize_breed_detail(
    *,
    detail_kind: str,
    requested_breed_name: str,
    mapped_breed: str,
    detail: dict,
):
    if not detail:
        return None

    if not settings.gemini_api_key:
        return _fallback_summary(requested_breed_name, mapped_breed, detail)

    payload = {
        "kind": detail_kind,
        "requested_breed_name": requested_breed_name,
        "mapped_breed": mapped_breed,
        "detail": _compact_detail(detail),
    }

    system_prompt = """
너는 반려동물 품종백과 요약기다.
DB에서 가져온 품종 상세 JSON을 보고 프론트 검색 결과 상단 카드에 보여줄 값을 만든다.

규칙:
1. 반드시 JSON 객체 하나만 출력한다.
2. 한국어로 작성한다.
3. DB에 있는 사실만 사용하고, 없는 정보는 꾸며내지 않는다.
4. description은 5 ~ 6문장으로 쓴다.
5. highlights는 사용자가 빠르게 훑을 수 있는 핵심 특징 3~5개로 작성한다.
"""

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "highlights": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["title", "description", "highlights"],
    }

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=json.dumps(payload, ensure_ascii=False, default=str),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=schema,
                temperature=0,
                max_output_tokens=700,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except TypeError:
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=json.dumps(payload, ensure_ascii=False, default=str),
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0,
                    max_output_tokens=700,
                ),
            )
        except Exception:
            return _fallback_summary(requested_breed_name, mapped_breed, detail)
    except Exception:
        return _fallback_summary(requested_breed_name, mapped_breed, detail)

    data = safe_parse_json(response.text)

    if not data:
        return _fallback_summary(requested_breed_name, mapped_breed, detail)

    return {
        "title": data.get("title") or _display_name(requested_breed_name, mapped_breed, detail),
        "description": data.get("description") or "",
        "highlights": data.get("highlights") or [],
        "source": "llm",
    }


def _find_requested_breed(user_text: str, filters: dict):
    preferred_kinds = []

    if filters.get("kind") == "개":
        preferred_kinds = ["dog", "cat"]
    elif filters.get("kind") == "고양이":
        preferred_kinds = ["cat", "dog"]
    else:
        preferred_kinds = ["dog", "cat"]

    for detail_kind in preferred_kinds:
        match = _find_dog_breed(user_text) if detail_kind == "dog" else _find_cat_breed(user_text)

        if match:
            return {
                "requested_breed_name": match["requested_breed_name"],
                "detail_kind": detail_kind,
                "mapped_breed": match["mapped_breed"],
            }

    return None


def _find_dog_breed(user_text: str):
    compact_text = dog_ko_key(user_text)

    for alias, mapped_breed in sorted(
        DOG_KO_TO_EN.items(),
        key=lambda item: len(dog_ko_key(item[0])),
        reverse=True,
    ):
        alias_key = dog_ko_key(alias)

        if len(alias_key) >= 2 and alias_key in compact_text:
            return {
                "requested_breed_name": alias,
                "mapped_breed": mapped_breed,
            }

    mapped_breed = match_dog_breed(user_text)

    if mapped_breed:
        return {
            "requested_breed_name": mapped_breed,
            "mapped_breed": mapped_breed,
        }

    return None


def _find_cat_breed(user_text: str):
    normalized_text = normalize_cat_text(user_text)

    for alias, mapped_breed in sorted(
        CAT_BREED_ALIASES.items(),
        key=lambda item: len(normalize_cat_text(item[0])),
        reverse=True,
    ):
        alias_key = normalize_cat_text(alias)

        if len(alias_key) >= 2 and alias_key in normalized_text:
            return {
                "requested_breed_name": alias,
                "mapped_breed": mapped_breed,
            }

    mapped_breed = match_cat_breed(user_text)

    if mapped_breed:
        return {
            "requested_breed_name": mapped_breed,
            "mapped_breed": mapped_breed,
        }

    return None


def _compact_detail(detail: dict):
    excluded = {"img"}
    compacted = {}

    for key, value in detail.items():
        if key in excluded or value in [None, ""]:
            continue

        compacted[key] = value

    return compacted


def _fallback_summary(requested_breed_name: str, mapped_breed: str, detail: dict):
    title = _display_name(requested_breed_name, mapped_breed, detail)
    highlights = []

    for key, value in _compact_detail(detail).items():
        if key in {"breed_key", "name"}:
            continue

        highlights.append(f"{key}: {value}")

        if len(highlights) >= 5:
            break

    return {
        "title": title,
        "description": f"{title} 품종백과 정보를 기반으로 정리한 요약입니다.",
        "highlights": highlights,
        "source": "fallback",
    }


def _display_name(requested_breed_name: str, mapped_breed: str, detail: dict):
    return (
        requested_breed_name
        or detail.get("name")
        or detail.get("breed_key")
        or mapped_breed
    )


def _build_detail_route(detail_kind: str, mapped_breed: str):
    return f"/breeds/{detail_kind}/{quote(mapped_breed, safe='')}"


def _build_detail_api(detail_kind: str, mapped_breed: str):
    return (
        "/api/detail/breeds/detail"
        f"?kind={quote(detail_kind, safe='')}"
        f"&breed_name={quote(mapped_breed, safe='')}"
    )
