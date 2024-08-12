import base64
from typing import Optional, get_origin, get_args, Union

from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel

from .db_sqlalchemy_instance import default_sqlalchemy_instance as db
from .error_handle import fail_to_translator
from .logger_setting import pyjson_translator_logging as logging
from .marshmallow_db_util import (
    orm_class_to_dict,
    orm_class_from_dict
)


def serialize_value(value: any,
                    db_sqlalchemy_instance: SQLAlchemy = db,
                    db_sqlalchemy_merge: bool = False):
    if value is None:
        logging.debug("Serializing None value.")
        return value
    if isinstance(value, (int, float, str, bool)):
        logging.debug(f"Serializing primitive type: {value}")
        return value
    if isinstance(value, bytes):
        encoded_bytes = base64.b64encode(value).decode('utf-8')
        logging.debug(f"Serializing bytes: {encoded_bytes}")
        return encoded_bytes
    if isinstance(value, complex):
        complex_dict = {"real": value.real, "imaginary": value.imag}
        logging.debug(f"Serializing complex number to dict: {complex_dict}")
        return complex_dict
    if isinstance(value, (list, tuple)):
        logging.debug(f"Serializing list or tuple: {value}")
        return [serialize_value(item) for item in value]
    if isinstance(value, set):
        logging.debug(f"Serializing set: {value}")
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        logging.debug(f"Serializing dictionary. Keys: {value.keys()}")
        return {serialize_value(k): serialize_value(v) for k, v in value.items()}
    if isinstance(value, db_sqlalchemy_instance.Model):
        logging.debug(f"Serializing sqlalchemy db.Model: {type(value).__name__}")
        serialized_model = orm_class_to_dict(value, db_sqlalchemy_merge)
        logging.debug(f"Serialized sqlalchemy db.Model to dict: {serialized_model}")
        return serialized_model
    if isinstance(value, BaseModel):
        logging.debug(f"Serializing pydantic BaseModel: {type(value).__name__}")
        model_dict = value.model_dump()
        logging.debug(f"Serialized BaseModel to dict: {model_dict}")
        return model_dict
    if hasattr(value, '__dict__'):
        logging.debug(f"Serializing using __dict__ for: {type(value).__name__}")
        return {k: serialize_value(v) for k, v in value.__dict__.items()}
    if callable(getattr(value, 'to_dict', None)):
        logging.debug(f"Serializing using custom method to_dict for: {type(value).__name__}")
        return value.to_dict()
    if callable(getattr(value, 'dict', None)):
        logging.debug(f"Serializing using custom method dict for: {type(value).__name__}")
        return value.dict()
    if get_origin(value) is Optional:
        logging.debug(
            f"Encountered an Optional type, deeper serialization might be required for: {value}")
        return serialize_value(value)
    fail_to_translator(f"Unhandled serialize type {type(value).__name__}")


def deserialize_value(value: any,
                      expected_type: type = None,
                      db_sqlalchemy_instance: SQLAlchemy = db,
                      db_sqlalchemy_merge: bool = False):
    if value is None:
        logging.debug("Deserializing None value.")
        return value
    if expected_type in (int, float, str, bool):
        logging.debug(f"Deserializing primitive type: {value}")
        return expected_type(value)
    if expected_type == bytes:
        decoded_bytes = base64.b64decode(value.encode('utf-8'))
        logging.debug(f"Deserialized bytes: {decoded_bytes}")
        return decoded_bytes
    if expected_type == complex:
        complex_value = complex(value['real'], value['imaginary'])
        logging.debug(f"Deserialized complex number from dict: {complex_value}")
        return complex_value

    if expected_type in (list, tuple):
        logging.debug(f"Deserializing list or tuple: {value}")
        return [deserialize_value(item, type(item)) for item in value]
    if expected_type == set:
        logging.debug(f"Deserializing set: {value}")
        return set(deserialize_value(item, type(item)) for item in value)
    if expected_type == dict:
        logging.debug(f"Deserializing dictionary. Keys: {value.keys()}")
        return {deserialize_value(k, type(k)): deserialize_value(v, type(v)) for k, v in value.items()}

    origin_expected_type = get_origin(expected_type)
    if origin_expected_type:
        item_type = get_args(expected_type)[0]

        if origin_expected_type in (list, tuple):
            logging.debug(f"Deserializing list or tuple: {value}")
            return [deserialize_value(item, item_type) for item in value]
        if origin_expected_type == set:
            logging.debug(f"Deserializing set: {value}")
            return set(deserialize_value(item, item_type) for item in value)
        if origin_expected_type is Union:
            logging.debug(f"Deserializing Union type: {item_type.__name__}")
            return deserialize_value(value, item_type)
        if origin_expected_type == dict:
            logging.debug(f"Deserializing dictionary. Keys: {value.keys()}")
            key_type, val_type = get_args(expected_type)
            return {deserialize_value(k, key_type): deserialize_value(v, val_type) for k, v in value.items()}

    if expected_type and issubclass(expected_type, db_sqlalchemy_instance.Model):
        logging.debug(f"Deserializing sqlalchemy db.Model: {expected_type.__name__}")
        model_instance = orm_class_from_dict(expected_type, value, db_sqlalchemy_instance, db_sqlalchemy_merge)
        logging.debug(f"Deserialized sqlalchemy db.Model to instance: {model_instance}")
        return model_instance
    if expected_type and issubclass(expected_type, BaseModel):
        logging.debug(f"Deserializing pydantic BaseModel: {expected_type.__name__}")
        model_instance = expected_type.model_validate(value)
        logging.debug(f"Deserialized BaseModel to instance: {model_instance}")
        return model_instance
    if expected_type and hasattr(expected_type, '__dict__'):
        logging.debug(f"Deserializing using __dict__ for: {expected_type.__name__}")
        constructor_params = expected_type.__init__.__code__.co_varnames[
                             1:expected_type.__init__.__code__.co_argcount]
        if all(param in value for param in constructor_params):
            return expected_type(**{param: value[param] for param in constructor_params})
        else:
            missing_params = [param for param in constructor_params if param not in value]
            fail_to_translator(f"Missing required parameters for initializing "
                               f"'{expected_type.__name__}': {', '.join(missing_params)}")
    if expected_type and callable(getattr(expected_type, 'to_dict', None)):
        logging.debug(f"Deserializing using custom method to_dict for: {expected_type.__name__}")
        return expected_type.to_dict(value)
    if expected_type and callable(getattr(expected_type, 'dict', None)):
        logging.debug(f"Deserializing using custom method dict for: {expected_type.__name__}")
        return expected_type.dict(value)
    fail_to_translator(f"Unhandled deserialize type {expected_type.__name__ if expected_type else 'unknown'}")
