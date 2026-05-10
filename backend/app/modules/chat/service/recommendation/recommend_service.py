from app.modules.chat.repository.common.schema import BreedRecommendationRequest
from app.modules.chat.service.recommendation.cat import search_cat_breed_recommendations
from app.modules.chat.service.recommendation.dog import search_dog_breed_recommendations


def recommend_dog_breeds(payload: BreedRecommendationRequest):
    return search_dog_breed_recommendations(
        payload.text,
        limit=payload.limit,
        use_llm=payload.use_llm,
        include_debug=payload.include_debug,
    )


def recommend_cat_breeds(payload: BreedRecommendationRequest):
    return search_cat_breed_recommendations(
        payload.text,
        limit=payload.limit,
        use_llm=payload.use_llm,
        include_debug=payload.include_debug,
    )
