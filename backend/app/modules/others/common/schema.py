from pydantic import BaseModel, Field
from typing import Literal


class BreedPageResponse(BaseModel):
    kind: Literal["dog", "cat"]
    page: int
    size: int
    items: list[dict]