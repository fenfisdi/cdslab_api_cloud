from pydantic import BaseModel, Field


class NewMachine(BaseModel):
    name: str = Field(...)
