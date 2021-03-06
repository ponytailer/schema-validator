from typing import Optional

from flask import current_app, render_template_string

from schema_validator.constants import SWAGGER_TEMPLATE


def openapi(validator, tag: Optional[str] = None) -> dict:
    from ..core import _build_openapi_schema
    return _build_openapi_schema(current_app, validator, tag)


def swagger_ui(validator, tag: Optional[str] = None) -> str:
    path = f"/swagger/openapi-{tag}.json" if tag else validator.openapi_path
    return render_template_string(
        SWAGGER_TEMPLATE,
        title=validator.title,
        openapi_path=path,
        swagger_js_url=current_app.config["SCHEMA_SWAGGER_JS_URL"],
        swagger_css_url=current_app.config["SCHEMA_SWAGGER_CSS_URL"],
    )
