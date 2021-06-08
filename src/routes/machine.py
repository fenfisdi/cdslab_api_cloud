from fastapi import APIRouter, Depends
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from src.models.routes import NewMachine
from src.use_case import SecurityUseCase
from src.use_case.gcloud import MachineUseCase, SessionUseCase
from src.utils.message import GoogleMessage
from src.utils.response import UJSONResponse

machine_routes = APIRouter()


@machine_routes.post("/machine")
def create_machine(
    machine: NewMachine,
    user=Depends(SecurityUseCase.get_current_user)
):
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

    return UJSONResponse(GoogleMessage.created, HTTP_201_CREATED)

