from typing import Optional

from pydantic import BaseModel

from pyjson_translator.core import (
    serialize_value,
    with_prepare_func_json_data
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
    def get_max(self, a, b):
        return max(a, b)

    @with_prepare_func_json_data
    def single(self, model: ExampleModel):
        pyjson_translator_logging.info(f"Model received: {model}")
        return "Data processed"

    @with_prepare_func_json_data
    def list_model(self, model_list: list[ExampleModel]):
        pyjson_translator_logging.info(f"Model list received: {model_list}")
        return "Data processed"

    @with_prepare_func_json_data
    def list_simple_model(self, model_list: list[SimpleModel]):
        pyjson_translator_logging.info(f"Simple model list received: {model_list}")
        return "Data processed"

    @with_prepare_func_json_data
    def db_model(self, user: User):
        pyjson_translator_logging.info(f"Database model user received: {user}")
        return "Data processed"

    @with_prepare_func_json_data
    def optional_db_model(self, optional_user: Optional[User]):
        pyjson_translator_logging.info(f"Database model optional_user received: {optional_user}")
        return "Data processed"

    @with_prepare_func_json_data
    def list_nested_model(self, model_list: list[dict[int, ExampleModel]]):
        pyjson_translator_logging.info(f"Nested model list received: {model_list}")
        return "Data processed"


demo_service = DemoService()


def test_basic_type():
    max_value = demo_service.get_max(1, 2)
    pyjson_translator_logging.info(f"Max value is: {max_value}")


def test_complex_type():
    example_bytes = b"hello world"
    example_complex = 3 + 4j
    example_set = {1, 2, 3}
    example_tuple = (1, 2, 3)

    pyjson_translator_logging.info(serialize_value(example_bytes))  # Base64 encoded string
    pyjson_translator_logging.info(serialize_value(example_complex))  # JSON object with real and imaginary parts
    pyjson_translator_logging.info(serialize_value(example_set))  # JSON array
    pyjson_translator_logging.info(serialize_value(example_tuple))  # JSON array


def test_pydantic_type():
    example_model = ExampleModel(id=1, name="Example", active=True)
    pyjson_translator_logging.info(demo_service.single(example_model))


def test_pydantic_list_type():
    example_model = ExampleModel(id=1, name="Example", active=True)
    example_model2 = ExampleModel(id=2, name="Example", active=True)
    pyjson_translator_logging.info(demo_service.list_model([example_model, example_model2]))


def test_simple_list_type():
    example_model = SimpleModel(simple_id=1, name="Example", active=True)
    example_model2 = SimpleModel(simple_id=2, name="Example", active=True)
    pyjson_translator_logging.info(demo_service.list_simple_model([example_model, example_model2]))


def test_db_type():
    address_instance = Address(id=1, street="123 Main St", city="New York",
                               state="NY", zip="10001", user_id=1, )
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])
    pyjson_translator_logging.info(demo_service.db_model(user_instance))


def test_optional_type():
    address_instance = Address(id=1, street="123 Main St", city="New York",
                               state="NY", zip="10001", user_id=1, )
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])
    pyjson_translator_logging.info(demo_service.optional_db_model(user_instance))
    pyjson_translator_logging.info(demo_service.optional_db_model(None))


def test_nested_type():
    example_model = ExampleModel(id=1, name="Example", active=True)
    example_model2 = ExampleModel(id=2, name="Example", active=True)
    pyjson_translator_logging.info(demo_service.list_nested_model([{1: example_model, 2: example_model2}]))


if __name__ == '__main__':
    test_basic_type()
    test_complex_type()
    test_pydantic_type()
    test_pydantic_list_type()
    test_simple_list_type()
    test_db_type()
    test_optional_type()
    test_nested_type()
