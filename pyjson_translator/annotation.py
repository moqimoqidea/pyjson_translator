import functools
import inspect

from .error_handle import fail_to_translator
from .logger_setting import pyjson_translator_logging as logging
from .serialize import (
    serialize_value,
    deserialize_value
)


def with_prepare_func_json_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        prepare_json_data(func, args, kwargs)
        return func(*args, **kwargs)

    return wrapper


def with_post_func_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return_type = type(result)

        if result is None:
            return result

        if return_type is not inspect.Signature.empty and isinstance(return_type, tuple):
            serialized_results = tuple(serialize_value(val) for val in result)
            deserialized_results = tuple(deserialize_value(val, typ)
                                         for val, typ in zip(serialized_results, return_type))
            return deserialized_results
        elif return_type is not inspect.Signature.empty:
            serialized_result = serialize_value(result)
            return deserialize_value(serialized_result, return_type)
        else:
            fail_to_translator(f"Unhandled real post_func type {type(return_type).__name__}")

    return wrapper


def prepare_json_data(func, args, kwargs):
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    json_data = {}
    deserialized_data = {}

    for name, arg_value in bound_args.arguments.items():
        if name == 'self':
            logging.debug(f"Skipping 'self' parameter.")
            continue

        serialized_value = serialize_value(arg_value)
        json_data[name] = serialized_value
        logging.debug(f"Processed parameter '{name}': {serialized_value}")

        deserialized_value = deserialize_value(serialized_value, type(arg_value))
        deserialized_data[name] = deserialized_value
        logging.debug(f"Deserialized parameter '{name}': {deserialized_value}")

    logging.debug(f"Final JSON data prepared for sending: {json_data}")
    return json_data
