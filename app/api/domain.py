import datetime
import enum
import typing

import pydantic


class IssueState(enum.Enum):
    NEW = "new"
    OPEN = "open"
    ON_HOLD = "on hold"
    RESOLVED = "resolved"
    CLOSED = "closed"
    INVALID = "invalid"
    DUPLICATE = "duplicate"
    WONTFIX = "wontfix"


class IssuePriority(enum.Enum):
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class IssueKind(enum.Enum):
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    PROPOSAL = "proposal"
    TASK = "task"


class Link(pydantic.BaseModel):
    href: pydantic.HttpUrl


class Repository(pydantic.BaseModel):
    name: str
    uuid: str
    links: typing.Dict[str, Link]


class User(pydantic.BaseModel):
    uuid: str
    display_name: str
    nickname: str


class IssueContent(pydantic.BaseModel):
    type: str
    raw: str
    markup: str
    html: str


class Issue(pydantic.BaseModel):
    id: int
    title: str
    created_on: datetime.datetime
    updated_on: datetime.datetime
    state: IssueState
    kind: IssueKind
    priority: IssuePriority
    votes: int

    repository: Repository
    links: typing.Dict[str, Link]
    content: IssueContent
    reporter: User
    assignee: typing.Union[User, None]
