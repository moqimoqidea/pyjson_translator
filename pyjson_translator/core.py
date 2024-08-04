import base64
import functools
import inspect
from typing import Optional, get_origin

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from pydantic import BaseModel

from .db_sqlalchemy_instance import default_sqlalchemy_instance as db
from .logger_setting import pyjson_translator_logging

GLOBAL_DB_SCHEMA_CACHE = {}


def generate_db_schema(input_class_instance):
    global GLOBAL_DB_SCHEMA_CACHE
    input_db_class = input_class_instance.__class__

    if input_db_class in GLOBAL_DB_SCHEMA_CACHE:
        return GLOBAL_DB_SCHEMA_CACHE[input_db_class]

    def get_nested_schema(relation_class_instance):
        related_model = relation_class_instance.mapper.entity
        related_instance = related_model()
        return generate_db_schema(related_instance)

    schema_fields = {}
    for attr_name, relation in input_db_class.__mapper__.relationships.items():
        if relation.uselist:
            nested_db_schema = get_nested_schema(relation)
            if nested_db_schema:
                # noinspection PyTypeChecker
                schema_fields[attr_name] = fields.Nested(nested_db_schema, many=True)

    # DB 环境运行时设定 load_instance 为 True 并配置 sqla_session
    class Meta:
        model = input_db_class
        load_instance = False

    schema_class = type(f"{input_db_class.__name__}Schema", (SQLAlchemyAutoSchema,),
                        {"Meta": Meta, **schema_fields})

    GLOBAL_DB_SCHEMA_CACHE[input_db_class] = schema_class
    return schema_class


def orm_class_to_dict(instance):
    schema = generate_db_schema(instance)()
    schema_value = schema.dump(instance)
    return schema_value


def orm_class_from_dict(cls, data):
    schema = generate_db_schema(cls())()
    schema_object = schema.load(data)
    # DB 环境运行时设定返回 db.session.merge(schema_object)
    # merge_schema_object = db.session.merge(schema_object)
    return schema_object


def with_prepare_func_json_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        prepare_json_data(func, args, kwargs)
        return func(*args, **kwargs)

    return wrapper


def prepare_json_data(func, args, kwargs):
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    json_data = {}
    deserialized_data = {}

    for name, arg_value in bound_args.arguments.items():
        if name == 'self':
            pyjson_translator_logging.info(f"Skipping 'self' parameter.")
            continue

        serialized_value = serialize_value(arg_value)
        json_data[name] = serialized_value
        pyjson_translator_logging.info(f"Processed parameter '{name}': {serialized_value}")

        deserialized_value = deserialize_value(serialized_value, type(arg_value))
        deserialized_data[name] = deserialized_value
        pyjson_translator_logging.info(f"Deserialized parameter '{name}': {deserialized_value}")

    pyjson_translator_logging.info(f"Final JSON data prepared for sending: {json_data}")
    return json_data


def serialize_value(value, db_sqlalchemy_instance: SQLAlchemy = db):
    if value is None:
        pyjson_translator_logging.info("Serializing None value.")
        return value
    elif isinstance(value, (int, float, str, bool)):
        pyjson_translator_logging.info(f"Serializing primitive type: {value}")
        return value
    elif isinstance(value, bytes):
        encoded_bytes = base64.b64encode(value).decode('utf-8')
        pyjson_translator_logging.info(f"Serializing bytes: {encoded_bytes}")
        return encoded_bytes
    elif isinstance(value, complex):
        complex_dict = {"real": value.real, "imaginary": value.imag}
        pyjson_translator_logging.info(f"Serializing complex number to dict: {complex_dict}")
        return complex_dict
    elif isinstance(value, list) or isinstance(value, tuple):
        pyjson_translator_logging.info(f"Serializing list or tuple: {value}")
        return [serialize_value(item) for item in value]
    elif isinstance(value, set):
        pyjson_translator_logging.info(f"Serializing set: {value}")
        return [serialize_value(item) for item in value]  # Convert set to list
    elif isinstance(value, dict):
        pyjson_translator_logging.info(f"Serializing dictionary. Keys: {value.keys()}")
        return {serialize_value(k): serialize_value(v) for k, v in value.items()}
    elif isinstance(value, db_sqlalchemy_instance.Model):
        pyjson_translator_logging.info(f"Serializing database model: {type(value).__name__}")
        serialized_model = orm_class_to_dict(value)
        pyjson_translator_logging.info(f"Serialized db.Model to dict: {serialized_model}")
        return serialized_model
    elif isinstance(value, BaseModel):
        pyjson_translator_logging.info(f"Serializing pydantic BaseModel: {type(value).__name__}")
        model_dict = value.model_dump()
        pyjson_translator_logging.info(f"Serialized BaseModel to dict: {model_dict}")
        return model_dict
    elif hasattr(value, '__dict__'):
        pyjson_translator_logging.info(f"Serializing using __dict__ for: {type(value).__name__}")
        return {k: serialize_value(v) for k, v in value.__dict__.items()}
    elif callable(getattr(value, 'to_dict', None)):
        pyjson_translator_logging.info(f"Serializing using custom method to_dict for: {type(value).__name__}")
        return value.to_dict()
    elif callable(getattr(value, 'dict', None)):
        pyjson_translator_logging.info(f"Serializing using custom method dict for: {type(value).__name__}")
        return value.dict()
    elif get_origin(value) is Optional:
        pyjson_translator_logging.info(f"Encountered an Optional type, "
                                       f"deeper serialization might be required for: {value}")
        return serialize_value(value)  # Recursive call for content inside Optional
    else:
        pyjson_translator_fail_message = f"Unhandled serialize type {type(value).__name__}"
        pyjson_translator_logging.warning(pyjson_translator_fail_message)
        raise ValueError(pyjson_translator_fail_message)


