from typing import List

from pydantic import BaseModel, create_model, ConfigDict
from sqlalchemy import TypeDecorator

GLOBAL_DB_SCHEMA_CACHE = {}


def generate_db_schema(sqlalchemy_model):
    if sqlalchemy_model in GLOBAL_DB_SCHEMA_CACHE:
        return GLOBAL_DB_SCHEMA_CACHE[sqlalchemy_model]

    # 创建字段字典
    fields = {}
    for column in sqlalchemy_model.__table__.columns:
        try:
            if isinstance(column.type, TypeDecorator):
                python_type = column.type.impl.python_type
            else:
                python_type = column.type.python_type
        except NotImplementedError:
            python_type = str  # Fallback to str if python_type is not implemented
        # noinspection PyUnresolvedReferences
        default = None if column.default is None else column.default.arg
        fields[column.name] = (python_type, default)

    # 处理关系字段
    for attr_name, relation in sqlalchemy_model.__mapper__.relationships.items():
        related_model = relation.mapper.entity
        if relation.uselist:
            nested_model = generate_db_schema(related_model)
            fields[attr_name] = (List[nested_model], None)

    pydantic_model = create_model(
        sqlalchemy_model.__name__ + 'Model',
        __base__=BaseModel,
        **fields
    )

    class Config:
        orm_mode = False

    pydantic_model.Config = Config
    pydantic_model.model_config = ConfigDict(
        from_attributes=True,
    )
    pydantic_model._original_class = sqlalchemy_model
    GLOBAL_DB_SCHEMA_CACHE[sqlalchemy_model] = pydantic_model
    return pydantic_model


def convert_instance_to_pydantic(instance):
    model_class = generate_db_schema(instance.__class__)
    instance_dict = instance.__dict__.copy()
    for attr_name, relation in instance.__mapper__.relationships.items():
        if relation.uselist:
            instance_dict[attr_name] = [convert_instance_to_pydantic(related_instance) for related_instance in
                                        getattr(instance, attr_name)]
    return model_class(**instance_dict)


def pydantic_to_sqlalchemy(pydantic_instance):
    sqlalchemy_class = pydantic_instance.__class__._original_class
    instance_dict = {}

    for attr_name in pydantic_instance.model_fields:
        field_value = getattr(pydantic_instance, attr_name)
        if isinstance(field_value, list) and field_value and isinstance(field_value[0], BaseModel):
            instance_dict[attr_name] = [pydantic_to_sqlalchemy(item) for item in field_value]
        elif isinstance(field_value, BaseModel):
            instance_dict[attr_name] = pydantic_to_sqlalchemy(field_value)
        else:
            instance_dict[attr_name] = field_value

    sqlalchemy_instance = sqlalchemy_class()
    for attr_name, value in instance_dict.items():
        setattr(sqlalchemy_instance, attr_name, value)

    return sqlalchemy_instance


def orm_class_to_dict(instance: any):
    instance_dict = convert_instance_to_pydantic(instance).model_dump()
    return instance_dict


def orm_class_from_dict(cls: type,
                        data: any):
    model_class = generate_db_schema(cls)
    model_instance = model_class(**data)
    original_instance = pydantic_to_sqlalchemy(model_instance)
    return original_instance
