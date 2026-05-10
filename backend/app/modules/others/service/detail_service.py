from fastapi import HTTPException
from math import ceil
from deep_translator import GoogleTranslator
from app.modules.others.repository.find_db import (
    find_breeds_by_page,
    PAGE_SIZE,
    find_breed_detail
)
from app.modules.others.util.cat_breed_mapper import match_cat_breed
from app.modules.others.util.dog_breed_mapper import match_dog_breed

# 품종 페이지 조회
def get_breed_page(kind: str, page: int):

    if kind not in ["dog", "cat"]:
        raise HTTPException(
            status_code=400,
            detail="kind는 'dog' 또는 'cat'만 가능합니다."
        )

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="page는 1 이상이어야 합니다."
        )

    result = find_breeds_by_page(kind, page)

    total_items = result["total_items"]
    total_pages = ceil(total_items / PAGE_SIZE) if total_items > 0 else 0

    return {
        "kind": kind,
        "page": page,
        "size": PAGE_SIZE,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "items": result["items"],
    }

def get_breed_detail(kind: str, breed_name: str):
    if kind not in ["dog", "cat"]:
        raise HTTPException(
            status_code=400,
            detail="kind는 dog 또는 cat만 가능합니다."
        )

    if not breed_name or not breed_name.strip():
        raise HTTPException(
            status_code=400,
            detail="breed_name을 입력해주세요."
        )

    if kind == "dog":
        mapped_breed = match_dog_breed(breed_name)

    else:
        mapped_breed = match_cat_breed(breed_name)

    if not mapped_breed:
        raise HTTPException(
            status_code=404,
            detail="해당 세부종을 찾을 수 없습니다."
        )
    
    detail = find_breed_detail(kind, mapped_breed)

    if not detail:
        raise HTTPException(
            status_code=404,
            detail={
            "message": "DB에서 해당 세부종 정보를 찾을 수 없습니다.",
            "breed_name": breed_name,
            "mapped_breed": mapped_breed,
            },
        )

    if kind == "dog":
        converted_detail = convert_dog_detail_for_ko_display(detail)
    else:
        converted_detail = convert_cat_detail_for_ko_display(detail)

    return {
        "kind": kind,
        "input": breed_name,
        "mapped_breed": mapped_breed,
        "detail": converted_detail,
    }

def get_detail(kind: str, breeds: str):
    if kind not in ["dog", "cat"]:
        raise HTTPException(
            status_code=400,
            detail="kind는 dog 또는 cat만 가능합니다."
        )

    if not breeds or not breeds.strip():
        raise HTTPException(
            status_code=400,
            detail="breed_name을 입력해주세요."
        )
    
    detail = find_breed_detail(kind, breeds)

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="DB에서 해당 세부종 정보를 찾을 수 없습니다."
        )

    if kind == "dog":
        converted_detail = convert_dog_detail_for_ko_display(detail)
    else:
        converted_detail = convert_cat_detail_for_ko_display(detail)

    return {
        "kind": kind,
        "input": breeds,
        "mapped_breed": breeds,
        "detail": converted_detail,
    }

def inch_to_meter(value):
    return round(value * 0.0254, 2)


def pound_to_kg(value):
    return round(value * 0.45359237, 1)


def avg(*values):
    valid_values = [v for v in values if v is not None]

    if not valid_values:
        return None

    return sum(valid_values) / len(valid_values)


def format_score(value):
    if value is None:
        return None

    value = int(value)

    filled_star = "★" * value
    empty_star = "☆" * (5 - value)

    return f"{filled_star}{empty_star}"


