from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND
)

from src.interfaces import MachineInterface
from src.models.routes import NewMachine
from src.use_case import SecurityUseCase
from src.use_case.gcloud import MachineUseCase, SessionUseCase
from src.utils.message import GoogleMessage, MachineMessage
from src.utils.response import UJSONResponse

machine_routes = APIRouter()


@machine_routes.post("/machine")
def create_machine(
    machine: NewMachine,
    user=Depends(SecurityUseCase.get_current_user)
):
    machine_found = MachineInterface.find_one(user)
    if machine_found:
        data = {
            'ip': machine_found.ip,
            'name': '...' + machine_found.name[-4::],
            'zone': machine_found.zone,
        }
        return UJSONResponse(
            MachineMessage.exist,
            HTTP_200_OK,
            data
        )
    if not SessionUseCase.create_session():
        return UJSONResponse(GoogleMessage.not_session, HTTP_400_BAD_REQUEST)

    machine_information, is_error = MachineUseCase.create(user)
    if is_error:
        return UJSONResponse(GoogleMessage.error, HTTP_400_BAD_REQUEST)

    machine = MachineUseCase.save(machine_information, user)

    try:
        machine.save()
    except Exception as error:
        UJSONResponse(str(error), HTTP_400_BAD_REQUEST)

    return UJSONResponse(MachineMessage.created, HTTP_201_CREATED)


@machine_routes.delete("/machine")
def delete_machine(
    background_task: BackgroundTasks,
    user=Depends(SecurityUseCase.get_current_user)
):
    machine_found = MachineInterface.find_one(user)
    if not machine_found:
        return UJSONResponse(MachineMessage.not_found, HTTP_404_NOT_FOUND)

    if not SessionUseCase.create_session():
        return UJSONResponse(GoogleMessage.not_session, HTTP_400_BAD_REQUEST)

    background_task.add_task(MachineUseCase.delete, user, machine_found)

    return UJSONResponse(MachineMessage.deleted, 200)
