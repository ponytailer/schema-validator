from flask import Flask, g
from schema_validator import validate
from dataclasses import dataclass


app = Flask()


@dataclass
class Req:
    name: str
    age: int


@dataclass
class Response:
    name: str


@app.post("/test")
@validate(query=Req, body=Req, responses=Response, tags=["test"])
def new_model():
    """ tags only for swagger """
    body = g.body_params
    query_params = g.query_params
    print(body, query_params)
    return Response(name=123)


if __name__ == "__main__":
    app.run()
