from enum import Enum, auto
from typing import Callable, Dict, Iterable, Union

from pydantic.dataclasses import dataclass as pydantic_dataclass, \
    is_builtin_dataclass
from pydantic.schema import model_schema

from schema_validator.constants import SCHEMA_TAG_ATTRIBUTE
from schema_validator.types import PydanticModel


class SchemaInvalidError(Exception):
    pass


class DataSource(Enum):
    FORM = auto()
    JSON = auto()


def check_query_string_schema(query_string: PydanticModel) -> PydanticModel:
    if is_builtin_dataclass(query_string):
        query_string = pydantic_dataclass(query_string).__pydantic_model__
    return query_string


def check_body_schema(
    body: PydanticModel,
    source: DataSource
) -> PydanticModel:
    if is_builtin_dataclass(body):
        body = pydantic_dataclass(body).__pydantic_model__

    schema = model_schema(body)
    if source == DataSource.FORM and any(
        schema["properties"][field]["type"] == "object" for field in
            schema["properties"]
    ):
        raise SchemaInvalidError("Form must not have nested objects")
    return body


def check_response_schema(
    responses: Union[PydanticModel, Dict]
) -> Dict[int, PydanticModel]:
    if not isinstance(responses, dict):
        if is_builtin_dataclass(responses):
            responses = pydantic_dataclass(responses).__pydantic_model__
        responses = {200: responses}

    for status_code, v in responses.items():
        try:
            code = int(status_code)
        except BaseException as e:
            raise ValueError(f"invalid status_code: {status_code}, {str(e)}")
        if is_builtin_dataclass(v):
            responses[code] = pydantic_dataclass(v).__pydantic_model__

    return responses


def tags(*tags: Iterable[str]) -> Callable:
    """Add tag names to the route."""

    def decorator(func: Callable) -> Callable:
        setattr(func, SCHEMA_TAG_ATTRIBUTE, list(set(tags)))
        return func

    return decorator
