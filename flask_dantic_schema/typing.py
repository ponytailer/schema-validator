from typing import Dict, List, Tuple, Type, TypedDict, Union

from pydantic import BaseModel
from flask.typing import (
    HeadersValue,
    ResponseReturnValue as FlaskResponseReturnValue,
    ResponseValue as FlaskResponseValue,
    StatusCode,
)

PydanticModel = Union[Type[BaseModel], Type]

ResponseValue = Union[FlaskResponseValue, PydanticModel]

ResponseReturnValue = Union[
    FlaskResponseReturnValue,
    ResponseValue,
    Tuple[ResponseValue, HeadersValue],
    Tuple[ResponseValue, StatusCode],
    Tuple[ResponseValue, StatusCode, HeadersValue],
]


class VariableObject(TypedDict, total=False):
    enum: List[str]
    default: str
    description: str


class ServerObject(TypedDict, total=False):
    url: str
    description: str
    variables: Dict[str, VariableObject]
