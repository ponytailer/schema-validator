from dataclasses import dataclass
from typing import Optional

import pytest
from pydantic import BaseModel
from flask import Flask

from schema_validator import (
    DataSource, FlaskSchema, ResponseReturnValue, validate_request
)
from schema_validator.typing import PydanticModel


@dataclass
class DCDetails:
    name: str
    age: Optional[int] = None


class Details(BaseModel):
    name: str
    age: Optional[int]


@pytest.mark.parametrize("type_", [DCDetails, Details])
def test_send_json(type_: PydanticModel) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/", methods=["POST"])
    @validate_request(type_)
    def index(data: PydanticModel) -> ResponseReturnValue:
        return data

    test_client = app.test_client()
    response = test_client.post("/", json=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}


@pytest.mark.parametrize("type_", [DCDetails, Details])
def test_send_form(type_: PydanticModel) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/", methods=["POST"])
    @validate_request(type_, source=DataSource.FORM)
    def index(data: PydanticModel) -> ResponseReturnValue:
        return data

    test_client = app.test_client()
    response = test_client.post("/", data=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}
