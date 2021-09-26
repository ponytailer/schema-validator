from dataclasses import dataclass
from typing import Optional

import pytest
from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass
from flask import Flask

from schema_validator import FlaskSchema, ResponseReturnValue
from schema_validator.typing import PydanticModel


@dataclass
class DCDetails:
    name: str
    age: Optional[int] = None


class Details(BaseModel):
    name: str
    age: Optional[int]


@pydantic_dataclass
class PyDCDetails:
    name: str
    age: Optional[int] = None


@pytest.mark.parametrize("type_", [DCDetails, Details, PyDCDetails])
def test_make_response(type_: PydanticModel) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/")
    def index() -> ResponseReturnValue:
        return type_(name="bob", age=2)

    test_client = app.test_client()
    response = test_client.get("/")
    assert response.get_json() == {"name": "bob", "age": 2}
