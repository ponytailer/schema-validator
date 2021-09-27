schema-validator
============

#### Generate from quart-schema


### Install

 - `pip install schema-validator`

### How to use

```
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Optional
    from pydantic import BaseModel

    from flask import Flask
    from schema_validator import FlaskSchema, validate

    app = Flask(__name__)
    
    FlaskSchema(app)
    
    OR
    
    schema = FlaskSchema()
    schema.init_app(app)

    @dataclass
    class Todo:
        task: str
        due: Optional[datetime]

    class TodoResponse(BaseModel):
        id: int
        name: str

    @app.post("/")
    @validate(body=Todo, responses=TodoResponse)
    def create_todo():
        # balabala
        return dict(id=1, name="2")
        
    @app.put("/")
    @validate(
        body=Todo,
        responses={200: TodoResponse, 400: TodoResponse}
    )
    def update_todo():
        # balabala
        return TodoResponse(id=1, name="123")

    @app.delete("/")
    @validate(
        body=Todo,
        responses={200: TodoResponse}
    )
    def delete():
        # balabala
        return jsonify(id=1)
     
    @tags("SOME-TAG", "OTHER-TAG")
    class View(MethodView):
        @validate(...)
        def get(self):
            return {}
       
    app.cli.add_command(generate_schema_command)
    
    virtualenv:  flask schema swagger.json -> generate json swagger
```


##### FEATURES
    - direct package/api/view_class name to export json-swagger
    - direct tag to swagger html
