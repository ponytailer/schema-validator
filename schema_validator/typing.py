from typing import Dict, List, Tuple, Type, TypedDict, Union, Optional
from dataclasses import dataclass

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


class ResponseSchema(BaseModel):
    """
        base response to inherit

        class TodoResponse(ResponseSchema):
            name: str
            age: int
    """
    success: Optional[bool] = True
    error_no: Optional[int] = 0
    error_message: Optional[str] = ""


@dataclass
class ResponseClass:
    """
        base response schema with dataclass

        @dataclass
        class B(ResponseClass):
            name: str

        =>

        type B struct{
            success: Optional[bool]
            error_no: Optional[int32]
            error_message: Optional[string]
            name: string
        }
    """
    success: Optional[bool] = True
    error_no: Optional[int] = 0
    error_message: Optional[str] = ""
