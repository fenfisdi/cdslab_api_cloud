from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.background import BackgroundTasks
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)

from src.interfaces import ExecutionInterface
from src.models.routes import Simulation
from src.use_case import (
    CreateExecution,
    CreateMultipleMachines,
    ProcessInformation,
    SecurityUseCase,
    SendSimulationData,
    SessionUseCase,
    StopSimulationEmergency,
    TestMachine
)
from src.utils.message import ExecutionMessage, GoogleMessage, MachineMessage
from src.utils.response import UJSONResponse

machine_routes = APIRouter(
    prefix="/root",
    include_in_schema=False
)


@machine_routes.post("/simulation/execute")
async def execute_simulation(
    simulation: Simulation,
    background_tasks: BackgroundTasks,
    user = Depends(SecurityUseCase.get_current_user),
    is_logged = Depends(SessionUseCase.create_session)
):
    if not is_logged:
        return UJSONResponse(
            GoogleMessage.unavailable,
            HTTP_503_SERVICE_UNAVAILABLE
        )

    execution = CreateExecution.handle(simulation, user)
    is_valid = ProcessInformation.handle(
        simulation.data,
        simulation.simulation_id
    )
    if not is_valid:
        return UJSONResponse(ExecutionMessage.invalid, HTTP_400_BAD_REQUEST)
    await CreateMultipleMachines.handle(simulation, execution, user)
    TestMachine.handle(execution)

    background_tasks.add_task(
        SendSimulationData.handle,
        simulation,
        execution
    )

    return UJSONResponse(MachineMessage.created, HTTP_201_CREATED)


@machine_routes.post("/simulation/{simulation_uuid}/finish")
def finish_simulation(
    simulation_uuid: UUID,
    data: dict = None,
    is_emergency: bool = Query(False),
    is_logged = Depends(SessionUseCase.create_session)
):
    if not is_logged:
        return UJSONResponse(
            GoogleMessage.unavailable,
            HTTP_503_SERVICE_UNAVAILABLE
        )
    execution = ExecutionInterface.find_one_by_simulation(simulation_uuid)
    if not execution:
        return UJSONResponse(ExecutionMessage.not_found, HTTP_404_NOT_FOUND)

    if is_emergency:
        instance_name = data.get("name")
        has_error = StopSimulationEmergency.handle(
            execution,
            instance_name
        )
        if has_error:
            return UJSONResponse(
                MachineMessage.can_not_stop,
                HTTP_500_INTERNAL_SERVER_ERROR
            )

        return UJSONResponse(ExecutionMessage.failure, HTTP_200_OK)
    # TODO: delete machine and set finish status
    return UJSONResponse(ExecutionMessage.finish, HTTP_200_OK)
