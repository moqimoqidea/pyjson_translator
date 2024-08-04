from pyjson_translator.core import (
    with_prepare_func_json_data,
    with_post_func_data
)


class DemoException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DemoService:
    @with_prepare_func_json_data
    @with_post_func_data
    def double_exception(self, e: DemoException) -> list[DemoException]:
        return [e, e]


demo_service = DemoService()


def test_double_exception():
    exception = DemoException(message="An error occurred")
    demo_service.double_exception(exception)
