import fastapi

from app.core.config import settings


router = fastapi.APIRouter()


@router.get("/")
async def index():
    return {}


print(settings)
