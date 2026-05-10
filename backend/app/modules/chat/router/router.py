from fastapi import APIRouter

from app.modules.chat.repository.common.schema import (
    AnimalSearchFilter,
    AnimalSearchTextRequest,
    BreedRecommendationRequest,
)
from app.modules.chat.service.recommendation.recommend_service import (
    recommend_cat_breeds,
    recommend_dog_breeds,
)
from app.modules.chat.service.search_animal import search_animals_by_filter, search_animals_by_text

router = APIRouter(prefix="/animal", tags=["animal"])

# 검색어를 입력해서 유기동물을 찾음
@router.post("/search")
def search_by_text(payload: AnimalSearchTextRequest):
    return search_animals_by_text(payload)

# 필터버튼을 통해 이미 정해진값을 받아서 유기동물을 찾음
@router.post("/search/filter")
def search_by_filter(payload: AnimalSearchFilter):
    return search_animals_by_filter(payload.model_dump())

# llm을 통한 강아지 품종 추천
@router.post("/recommend/dog")
def recommend_dog(payload: BreedRecommendationRequest):
    return recommend_dog_breeds(payload)

# llm을 통한 고양이 품종 추천
@router.post("/recommend/cat")
def recommend_cat(payload: BreedRecommendationRequest):
    return recommend_cat_breeds(payload)