def deserialize_value(value, expected_type=None, db_sqlalchemy_instance: SQLAlchemy = db):
    if value is None:
        pyjson_translator_logging.info("Deserializing None value.")
        return value
    elif expected_type in (int, float, str, bool):
        pyjson_translator_logging.info(f"Deserializing primitive type: {value}")
        return expected_type(value)
    elif expected_type == bytes:
        decoded_bytes = base64.b64decode(value.encode('utf-8'))
        pyjson_translator_logging.info(f"Deserialized bytes: {decoded_bytes}")
        return decoded_bytes
    elif expected_type == complex:
        complex_value = complex(value['real'], value['imaginary'])
        pyjson_translator_logging.info(f"Deserialized complex number from dict: {complex_value}")
        return complex_value
    elif expected_type == list or expected_type == tuple:
        pyjson_translator_logging.info(f"Deserializing list or tuple: {value}")
        return [deserialize_value(item, type(item)) for item in value]
    elif expected_type == set:
        pyjson_translator_logging.info(f"Deserializing set: {value}")
        return set(deserialize_value(item, type(item)) for item in value)
    elif expected_type == dict:
        pyjson_translator_logging.info(f"Deserializing dictionary. Keys: {value.keys()}")
        return {deserialize_value(k, type(k)): deserialize_value(v, type(v)) for k, v in value.items()}
    elif expected_type and issubclass(expected_type, db_sqlalchemy_instance.Model):
        pyjson_translator_logging.info(f"Deserializing database model: {expected_type.__name__}")
        model_instance = orm_class_from_dict(expected_type, value)
        pyjson_translator_logging.info(f"Deserialized db.Model to instance: {model_instance}")
        return model_instance
    elif expected_type and issubclass(expected_type, BaseModel):
        pyjson_translator_logging.info(f"Deserializing pydantic BaseModel: {expected_type.__name__}")
        model_instance = expected_type.model_validate(value)
        pyjson_translator_logging.info(f"Deserialized BaseModel to instance: {model_instance}")
        return model_instance
    elif expected_type and hasattr(expected_type, '__dict__'):
        pyjson_translator_logging.info(f"Deserializing using __dict__ for: {expected_type.__name__}")
        instance = expected_type.__new__(expected_type)
        for k, v in value.items():
            setattr(instance, k, deserialize_value(v))
        return instance
    elif expected_type and callable(getattr(expected_type, 'to_dict', None)):
        pyjson_translator_logging.info(f"Deserializing using custom method to_dict for: {expected_type.__name__}")
        instance = expected_type.to_dict(value)
        return instance
    elif expected_type and callable(getattr(expected_type, 'dict', None)):
        pyjson_translator_logging.info(f"Deserializing using custom method dict for: {expected_type.__name__}")
        instance = expected_type.dict(value)
        return instance
    else:
        pyjson_translator_fail_message = (f"Unhandled deserialize type "
                                          f"{expected_type.__name__ if expected_type else 'unknown'}")
        pyjson_translator_logging.warning(pyjson_translator_fail_message)
        raise ValueError(pyjson_translator_fail_message)

