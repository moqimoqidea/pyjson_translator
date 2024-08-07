# pyjson_translator

A simple JSON to Python object translator.

## Installation

```bash
pip install -U pyjson_translator
```

Alternatively, you can use `poetry` for installation:

```bash
poetry add pyjson_translator@latest
```

For development purposes, use:

```bash
poetry install --with dev
```

Otherwise, use:

```bash
poetry install
```

## How to Use

### Serialization and Deserialization

The `pyjson_translator` package provides functions to serialize and deserialize various types of Python objects,
including primitive types, complex types, Pydantic models, SQLAlchemy models, and some simple classes.

When pyjson_translator encounters an unhandled type, it fails quickly and throws an exception.
This helps to quickly diagnose the problem and make adjustments as needed.

#### Basic Types

```python
from pyjson_translator.serialize import serialize_value, deserialize_value

int_value = 123
str_value = "hello"
bool_value = True

# Serialize basic types
serialized_int = serialize_value(123)
serialized_str = serialize_value("hello")
serialized_bool = serialize_value(True)

# Deserialize basic types
deserialize_value(serialized_int, int)
deserialize_value(serialized_str, str)
deserialize_value(serialized_bool, bool)
```

#### Complex Types

```python
from pyjson_translator.serialize import serialize_value, deserialize_value

complex_value = 3 + 4j

# Serialize complex types
# {'real': 3.0, 'imaginary': 4.0}
serialized_complex = serialize_value(complex_value)

# Deserialize basic types
# (3+4j)
deserialize_value(serialized_complex, complex)
```

#### Pydantic Models

```python
from pydantic import BaseModel
from pyjson_translator.serialize import serialize_value, deserialize_value


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
```

#### SQLAlchemy Models

```python
from pyjson_translator.serialize import serialize_value, deserialize_value
from pyjson_translator.db_sqlalchemy_instance import default_sqlalchemy_instance as db


class AddressClass(db.Model):
    __tablename__ = 'addresses_table'
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)

class UserClass(db.Model):
    __tablename__ = 'users_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    address = db.relationship("AddressClass", backref="user", lazy='select', passive_deletes="all")

address_instance = AddressClass(id=1, street="123 Main St", city="New York", state="NY", zip="10001", user_id=1)
user_instance = UserClass(id=1, username="john_doe", email="john@example.com", address=[address_instance])

# Serialize SQLAlchemy model
# {'address': [{'city': 'New York',
#               'id': 1,
#               'state': 'NY',
#               'street': '123 Main St',
#               'zip': '10001'}],
#  'email': 'john@example.com',
#  'id': 1,
#  'username': 'john_doe'}
serialized_user = serialize_value(user_instance)

# Deserialize SQLAlchemy model
# {'address': [{'city': 'New York',
#               'id': 1,
#               'state': 'NY',
#               'street': '123 Main St',
#               'zip': '10001'}],
#  'email': 'john@example.com',
#  'id': 1,
#  'username': 'john_doe'}
deserialized_user = deserialize_value(serialized_user, UserClass)
```

#### Simple Classes

```python
from pyjson_translator.serialize import serialize_value, deserialize_value


class SimpleModel:
    def __init__(self, simple_id, name, active):
        self.simple_id = simple_id
        self.name = name
        self.active = active

    def __repr__(self):
        return f"<SimpleModel simple_id={self.simple_id}, name={self.name}, active={self.active}>"


example_model = SimpleModel(simple_id=1, name="Example", active=True)

# Serialize simple class
# {'simple_id': 1, 'name': 'Example', 'active': True}
serialized_simple_model = serialize_value(example_model)

# Deserialize simple class
# <SimpleModel simple_id=1, name=Example, active=True>
deserialized_simple_model = deserialize_value(serialized_simple_model, SimpleModel)
```

#### List with Simple Class

```python
from typing import List

from pyjson_translator.serialize import serialize_value, deserialize_value


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
# [{'simple_id': 1, 'name': 'Example', 'active': True}, {'simple_id': 2, 'name': 'Example', 'active': True}]
serialized_simple_model_list = serialize_value(simple_model_list)

# Deserialize simple class
# [<SimpleModel simple_id=1, name=Example, active=True>, <SimpleModel simple_id=2, name=Example, active=True>]
deserialized_simple_model_list = deserialize_value(serialized_simple_model_list, List[SimpleModel])
```

#### More Examples

For more examples and detailed usage, please refer to the `tests` directory in the repository.
