from uuid import UUID

from pydantic import BaseModel, Field


class Machine(BaseModel):
    cpu: int = Field(2, ge=1, le=8)
    memory: int = Field(2048)
    instances: int = Field(1, le=5)


class Simulation(BaseModel):
    machine: Machine = Field(...)
    simulation_id: UUID = Field(...)
    data: dict = Field(...)
