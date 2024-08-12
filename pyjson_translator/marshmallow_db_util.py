from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_sqlalchemy_instance import default_sqlalchemy_instance as db
from .error_handle import fail_to_translator

GLOBAL_DB_SCHEMA_CACHE = {}


def generate_db_schema(input_class_instance: any,
                       db_sqlalchemy_instance: SQLAlchemy = db,
                       db_sqlalchemy_merge: bool = False):
    input_db_class = input_class_instance.__class__

    if input_db_class in GLOBAL_DB_SCHEMA_CACHE:
        return GLOBAL_DB_SCHEMA_CACHE[input_db_class]

    def get_nested_schema(relation_class_instance):
        related_model = relation_class_instance.mapper.entity
        related_instance = related_model()
        return generate_db_schema(related_instance, db_sqlalchemy_instance, db_sqlalchemy_merge)

    schema_fields = {}
    for attr_name, relation in input_db_class.__mapper__.relationships.items():
        if relation.uselist:
            nested_db_schema = get_nested_schema(relation)
            if nested_db_schema:
                schema_fields[attr_name] = fields.Nested(nested_db_schema, many=True)

    class Meta:
        model = input_db_class
        load_instance = db_sqlalchemy_merge
        sqla_session = db_sqlalchemy_instance.session

    schema_class = type(f"{input_db_class.__name__}Schema", (SQLAlchemyAutoSchema,),
                        {"Meta": Meta, **schema_fields})

    GLOBAL_DB_SCHEMA_CACHE[input_db_class] = schema_class
    return schema_class


def orm_class_to_dict(instance: any,
                      db_sqlalchemy_instance: SQLAlchemy = db,
                      db_sqlalchemy_merge: bool = False):
    schema = generate_db_schema(instance, db_sqlalchemy_instance, db_sqlalchemy_merge)()
    return schema.dump(instance)


def orm_class_from_dict(cls: type,
                        data: any,
                        db_sqlalchemy_instance: SQLAlchemy = db,
                        db_sqlalchemy_merge: bool = False):
    pre_check_sqlalchemy(db_sqlalchemy_instance, db_sqlalchemy_merge)

    schema = generate_db_schema(cls(), db_sqlalchemy_instance, db_sqlalchemy_merge)()
    schema_object = schema.load(data)

    if db_sqlalchemy_merge:
        return db_sqlalchemy_instance.session.merge(schema_object)
    else:
        return schema_object


def pre_check_sqlalchemy(db_sqlalchemy_instance: SQLAlchemy = None,
                         db_sqlalchemy_merge: bool = False):
    if db_sqlalchemy_merge and not db_sqlalchemy_instance:
        fail_to_translator("db_sqlalchemy_merge is True but no db_sqlalchemy_instance provided.")
