import datetime
import os
import typing

import dotenv
import pydantic
import yaml
from pydantic.env_settings import SettingsSourceCallable

dotenv.load_dotenv()


def yaml_config_settings_source(
    settings: pydantic.BaseSettings,
) -> typing.Dict[str, typing.Any]:
    encoding = settings.__config__.env_file_encoding
    filename = os.environ.get("CONFIG_FILE", "config.yml")
    if not os.path.exists(filename):
        return {}

    with open(filename, encoding=encoding) as f:
        return yaml.safe_load(f)


class BitBucket(pydantic.BaseModel):
    login: str
    password: pydantic.SecretStr
    owner: typing.Union[str, None]


class Issues(pydantic.BaseModel):
    repositories_filter: typing.Union[str, None] = pydantic.Field(
        "", alias="repositoriesFilter"
    )
    issues_filter: str = pydantic.Field(
        '(state = "new" OR state = "open" OR state = "on hold") AND (priority = "major" OR priority = "critical" OR priority = "blocker")',
        alias="issuesFilte",
    )


class StorageDsn(pydantic.AnyHttpUrl):
    __slots__ = ()
    allowed_schemes = {"memory", "redis", "rediss"}
    host_required = False


class Storage(pydantic.BaseModel):
    dsn: StorageDsn = pydantic.Field("memory://")
    ttl: datetime.timedelta = datetime.timedelta(hours=6)


class Settings(pydantic.BaseSettings):
    bitbucket: BitBucket
    issues: Issues = Issues()  # type: ignore
    storage: Storage = Storage()  # type: ignore

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        extra = "ignore"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> typing.Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                file_secret_settings,
                env_settings,
                yaml_config_settings_source,
            )


settings = Settings()  # type: ignore
