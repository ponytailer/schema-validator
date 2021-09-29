import json
from typing import Optional

import click
from flask.cli import with_appcontext
from flask import current_app as app

from .extension import _build_openapi_schema


@click.command("schema")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output the spec to a file given by a path.",
)
@click.option(
    "--tag",
    "-t",
    type=str,
    required=False,
    default="",
    help="Export swagger include tag"
)
@with_appcontext
def generate_schema_command(
    output: Optional[str],
    tag: Optional[str]
) -> None:
    """
    The command which can dump json-swagger
        app.cli.add_command(generate_schema_command)
    virtualenv: flask schema
    """
    schema = _build_openapi_schema(
        app, app.extensions["FLASK_SCHEMA"], tag if tag else None)

    formatted_spec = json.dumps(schema, indent=2)
    if output is not None:
        with open(output, "w") as file_:
            click.echo(formatted_spec, file=file_)
    else:
        click.echo(formatted_spec)
