import typing
import fastapi
from app import storage
from app.api.domain import Issue
from app.core.config import settings

from app.services.bitbucket import BitBucketService
from app.services.issues import IssuesService, Priority


router = fastapi.APIRouter()

bitbucket_svc = BitBucketService(
    settings.bitbucket.login,
    settings.bitbucket.password.get_secret_value(),
    settings.bitbucket.owner,
)
issues = storage.create_issues_repository(
    settings.storage.dsn, ttl=settings.storage.ttl
)
issues_svc = IssuesService(bitbucket_svc, issues)


@router.get(
    "/v1/issues",
    response_model=typing.List[Issue],
    tags=["Issues"],
    summary="Get issues",
    description="Returns issues with filter",
)
async def issues_get(
    priority: typing.Union[Priority, None] = None,
    assignee: typing.Union[str, None] = None,
):
    return await issues_svc.select(priority=priority, assignee=assignee)
