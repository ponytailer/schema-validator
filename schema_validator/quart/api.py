import inspect

from typing import Optional, Callable
from functools import wraps
from dataclasses import is_dataclass, asdict
from pydantic import BaseModel

from quart import current_app, render_template_string

from schema_validator.constants import SWAGGER_TEMPLATE


def convert_model_result(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(result):
        status_or_headers = None
        headers = None
        if isinstance(result, tuple):
            value, status_or_headers, headers = result + (None,) * (3 - len(result))
        else:
            value = result

        if is_dataclass(value):
            dict_or_value = asdict(value)
        elif isinstance(value, BaseModel):
            dict_or_value = value.dict()
        elif inspect.iscoroutine(value):
            dict_or_value = await value
        else:
            dict_or_value = value
        return await func((dict_or_value, status_or_headers, headers))

    return decorator


async def openapi(validator, tag: Optional[str] = None) -> dict:
    from ..core import _build_openapi_schema
    return _build_openapi_schema(current_app, validator, tag)


async def swagger_ui(validator, tag: Optional[str] = None) -> str:
    path = f"/swagger/openapi-{tag}.json" if tag else validator.openapi_path
    return await render_template_string(
        SWAGGER_TEMPLATE,
        title=validator.title,
        openapi_path=path,
        swagger_js_url=current_app.config["SCHEMA_SWAGGER_JS_URL"],
        swagger_css_url=current_app.config["SCHEMA_SWAGGER_CSS_URL"],
    )
