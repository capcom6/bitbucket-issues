import typing

import fastapi
from fastapi.responses import HTMLResponse

from app.api.domain import Issue
from app.core.config import settings
from app.services.bitbucket import BitBucketService
from app.services.issues import IssuesService, Priority

print(settings)
router = fastapi.APIRouter()
bitbucket_svc = BitBucketService(
    settings.bitbucket.login,
    settings.bitbucket.password.get_secret_value(),
    settings.bitbucket.owner,
)
issues_svc = IssuesService(bitbucket_svc)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    with open("static/index.html", "r") as html:
        return HTMLResponse(content=html.read())


@router.get(
    "/api/v1/issues",
    response_model=typing.List[Issue],
    tags=["Issues"],
    summary="Get issues",
    description="Returns issues with filter",
)
async def issues(
    priority: typing.Union[Priority, None] = None,
    assignee: typing.Union[str, None] = None,
    *,
    tasks: fastapi.BackgroundTasks
):
    return await issues_svc.select(priority=priority, assignee=assignee)
