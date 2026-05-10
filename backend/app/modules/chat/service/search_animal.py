from fastapi import HTTPException

from app.modules.chat.repository.common.schema import AnimalSearchTextRequest, AnimalSearchFilter
from app.modules.chat.repository.dog.dog_find import search_dogs
from app.modules.chat.repository.cat.cat_find import search_cats
from app.modules.chat.service.breed_info import build_breed_info_from_text
from app.modules.chat.service.llm.chat import extract_filters
from app.modules.chat.service.llm.google import extract_filters_google

is_google = True

def search_animals_by_text(payload: AnimalSearchTextRequest):
    if is_google :
        filters = extract_filters_google(
            user_text=payload.text,
            use_llm=payload.use_llm,
            verbose=False,
        )
    else :
        filters = extract_filters(
            user_text=payload.text,
            use_llm=payload.use_llm,
            verbose=False,
        )

    breed_info = build_breed_info_from_text(payload.text, filters)

    return search_animals_by_filter(filters, breed_info=breed_info)


def search_animals_by_filter(filters: dict, breed_info: dict | None = None):
    kind = filters.get("kind")

    if kind == "개":
        response = {
            "filters": filters,
            "results": search_dogs(filters),
        }

        if breed_info:
            response["breed_info"] = breed_info

        return response

    if kind == "고양이":
        response = {
            "filters": filters,
            "results": search_cats(filters),
        }

        if breed_info:
            response["breed_info"] = breed_info

        return response

    raise HTTPException(
        status_code=400,
        detail={
            "message": "개 또는 고양이를 판단할 수 없습니다.",
            "filters": filters,
        },
    )
