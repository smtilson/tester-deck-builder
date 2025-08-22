from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    version: str = "0.0.0"
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )