from typing import List

import pytest
from pydantic import BaseModel

from pyjson_translator.db_sqlalchemy_instance import default_sqlalchemy_instance as db
from pyjson_translator.serialize import serialize_value, deserialize_value


def test_primitive_types():
    int_value = 123
    str_value = "hello"
    bool_value = True

    # Serialize basic types
    serialized_int = serialize_value(123)
    serialized_str = serialize_value("hello")
    serialized_bool = serialize_value(True)

    # Deserialize basic types
    assert int_value == deserialize_value(serialized_int, int)
    assert str_value == deserialize_value(serialized_str, str)
    assert bool_value == deserialize_value(serialized_bool, bool)


def test_complex_types():
    complex_value = 3 + 4j

    # Serialize complex types
    # {'real': 3.0, 'imaginary': 4.0}
    serialized_complex = serialize_value(complex_value)

    # Deserialize basic types
    # (3+4j)
    assert complex_value == deserialize_value(serialized_complex, complex)


def test_pydantic_types():
    class ExampleModel(BaseModel):
        id: int
        name: str
        active: bool = True

    example_model = ExampleModel(id=1, name="Example", active=True)

    # Serialize Pydantic model
    # {'id': 1, 'name': 'Example', 'active': True}
    serialized_model = serialize_value(example_model)

    # Deserialize Pydantic model
    # id=1 name='Example' active=True
    deserialized_model = deserialize_value(serialized_model, ExampleModel)
    assert isinstance(deserialized_model, ExampleModel)
    assert deserialized_model.id == example_model.id


@pytest.mark.skip(reason="skip for sqlalchemy db data.")
def test_sqlalchemy_types():
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

    address_instance = Address(id=1, street="123 Main St", city="New York", state="NY", zip="10001", user_id=1)
    user_instance = User(id=1, username="john_doe", email="john@example.com", address=[address_instance])

    # Serialize SQLAlchemy model
    serialized_user = serialize_value(user_instance)

    # Deserialize SQLAlchemy model
    deserialized_user = deserialize_value(serialized_user, User)
    assert deserialized_user['id'] == user_instance.id

    # fixme: if you need isinstance, you should add parameter with sqlalchemy data.
    # assert isinstance(deserialized_user, User)


def test_simple_types():
    class SimpleModel:
        def __init__(self, simple_id, name, active):
            self.simple_id = simple_id
            self.name = name
            self.active = active

        def __repr__(self):
            return f"<SimpleModel simple_id={self.simple_id}, name={self.name}, active={self.active}>"

    example_model = SimpleModel(simple_id=1, name="Example", active=True)

    # Serialize simple class
    serialized_simple_model = serialize_value(example_model)

    # Deserialize simple class
    deserialized_simple_model = deserialize_value(serialized_simple_model, SimpleModel)
    assert isinstance(deserialized_simple_model, SimpleModel)
    assert deserialized_simple_model.simple_id == example_model.simple_id


def test_list_with_simple_class_types():
    class SimpleModel:
        def __init__(self, simple_id, name, active):
            self.simple_id = simple_id
            self.name = name
            self.active = active

        def __repr__(self):
            return f"<SimpleModel simple_id={self.simple_id}, name={self.name}, active={self.active}>"

    example_model = SimpleModel(simple_id=1, name="Example", active=True)
    example_model2 = SimpleModel(simple_id=2, name="Example", active=True)
    simple_model_list = [example_model, example_model2]

    # Serialize a list with simple class
    serialized_simple_model_list = serialize_value(simple_model_list)
    print(serialized_simple_model_list)

    # Deserialize simple class
    deserialized_simple_model_list = deserialize_value(serialized_simple_model_list, List[SimpleModel])
    print(deserialized_simple_model_list)
    assert isinstance(deserialized_simple_model_list, list)
    assert len(deserialized_simple_model_list) == 2
    assert isinstance(deserialized_simple_model_list[0], SimpleModel)
    assert deserialized_simple_model_list[0].simple_id == example_model.simple_id
