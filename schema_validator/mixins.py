from typing import Optional

from pydantic import ValidationError


class SchemaValidationError(Exception):
    def __init__(
        self,
        validation_error: Optional[ValidationError] = None
    ) -> None:
        super().__init__()
        self.validation_error = validation_error
