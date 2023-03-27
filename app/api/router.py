import typing

import fastapi

from app.core.config import settings
from app.services.bitbucket import BitBucketService
from app.services.issues import IssuesService, Priority

router = fastapi.APIRouter()
bitbucket_svc = BitBucketService(
    settings.bitbucket.login,
    settings.bitbucket.password.get_secret_value(),
    settings.bitbucket.owner,
)
issues_svc = IssuesService(bitbucket_svc)


@router.get("/")
async def index():
    return {}


@router.get("/issues")
async def issues(
    priority: typing.Union[Priority, None] = None,
    assignee: typing.Union[str, None] = None,
):
    return await issues_svc.select(priority=priority, assignee=assignee)
