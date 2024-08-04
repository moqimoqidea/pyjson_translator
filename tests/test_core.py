from typing import Optional

from pydantic import BaseModel

from pyjson_translator.core import (
    serialize_value,
    with_prepare_func_json_data,
    with_post_func_data
)
from pyjson_translator.db_sqlalchemy_instance import default_sqlalchemy_instance as db
from pyjson_translator.logger_setting import pyjson_translator_logging


class ExampleModel(BaseModel):
    id: int
    name: str
    active: bool = True


class SimpleModel:
    def __init__(self, simple_id, name, active):
        self.simple_id = simple_id
        self.name = name
        self.active = active


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    address = db.relationship("Address", backref="user", lazy='select', passive_deletes="all")


class DemoService:
    @with_prepare_func_json_data
    @with_post_func_data
    def get_max(self, a, b) -> int:
        return max(a, b)

    @with_prepare_func_json_data
    @with_post_func_data
    def single(self, model: ExampleModel) -> ExampleModel:
        return model

    @with_prepare_func_json_data
    @with_post_func_data
    def list_model(self, model_list: list[ExampleModel]) -> list[ExampleModel]:
        return model_list

    @with_prepare_func_json_data
    @with_post_func_data
    def list_simple_model(self, model_list: list[SimpleModel]) -> list[SimpleModel]:
        return model_list

    @with_prepare_func_json_data
    @with_post_func_data
    def db_model(self, user: User) -> User:
        return user

    @with_prepare_func_json_data
    @with_post_func_data
    def optional_db_model(self, optional_user: Optional[User]) -> Optional[User]:
        return optional_user

    @with_prepare_func_json_data
    @with_post_func_data
    def double_optional_db_model(self, optional_user: Optional[User]) -> (int, Optional[User]):
        if optional_user is None:
            return 0, None
        else:
            return 1, optional_user

    @with_prepare_func_json_data
    @with_post_func_data
    def list_nested_model(self, model_list: list[dict[int, ExampleModel]]) -> list[dict[int, ExampleModel]]:
        return model_list

    @with_prepare_func_json_data
    @with_post_func_data
    def list_nested_simple_model(self, model_list: list[dict[int, SimpleModel]]) -> list[dict[int, SimpleModel]]:
        return model_list


demo_service = DemoService()


def test_basic_type():
    # Test serializing and deserializing a basic type
    max_value = demo_service.get_max(1, 2)
    pyjson_translator_logging.info(f"Serialized and deserialized max value is: {max_value}")


def test_complex_type():
    # Test serializing and deserializing complex data types
    example_bytes = b"hello world"
    example_complex = 3 + 4j
    example_set = {1, 2, 3}
    example_tuple = (1, 2, 3)

    pyjson_translator_logging.info(serialize_value(example_bytes))  # Base64 encoded string
    pyjson_translator_logging.info(serialize_value(example_complex))  # JSON object with real and imaginary parts
    pyjson_translator_logging.info(serialize_value(example_set))  # JSON array
    pyjson_translator_logging.info(serialize_value(example_tuple))  # JSON array


def test_pydantic_type():
    # Test serializing and deserializing a Pydantic model
    example_model = ExampleModel(id=1, name="Example", active=True)
    received_model = demo_service.single(example_model)
    pyjson_translator_logging.info(f"Serialized and deserialized Pydantic model is: {received_model}")


def test_pydantic_list_type():
    # Test serializing and deserializing a list of Pydantic models
    example_model = ExampleModel(id=1, name="Example", active=True)
    example_model2 = ExampleModel(id=2, name="Example", active=True)
    received_list = demo_service.list_model([example_model, example_model2])
    pyjson_translator_logging.info(f"Serialized and deserialized list of Pydantic models is: {received_list}")


def test_simple_list_type():
    # Test serializing and deserializing a list of simple models
    example_model = SimpleModel(simple_id=1, name="Example", active=True)
    example_model2 = SimpleModel(simple_id=2, name="Example", active=True)
    received_list = demo_service.list_simple_model([example_model, example_model2])
    pyjson_translator_logging.info(f"Serialized and deserialized list of simple models is: {received_list}")


def test_db_type():
    # Test serializing and deserializing a database model
    address_instance = Address(id=1, street="123 Main St", city="New York", state="NY", zip="10001", user_id=1)
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])
    received_user = demo_service.db_model(user_instance)
    pyjson_translator_logging.info(f"Serialized and deserialized database model is: {received_user}")


def test_optional_type():
    # Test serializing and deserializing an optional database model
    address_instance = Address(id=1, street="123 Main St", city="New York", state="NY", zip="10001", user_id=1)
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])
    received_user = demo_service.optional_db_model(user_instance)
    pyjson_translator_logging.info(f"Serialized and deserialized optional database model is: {received_user}")
    received_none = demo_service.optional_db_model(None)
    pyjson_translator_logging.info(f"Serialized and deserialized None value is: {received_none}")


def test_double_optional_type():
    # Test serializing and deserializing a double optional database model
    address_instance = Address(id=1, street="123 Main St", city="New York", state="NY", zip="10001", user_id=1)
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])
    received_user = demo_service.double_optional_db_model(user_instance)
    pyjson_translator_logging.info(f"Serialized and deserialized double optional database model is: {received_user}")
    received_none = demo_service.double_optional_db_model(None)
    pyjson_translator_logging.info(f"Serialized and deserialized None value is: {received_none}")


def test_nested_type():
    # Test serializing and deserializing nested models
    example_model = ExampleModel(id=1, name="Example", active=True)
    example_model2 = ExampleModel(id=2, name="Example", active=True)
    received_list = demo_service.list_nested_model([{1: example_model, 2: example_model2}])
    pyjson_translator_logging.info(f"Serialized and deserialized list of nested models is: {received_list}")


def test_nested_simple_type():
    # Test serializing and deserializing nested models
    example_model = SimpleModel(simple_id=1, name="Example", active=True)
    example_model2 = SimpleModel(simple_id=2, name="Example", active=True)
    received_list = demo_service.list_nested_simple_model([{1: example_model, 2: example_model2}])
    pyjson_translator_logging.info(f"Serialized and deserialized list of nested simple models is: {received_list}")


if __name__ == '__main__':
    test_basic_type()
    test_complex_type()
    test_pydantic_type()
    test_pydantic_list_type()
    test_simple_list_type()
    test_db_type()
    test_optional_type()
    test_double_optional_type()
    test_nested_type()
    test_nested_simple_type()
