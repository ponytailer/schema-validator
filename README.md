Flask-Dantic-Schema
============

[![Build Status](https://app.travis-ci.com/huangxiaohen2738/flask-dantic-schema.svg?branch=main)](https://app.travis-ci.com/huangxiaohen2738/flask-dantic-schema)

```
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Optional

    from flask import Flask
    from flask_dantic_schema import FlaskSchema, validate_request, validate_response

    app = Flask(__name__)
    FlaskSchema(app)

    @dataclass
    class Todo:
        task: str
        due: Optional[datetime]

    @app.post("/")
    @validate_request(Todo)
    @validate_response(Todo, 201)
    def create_todo(data: Todo) -> Todo:
        ... # Do something with data, e.g. save to the DB
        return data, 201
```
