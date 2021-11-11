from typing import Optional

from quart import current_app, render_template_string

from schema_validator.constants import SWAGGER_TEMPLATE


async def openapi(validator, tag: Optional[str] = None) -> dict:
    from ..core import _build_openapi_schema
    return _build_openapi_schema(current_app, validator, tag)


async def swagger_ui(validator, tag: Optional[str] = None) -> str:
    path = f"/swagger/openapi-{tag}.json" if tag else validator.openapi_path
    return await render_template_string(
        SWAGGER_TEMPLATE,
        title=validator.title,
        openapi_path=path,
        swagger_js_url=current_app.config["FLASK_SCHEMA_SWAGGER_JS_URL"],
        swagger_css_url=current_app.config["FLASK_SCHEMA_SWAGGER_CSS_URL"],
    )
