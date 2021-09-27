from dataclasses import dataclass

from flask import Flask

from schema_validator import (
    FlaskSchema, ResponseReturnValue,
    validate
)


@dataclass
class Data:
    snake_case: str


def test_response_casing() -> None:
    app = Flask(__name__)
    FlaskSchema(app, convert_casing=True)

    @app.route("/", methods=["GET"])
    @validate(responses=Data)
    def index() -> ResponseReturnValue:
        return Data(snake_case="Hello")

    test_client = app.test_client()
    response = test_client.get("/")
    assert response.json == {"snakeCase": "Hello"}
