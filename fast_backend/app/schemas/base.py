from pydantic import BaseModel, ConfigDict

class SettingsSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )

class BaseSchema(SettingsSchema):
    version: str = "0.0.0"
    