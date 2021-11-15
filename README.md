schema-validator
============

#### Generate from quart-schema


### Install

 - `pip install schema-validator`

<details>
<summary>How to use</summary>

```
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Optional
    from pydantic import BaseModel

    from flask import Flask
    from quart import Quart
    from schema_validator import SchemaValidator
    from schema_validator.flask import validate
    # from schema_validator.quart import validate


    app = Flask(__name__)

    # or 
    app = Quart(__name__)
    
    
    OR
    
    schema = SchemaValidator(app)
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
        
    @app.get("/")
    @validate(
        query=Todo,
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

    @tags("SOME-TAG", "OTHER-TAG")  # only for swagger
    class View(MethodView):
        @validate(...)
        def get(self):
            return {}
       
    
```
</details>

<details>
<summary>How to show the swagger </summary>

```

app.config["SWAGGER_ROUTE"] = True

http://yourhost/swagger/docs   -> show the all swagger

http://yourhost/swagger/docs/{tag} -> show the swagger which include tag

```
</details>

<details>
<summary>How to export the swagger </summary>

```
add command in flask/quart:
    app.cli.add_command(generate_schema_command)

Export all swagger to json file:

 - flask/quart schema -o swagger.json

Export the swagger which include the ACCOUNT tag:

 - flask/quart schema -o swagger.json -t ACCOUNT

```
</details>
