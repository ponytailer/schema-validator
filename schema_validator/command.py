import json

import click

from schema_validator.types import Optional
from schema_validator.core import _build_openapi_schema

try:
    from flask import current_app as app
    from flask.cli import with_appcontext
except ImportError:
    from quart import current_app as app
    from quart.cli import with_appcontext


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
        app, app.extensions["SCHEMA_VALIDATOR"], tag if tag else None)

    formatted_spec = json.dumps(schema, indent=2, ensure_ascii=False)
    if output is not None:
        with open(output, "w") as file_:
            click.echo(formatted_spec, file=file_)
    else:
        click.echo(formatted_spec)
