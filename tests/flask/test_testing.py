from dataclasses import dataclass
from typing import Optional

import pytest
from pydantic import BaseModel
from flask import Flask, g

from schema_validator import DataSource, SchemaValidator
from schema_validator.flask import validate
from schema_validator.core import _build_openapi_schema
from schema_validator.types import PydanticModel


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
    SchemaValidator(app)

    @app.route("/", methods=["POST"])
    @validate(body=type_)
    def index():
        return g.body_params.dict()

    test_client = app.test_client()
    response = test_client.post("/", json=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}


@pytest.mark.parametrize("type_", [DCDetails, Details])
def test_send_form(type_: PydanticModel) -> None:
    app = Flask(__name__)
    SchemaValidator(app)

    @app.route("/", methods=["POST"])
    @validate(body=type_, source=DataSource.FORM)
    def index():
        return g.body_params.dict()

    test_client = app.test_client()
    response = test_client.post("/", data=dict(name="bob", age=2))
    assert response.get_json() == {"name": "bob", "age": 2}


def test_generate_swagger():
    app = Flask(__name__)
    SchemaValidator(app)

    @app.route("/test", methods=["POST"])
    @validate(
        body=Details,
        responses={200: Details, 500: DCDetails}
    )
    def index():
        return g.body_params.dict()

    schema = _build_openapi_schema(app, app.extensions["SCHEMA_VALIDATOR"])

    assert schema["paths"]["/test"]["post"]["requestBody"]
    assert schema["paths"]["/test"]["post"]["responses"]
