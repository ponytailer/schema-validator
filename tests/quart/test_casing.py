from dataclasses import dataclass

import pytest
from quart import Quart

from schema_validator import SchemaValidator
from schema_validator.quart import validate


@dataclass
class Data:
    snake_case: str


@pytest.mark.asyncio
async def test_response_casing() -> None:
    app = Quart(__name__)
    SchemaValidator(app, convert_casing=True)

    @app.route("/", methods=["GET"])
    @validate(responses=Data)
    async def index():
        return Data(snake_case="Hello")

    test_client = app.test_client()
    response = await test_client.get("/")
    result = await response.get_json()
    assert result == {"snakeCase": "Hello"}
