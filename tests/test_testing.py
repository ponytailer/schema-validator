from dataclasses import dataclass
from typing import Optional

import pytest
from pydantic import BaseModel
from flask import Flask, g

from schema_validator import (
    DataSource, FlaskSchema, ResponseReturnValue, validate
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
    @validate(body=type_)
    def index() -> ResponseReturnValue:
        print(type(g.body_params))
        return g.body_params.dict()

    test_client = app.test_client()
    response = test_client.post("/", json=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}


@pytest.mark.parametrize("type_", [DCDetails, Details])
def test_send_form(type_: PydanticModel) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/", methods=["POST"])
    @validate(body=type_, source=DataSource.FORM)
    def index() -> ResponseReturnValue:
        return g.body_params.dict()

    test_client = app.test_client()
    response = test_client.post("/", data=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}
