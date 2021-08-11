from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_503_SERVICE_UNAVAILABLE
)

from src.interfaces import MachineInterface
from src.models.routes import Simulation
from src.use_case import (CreateExecution, CreateMultipleMachines, SecurityUseCase, SessionUseCase)
from src.utils.message import GoogleMessage, MachineMessage
from src.utils.response import UJSONResponse

machine_routes = APIRouter()


@machine_routes.post("/simulation/execute")
async def execute_simulation(
    simulation: Simulation,
    user = Depends(SecurityUseCase.get_current_user),
    is_logged = Depends(SessionUseCase.create_session)
):
    if not is_logged:
        return UJSONResponse(
            GoogleMessage.unavailable,
            HTTP_503_SERVICE_UNAVAILABLE
        )

    execution = CreateExecution.handle(simulation, user)
    await CreateMultipleMachines.handle(simulation, execution, user)


    # machine_information, is_error = MachineUseCase.create(user, simulation)
    # if is_error:
    #     return UJSONResponse(GoogleMessage.error, HTTP_400_BAD_REQUEST)
    #
    # machine = MachineUseCase.save(machine_information, simulation, user)
    #
    # try:
    #     machine.save()
    # except Exception as error:
    #     UJSONResponse(str(error), HTTP_400_BAD_REQUEST)
    #
    # background_task.add_task(
    #     SimulationUseCase.send_information,
    #     machine,
    #     simulation
    # )

    return UJSONResponse(MachineMessage.created, HTTP_201_CREATED)


@machine_routes.post("/simulation/finish")
def finish_simulation():
    return {"hola": "mundo"}


@machine_routes.delete("/machine")
def delete_machine(
    background_task: BackgroundTasks,
    user = Depends(SecurityUseCase.get_current_user)
):
    machine_found = MachineInterface.find_one(user)
    if not machine_found:
        return UJSONResponse(MachineMessage.not_found, HTTP_404_NOT_FOUND)

    if not SessionUseCase.create_session():
        return UJSONResponse(GoogleMessage.not_session, HTTP_400_BAD_REQUEST)

    background_task.add_task(MachineUseCase.delete, user, machine_found)

    return UJSONResponse(MachineMessage.deleted, 200)
