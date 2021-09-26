from dataclasses import asdict, dataclass

from flask import Flask

from schema_validator import (
    FlaskSchema, ResponseReturnValue,
    validate_request, validate_response
)


@dataclass
class Data:
    snake_case: str


def test_request_casing() -> None:
    app = Flask(__name__)
    FlaskSchema(app, convert_casing=True)

    @app.route("/", methods=["POST"])
    @validate_request(Data)
    def index(data: Data) -> ResponseReturnValue:
        return str(asdict(data))

    test_client = app.test_client()
    response = test_client.post("/", json={"snakeCase": "Hello"})
    assert response.get_data(as_text=True) == "{'snake_case': 'Hello'}"


def test_response_casing() -> None:
    app = Flask(__name__)
    FlaskSchema(app, convert_casing=True)

    @app.route("/", methods=["GET"])
    @validate_response(Data)
    def index() -> ResponseReturnValue:
        return Data(snake_case="Hello")

    test_client = app.test_client()
    response = test_client.get("/")
    assert response.json == {"snakeCase":"Hello"}
