from dataclasses import dataclass
from typing import Any, Optional

import pytest
from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass
from flask import Flask

from schema_validator import (
    DataSource,
    FlaskSchema,
    ResponseReturnValue,
    validate
)


@dataclass
class DCDetails:
    name: str
    age: Optional[int] = None


@dataclass
class DCItem:
    count: int
    details: DCDetails


@dataclass
class QueryItem:
    count_le: Optional[int] = None
    count_gt: Optional[int] = None


class Details(BaseModel):
    name: str
    age: Optional[int]


class Item(BaseModel):
    count: int
    details: Details


@pydantic_dataclass
class PyDCDetails:
    name: str
    age: Optional[int] = None


@pydantic_dataclass
class PyDCItem:
    count: int
    details: PyDCDetails


VALID_DICT = {"count": 2, "details": {"name": "bob"}}
INVALID_DICT = {"count": 2, "name": "bob"}
VALID = Item(count=2, details=Details(name="bob"))
INVALID = Details(name="bob")
VALID_DC = DCItem(count=2, details=DCDetails(name="bob"))
INVALID_DC = DCDetails(name="bob")
VALID_PyDC = PyDCItem(count=2, details=PyDCDetails(name="bob"))
INVALID_PyDC = PyDCDetails(name="bob")


@pytest.mark.parametrize("path", ["/", "/dc"])
@pytest.mark.parametrize(
    "json, status",
    [
        (VALID_DICT, 200),
        (INVALID_DICT, 400),
    ],
)
def test_request_validation(path: str, json: dict, status: int) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/", methods=["POST"])
    @validate(body=Item)
    def item() -> ResponseReturnValue:
        return ""

    @app.route("/dc", methods=["POST"])
    @validate(body=DCItem)
    def dc_item() -> ResponseReturnValue:
        return ""

    test_client = app.test_client()
    response = test_client.post(path, json=json)
    assert response.status_code == status


@pytest.mark.parametrize(
    "data, status",
    [
        ({"name": "bob"}, 200),
        ({"age": 2}, 400),
    ],
)
def test_request_form_validation(data: dict, status: int) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/", methods=["POST"])
    @validate(body=Details, source=DataSource.FORM)
    def item() -> ResponseReturnValue:
        return ""

    test_client = app.test_client()
    response = test_client.post("/", data=data)
    assert response.status_code == status


@pytest.mark.parametrize(
    "model, return_value, status",
    [
        (Item, VALID_DICT, 200),
        (Item, INVALID_DICT, 500),
        (Item, VALID, 200),
        (Item, INVALID, 500),
        (DCItem, VALID_DICT, 200),
        (DCItem, INVALID_DICT, 500),
        (DCItem, VALID_DC, 200),
        (DCItem, INVALID_DC, 500),
        (PyDCItem, VALID_DICT, 200),
        (PyDCItem, INVALID_DICT, 500),
        (PyDCItem, VALID_PyDC, 200),
        (PyDCItem, INVALID_PyDC, 500),
    ],
)
def test_response_validation(model: Any, return_value: Any,
    status: int) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/")
    @validate(response=model)
    def item() -> ResponseReturnValue:
        return return_value

    test_client = app.test_client()
    response = test_client.get("/")
    assert response.status_code == status


@pytest.mark.parametrize(
    "path, status",
    [
        ("/", 200),
        ("/?count_le=2", 200),
        ("/?count_le=2&count_gt=0", 200),
        ("/?count_le=a", 400),
        ("/?count=a", 200),
    ],
)
def test_querystring_validation(path: str, status: int) -> None:
    app = Flask(__name__)
    FlaskSchema(app)

    @app.route("/")
    @validate(query_string=QueryItem)
    def query_item() -> ResponseReturnValue:
        return ""

    test_client = app.test_client()
    response = test_client.get(path)
    assert response.status_code == status
