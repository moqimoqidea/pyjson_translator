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

    @with_prepare_func_json_data
    @with_post_func_data
    def str_to_exception(self, message: str, exception_name: str) -> DemoException:
        exception_class = globals().get(exception_name)
        if exception_class is None:
            raise ValueError(f"No exception class found with the name: {exception_name}")

        if not issubclass(exception_class, Exception):
            raise TypeError(f"{exception_name} is not a subclass of Exception")

        # noinspection PyArgumentList
        return exception_class(message=message)


demo_service = DemoService()


def test_double_exception():
    exception = DemoException(message="An error occurred")
    demo_service.double_exception(exception)


def test_str_to_exception():
    message = "An error occurred"
    exception = demo_service.str_to_exception(message, "DemoException")
    assert exception.message == message
