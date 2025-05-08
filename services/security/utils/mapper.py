from typing import Type, Any
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def map_to_schema(model: Base, schema: Type[BaseModel]) -> dict:
    model_dict = {key: value for key, value in vars(model).items() if not key.startswith("_")}
    return schema(**model_dict).dict()