# src/utils/__init__.py

from .logger import setup_logger
from .validation import validate_inputs

class ExperimentUtils:
    setup_logger = staticmethod(setup_logger)
    validate_inputs = staticmethod(validate_inputs)