def convert_dog_detail_for_ko_display(detail: dict) -> dict:
    avg_life = avg(
        detail.get("min_life_expectancy"),
        detail.get("max_life_expectancy"),
    )

    avg_height_inch = avg(
        detail.get("min_height_female"),
        detail.get("max_height_female"),
        detail.get("min_height_male"),
        detail.get("max_height_male"),
    )

    avg_weight_lb = avg(
        detail.get("min_weight_female"),
        detail.get("max_weight_female"),
        detail.get("min_weight_male"),
        detail.get("max_weight_male"),
    )

    display_detail = {
        "품종명": detail.get("name"),

        "설명": detail.get("description"),
        "성격": detail.get("temperament"),
        "견종 역할": detail.get("breed_function"),
        "원산지": detail.get("origin"),

        "크기": sizeNormalize(detail.get("size_category")),
        "평균 수명": f"{round(avg_life, 1)}년" if avg_life is not None else None,
        "평균 신장": f"{inch_to_meter(avg_height_inch)}m" if avg_height_inch is not None else None,
        "평균 체중": f"{pound_to_kg(avg_weight_lb)}kg" if avg_weight_lb is not None else None,

        "털 길이": format_score(detail.get("coat_length")),
        "털 종류": detail.get("coat_type"),
        "털 색상": detail.get("colors"),
        "털 빠짐": format_score(detail.get("shedding")),
        "미용 관리 난이도": format_score(detail.get("grooming")),

        "아파트 생활 적합도": format_score(detail.get("apartment_friendly")),
        "초보 보호자 적합도": format_score(detail.get("novice_owner_friendly")),
        "아이 친화도": format_score(detail.get("children_friendly")),
        "다른 개와의 친화도": format_score(detail.get("good_with_other_dogs")),
        "낯선 사람 친화도": format_score(detail.get("good_with_strangers")),

        "에너지 수준": format_score(detail.get("energy")),
        "운동 필요량": format_score(detail.get("exercise_needs")),
        "장난기": format_score(detail.get("playfulness")),
        "훈련 쉬움": format_score(detail.get("trainability")),

        "짖음 정도": format_score(detail.get("barking")),
        "침 흘림": format_score(detail.get("drooling")),
        "사냥 본능": format_score(detail.get("prey_drive")),
        "보호 본능": format_score(detail.get("protectiveness")),

        "추위 적응력": format_score(detail.get("cold_tolerance")),
        "더위 적응력": format_score(detail.get("heat_tolerance")),
        "img": detail.get("img"),
        # 표 하단에 작게 보여줄 용도
        "출처 URL": detail.get("source_url"),
    }

    return {
        key: value
        for key, value in display_detail.items()
        if value is not None
    }

def convert_cat_detail_for_ko_display(detail: dict) -> dict:
    avg_life = avg(
        detail.get("min_life_expectancy"),
        detail.get("max_life_expectancy"),
    )

    avg_weight_lb = avg(
        detail.get("min_weight"),
        detail.get("max_weight"),
    )

    display_detail = {
        "품종명": detail.get("name"),

        "원산지": detail.get("origin"),
        "털 길이": detail.get("length"),

        "크기": catSizeNormalize(detail.get("length")),

        "평균 수명": (
            f"{round(avg_life, 1)}년"
            if avg_life is not None
            else None
        ),

        "평균 체중": (
            f"{pound_to_kg(avg_weight_lb)}kg"
            if avg_weight_lb is not None
            else None
        ),

        "아이 친화도": format_score(
            detail.get("children_friendly")
        ),

        "가족 친화도": format_score(
            detail.get("family_friendly")
        ),

        "다른 반려동물 친화도": format_score(
            detail.get("other_pets_friendly")
        ),

        "건강 관리": format_score(
            detail.get("general_health")
        ),

        "지능": format_score(
            detail.get("intelligence")
        ),

        "장난기": format_score(
            detail.get("playfulness")
        ),

        "털 빠짐": format_score(
            detail.get("shedding")
        ),

        "미용 관리 난이도": format_score(
            detail.get("grooming")
        ),

        # 프론트 이미지용
        "img": detail.get("img"),
    }

    return {
        key: value
        for key, value in display_detail.items()
        if value is not None
    }

def sizeNormalize(input: str) :
    if input == 'toy' :
        return "소형"
    elif input == 'small':
        return "소형에서 중형"
    elif input == 'medium':
        return "중형"
    elif input == 'large':
        return "중형에서 대형"
    elif input == 'giant':
        return "대형"
    
def catSizeNormalize(input: str):
    if input == 'Small' :
        return "소형"
    elif input == 'Small to medium':
        return "소형에서 중형"
    elif input == 'Medium':
        return "중형"
    elif input == 'Medium to large':
        return "중형에서 대형"
    elif input == 'Large':
        return "대형"