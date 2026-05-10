from fastapi import APIRouter

from app.modules.chat.router.router import router as animals_router
from app.modules.others.router.router import router as detail_router

gateway_router = APIRouter()

gateway_router.include_router(animals_router)
gateway_router.include_router(detail_router)