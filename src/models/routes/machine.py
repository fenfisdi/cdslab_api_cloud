from uuid import UUID

from pydantic import BaseModel, Field


class Machine(BaseModel):
    cpu: int = Field(2)
    memory: int = Field(2048)


class Simulation(BaseModel):
    machine: Machine = Field(...)
    simulation_id: UUID = Field(...)
    data: dict = Field(...)
