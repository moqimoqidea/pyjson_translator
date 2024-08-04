import importlib

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

    @with_prepare_func_json_data
    @with_post_func_data
    def str_and_path_to_exception(self, message: str, exception_path: str) -> DemoException:
        module_path, _, class_name = exception_path.rpartition('.')
        if not module_path:
            raise ValueError("You must provide the full path to the exception class, including the module.")

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Module {module_path} could not be loaded: {str(e)}")

        exception_class = getattr(module, class_name, None)
        if exception_class is None:
            raise ValueError(f"No exception class found with the name: {class_name} in module {module_path}")

        if not issubclass(exception_class, Exception):
            raise TypeError(f"{class_name} is not a subclass of Exception")

        # noinspection PyArgumentList
        return exception_class(message=message)

    def dict_and_path_to_exception(self, data: dict, exception_path: str) -> DemoException:
        module_path, _, class_name = exception_path.rpartition('.')
        if not module_path:
            raise ValueError("You must provide the full path to the exception class, including the module.")

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Module {module_path} could not be loaded: {str(e)}")

        exception_class = getattr(module, class_name, None)
        if exception_class is None:
            raise ValueError(f"No exception class found with the name: {class_name} in module {module_path}")

        if not issubclass(exception_class, Exception):
            raise TypeError(f"{class_name} is not a subclass of Exception")

        constructor_params = exception_class.__init__.__code__.co_varnames[
                             1:exception_class.__init__.__code__.co_argcount]
        missing_params = [param for param in constructor_params if param not in data]
        if missing_params:
            raise ValueError(f"Missing required parameters {missing_params} for initializing '{class_name}'.")

        # noinspection PyArgumentList
        return exception_class(**data)


demo_service = DemoService()


def test_double_exception():
    exception = DemoException(message="An error occurred")
    demo_service.double_exception(exception)


def test_str_to_exception():
    message = "An error occurred"
    exception = demo_service.str_to_exception(message, "DemoException")
    assert exception.message == message


def test_str_and_path_to_exception():
    message = "An error occurred"
    exception = demo_service.str_and_path_to_exception(message, "tests.test_core_exception.DemoException")
    assert exception.message == message


def test_dict_and_path_to_exception():
    exception_dict = {"message": "An error occurred"}
    exception = demo_service.dict_and_path_to_exception(exception_dict, "tests.test_core_exception.DemoException")
    assert exception.message == exception_dict["message"]
