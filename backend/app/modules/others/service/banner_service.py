from fastapi import HTTPException
from math import ceil

from app.modules.others.repository.find_db import (
    find_breeds_by_page,
    PAGE_SIZE,
    find_breed_detail
)

import random
from app.modules.others.repository.banner_db import find_random_stray, find_random_detail

# 배너 조회
def get_stray_banner():

    # 1. dog / cat 랜덤 선택
    kind = random.choice(["dog", "cat"])

    # 2. DB 조회
    items = find_random_stray(kind)

    if not items:
        raise HTTPException(
            status_code=404,
            detail="배너 데이터를 찾을 수 없습니다."
        )

    return {
        "kind": kind,
        "count": len(items),
        "items": items
    }

# 배너 조회
def get_detail_banner():

    # 1. dog / cat 랜덤 선택
    kind = random.choice(["dog", "cat"])

    # 2. DB 조회
    items = find_random_detail(kind)

    if not items:
        raise HTTPException(
            status_code=404,
            detail="배너 데이터를 찾을 수 없습니다."
        )

    return {
        "kind": kind,
        "count": len(items),
        "items": items
    }