from dataclasses import asdict, is_dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Optional, Union, cast

from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass, \
    is_builtin_dataclass
from pydantic.schema import model_schema
from flask import Response, request
from werkzeug.datastructures import Headers
from werkzeug.exceptions import BadRequest

from .constants import SCHEMA_QUERYSTRING_ATTRIBUTE, \
    SCHEMA_REQUEST_ATTRIBUTE, SCHEMA_RESPONSE_ATTRIBUTE
from .typing import PydanticModel, ResponseReturnValue


class SchemaInvalidError(Exception):
    pass


class ResponseSchemaValidationError(Exception):
    def __init__(
        self,
        validation_error: Optional[ValidationError] = None
    ) -> None:
        self.validation_error = validation_error


class RequestSchemaValidationError(BadRequest):
    def __init__(
        self,
        validation_error: Union[TypeError, ValidationError]
    ) -> None:
        super().__init__()
        self.validation_error = validation_error


class DataSource(Enum):
    FORM = auto()
    JSON = auto()


def validate_querystring(model_class: PydanticModel) -> Callable:
    if is_builtin_dataclass(model_class):
        model_class = pydantic_dataclass(model_class)

    schema = model_schema(model_class)

    if len(schema.get("required", [])) != 0:
        raise SchemaInvalidError("Fields must be optional")

    def decorator(func: Callable) -> Callable:
        setattr(func, SCHEMA_QUERYSTRING_ATTRIBUTE, model_class)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                model = model_class(**request.args)
            except (TypeError, ValidationError) as error:
                raise RequestSchemaValidationError(error)
            else:
                return func(*args, query_args=model, **kwargs)

        return wrapper

    return decorator


def validate_request(
    model_class: PydanticModel,
    *,
    source: DataSource = DataSource.JSON,
) -> Callable:
    if is_builtin_dataclass(model_class):
        model_class = pydantic_dataclass(model_class)

    schema = model_schema(model_class)
    if source == DataSource.FORM and any(
        schema["properties"][field]["type"] == "object" for field in
            schema["properties"]
    ):
        raise SchemaInvalidError("Form must not have nested objects")

    def decorator(func: Callable) -> Callable:
        setattr(func, SCHEMA_REQUEST_ATTRIBUTE, (model_class, source))

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            data = request.get_json() if source == DataSource.JSON else request.form  # noqa
            try:
                model = model_class(**data)
            except (TypeError, ValidationError) as error:
                raise RequestSchemaValidationError(error)
            else:
                return func(*args, data=model, **kwargs)

        return wrapper

    return decorator


def validate_response(
    model_class: PydanticModel,
    status_code: int = 200
) -> Callable:
    if is_builtin_dataclass(model_class):
        model_class = pydantic_dataclass(model_class)

    def decorator(
        func: Callable[..., ResponseReturnValue]
    ) -> Callable[..., Response]:
        schemas = getattr(func, SCHEMA_RESPONSE_ATTRIBUTE, {})
        schemas[status_code] = model_class
        setattr(func, SCHEMA_RESPONSE_ATTRIBUTE, schemas)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            status_or_headers = None
            headers = None
            if isinstance(result, tuple):
                value, status_or_headers, headers = result + (None,) * (
                    3 - len(result))
            else:
                value = result

            status = 200
            if status_or_headers is not None and not isinstance(
                status_or_headers, (Headers, dict, list)
            ):
                status = int(status_or_headers)

            if status == status_code:
                if isinstance(value, dict):
                    try:
                        model_value = model_class(**value)
                    except ValidationError as error:
                        raise ResponseSchemaValidationError(error)
                elif type(value) == model_class:
                    model_value = value
                elif is_builtin_dataclass(value):
                    model_value = model_class(**asdict(value))
                else:
                    raise ResponseSchemaValidationError()
                if is_dataclass(model_value):
                    return asdict(model_value), status_or_headers, headers
                else:
                    model_value = cast(BaseModel, model_value)
                    return model_value.dict(), status_or_headers, headers
            else:
                return result

        return wrapper

    return decorator
