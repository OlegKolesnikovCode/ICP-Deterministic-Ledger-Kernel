from enum import Enum


class ValidationMode(str, Enum):
    SRC_ONLY = "src-only"


class FailOn(str, Enum):
    WARNINGS = "warnings"
    ERRORS = "errors"
    BLOCKING = "blocking"

