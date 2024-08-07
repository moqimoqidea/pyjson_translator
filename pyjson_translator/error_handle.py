from .logger_setting import pyjson_translator_logging


def fail_to_translator(pyjson_translator_fail_message: str):
    pyjson_translator_logging.warning(pyjson_translator_fail_message)
    raise PyjsonTranslatorException(pyjson_translator_fail_message)


class PyjsonTranslatorException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
