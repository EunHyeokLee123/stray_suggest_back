from fastapi import APIRouter, Query

from app.modules.others.service.detail_service import get_breed_page, get_breed_detail, get_detail
from app.modules.others.service.banner_service import get_detail_banner, get_stray_banner

router = APIRouter(prefix="/detail", tags=["detail"])

# 품종 페이지 조회 API
@router.get("/breeds")
def get_breeds(
    kind: str = Query(..., description="dog or cat"),
    page: int = Query(1, ge=1)
):
    return get_breed_page(kind, page)

# 품종 검색조회
@router.get("/breeds/search")
def get_breed_search(
    kind: str = Query(..., description="dog 또는 cat"),
    breed_name: str = Query(..., description="검색할 세부종 이름")
):
    return get_breed_detail(kind, breed_name)

# 목록에서 클릭을 통한 상세조회
# 이건 매핑따로 안함. -> 프론트에서 올바른 값만 넘겨줄 것이기 때문
@router.get("/breeds/detail")
def get_breed_details(
    kind: str = Query(..., description="dog 또는 cat"),
    breed_name: str = Query(..., description="검색할 세부종 이름")
):
    return get_detail(kind, breed_name)

# 유기동물 아이들 배너 목록 조회
# 이건 클릭하면 냥몽 사이트로 넘어가게 하자.
@router.get("/banner/stray")
def get_stray():
    return get_stray_banner()

# 품종정보 보여주는 배너 목록 조회
# 이건 클릭하면 kind랑 items에 있는 breed_key또는 name을 넣어서
# get_breed_details 호출하게 하자.
@router.get("/banner/detail")
def get_banner_detail():
    return get_detail_banner()