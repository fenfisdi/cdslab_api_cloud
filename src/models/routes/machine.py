from pydantic import BaseModel, Field


class NewMachine(BaseModel):
    cpu: int = Field(...)
    memory: int = Field(...)
