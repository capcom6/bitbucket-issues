import fastapi
from fastapi.responses import HTMLResponse

from .endpoints.api import router as api_router


router = fastapi.APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    with open("static/index.html", "r") as html:
        return HTMLResponse(content=html.read())


router.include_router(api_router, prefix="/api")
