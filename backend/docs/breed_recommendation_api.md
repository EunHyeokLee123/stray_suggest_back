# 품종 추천 API

## 강아지 품종 추천

`POST /api/animal/recommend/dog`

### Request

```json
{
  "text": "아파트에서 키우기 좋은 조용한 소형 강아지 추천해줘",
  "limit": 12,
  "use_llm": true,
  "include_debug": false
}
```

### Response

```json
{
  "kind": "dog",
  "query": "아파트에서 키우기 좋은 조용한 소형 강아지 추천해줘",
  "limit": 12,
  "filters": {
    "include": {
      "colors": [],
      "temperaments": ["quiet", "calm"]
    },
    "exclude": {
      "colors": [],
      "temperaments": []
    },
    "numeric_filters": {
      "size_category": "small",
      "apartment_friendly": 4,
      "energy": 2
    }
  },
  "recommendations": [
    {
      "rank": 1,
      "kind": "dog",
      "breed_name": "poodle",
      "display_name": "poodle",
      "image_url": "https://...",
      "detail_route": "/breeds/dog/poodle",
      "detail_api": "/api/detail/breeds/detail?kind=dog&breed_name=poodle"
    }
  ]
}
```

## 고양이 품종 추천

`POST /api/animal/recommend/cat`

### Request

```json
{
  "text": "털이 짧고 아이와 잘 지내는 고양이 추천해줘",
  "limit": 12,
  "use_llm": true,
  "include_debug": false
}
```

### Response

```json
{
  "kind": "cat",
  "query": "털이 짧고 아이와 잘 지내는 고양이 추천해줘",
  "limit": 12,
  "filters": {
    "name": null,
    "numeric_filters": {
      "grooming": 1,
      "shedding": 2,
      "family_friendly": 5,
      "children_friendly": 5
    },
    "negative_traits": []
  },
  "recommendations": [
    {
      "rank": 1,
      "kind": "cat",
      "breed_name": "American Shorthair",
      "display_name": "American Shorthair",
      "image_url": "https://...",
      "detail_route": "/breeds/cat/American%20Shorthair",
      "detail_api": "/api/detail/breeds/detail?kind=cat&breed_name=American%20Shorthair"
    }
  ]
}
```

## Request 필드

- `text`: 사용자 자연어 입력. 1~500자.
- `limit`: 추천 결과 개수. 1~50, 기본 12.
- `use_llm`: `true`면 Gemini로 조건을 구조화한다. 기본 `true`.
- `include_debug`: `true`면 LLM 추출/SQL/payload 디버그 정보를 포함한다. 화면단 기본값은 `false` 권장.

## 화면단 연동 포인트

- 추천 카드 이미지는 `recommendations[].image_url`을 사용한다.
- 상세정보 보기 버튼은 `recommendations[].detail_route`로 이동한다.
- 품종백과 상세 API를 직접 호출해야 하면 `recommendations[].detail_api`를 사용한다.
- 추천 목록 조회 SQL은 품종백과 목록조회처럼 `dog_image` / `cat_image`를 조인해서 이름과 이미지만 가져온다.
- 상세 데이터가 필요하면 목록 응답의 `detail_route`로 이동하거나 `detail_api`를 호출한다.
