from dataclasses import asdict, is_dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, cast

from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass, \
    is_builtin_dataclass
from pydantic.schema import model_schema
from flask import Response, jsonify, request, g
from werkzeug.datastructures import Headers
from werkzeug.exceptions import BadRequest

from .constants import SCHEMA_QUERYSTRING_ATTRIBUTE, \
    SCHEMA_REQUEST_ATTRIBUTE, SCHEMA_RESPONSE_ATTRIBUTE
from .typing import PydanticModel


class SchemaInvalidError(Exception):
    pass


class DataSource(Enum):
    FORM = auto()
    JSON = auto()


def check_query_string_schema(query_string: PydanticModel) -> PydanticModel:
    if is_builtin_dataclass(query_string):
        query_string = pydantic_dataclass(query_string).__pydantic_model__
    query_string_schema = model_schema(query_string)
    if len(query_string_schema.get("required", [])) != 0:
        raise SchemaInvalidError("Fields must be optional")
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

    for k, v in responses.items():
        if is_builtin_dataclass(v):
            responses[k] = pydantic_dataclass(v).__pydantic_model__

    return responses


def check_response(result, response_model: Dict[int, PydanticModel]):
    status_or_headers: Union[None, int, str, Dict, list] = None
    headers: Optional[Headers] = None

    if isinstance(result, tuple):
        value, status_or_headers, headers = result + (None,) * (
            3 - len(result))
    else:
        value = result

    status = 200
    if status_or_headers is not None and not isinstance(
        status_or_headers, (Headers, dict, list)
    ) and str(status_or_headers).isdigit():
        status = int(status_or_headers)

    for status_code, model_cls in response_model.items():
        if status_code != status:
            continue
        if isinstance(value, dict):
            try:
                model_value = model_cls(**value)
            except (TypeError, ValidationError) as ve:
                return jsonify(validation_error=str(ve.errors())), BadRequest
        elif type(value) == model_cls:
            model_value = value
        elif is_builtin_dataclass(value):
            model_value = model_cls(**asdict(value))
        else:
            return jsonify(validation_error="invalid response"), BadRequest
        if is_dataclass(model_value):
            return asdict(model_value), status_or_headers, headers
        else:
            model_value = cast(BaseModel, model_value)
            return model_value.dict(), status_or_headers, headers
    return result


def validate(
    query_string: Optional[PydanticModel] = None,
    body: Optional[PydanticModel] = None,
    source: DataSource = DataSource.JSON,
    validate_path: bool = False,
    responses: Union[PydanticModel, Dict[int, PydanticModel], None] = None,
    headers: Optional[PydanticModel] = None
) -> Callable:
    """
    params:
        query_string:
            the params in query
        body:
            json body or form
        source:
            the body source
        response:
            response model define
    """
    if validate_path:
        pass
    if headers is not None:
        pass

    if query_string is not None:
        query_string = check_query_string_schema(query_string)

    if body is not None:
        body = check_body_schema(body, source)

    if responses is not None:
        responses = check_response_schema(responses)

    def decorator(func: Callable) -> Callable[..., Response]:

        if query_string:
            setattr(func, SCHEMA_QUERYSTRING_ATTRIBUTE, query_string)
        if body:
            setattr(func, SCHEMA_REQUEST_ATTRIBUTE, (body, source))
        if responses:
            setattr(func, SCHEMA_RESPONSE_ATTRIBUTE, responses)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            err = {}
            if body:
                data = request.get_json() if source == DataSource.JSON else request.form  # noqa
                try:
                    body_model = body(**data)
                except (TypeError, ValidationError) as ve:
                    err["body_params"] = str(ve)
                else:
                    g.body_params = body_model

            if query_string:
                try:
                    query_params = query_string(**request.args)
                except (TypeError, ValidationError) as ve:
                    err["query_params"] = str(ve)
                else:
                    g.query_params = query_params

            if err:
                return jsonify(validation_error=err), BadRequest.code

            result = func(*args, **kwargs)

            if responses:
                return check_response(result, responses)
            return result

        return wrapper

    return decorator
