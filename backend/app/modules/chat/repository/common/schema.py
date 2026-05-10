from pydantic import BaseModel, Field, field_validator
import re


class AnimalSearchTextRequest(BaseModel):
    text: str
    use_llm: bool = True

    text: str = Field(..., min_length=1, max_length=300)
    use_llm: bool = True

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str):
        value = value.strip()
        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
        return value


class AnimalSearchFilter(BaseModel):
    sido: str | None = None
    kind: str | None = None
    breed: str | list[str] | None = None
    colors: list[str] = []


class BreedRecommendationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=12, ge=1, le=50)
    use_llm: bool = True
    include_debug: bool = False

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str):
        value = value.strip()
        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
        return value
