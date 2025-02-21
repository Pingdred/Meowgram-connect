from enum import Enum
from functools import wraps
from typing import Callable, Dict, Union, Optional

from pydantic import BaseModel

from cat.experimental.form import CatFormState
from cat.log import log
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemory

from .settings import NameType

class PayloadType(Enum):
    FORM_ACTION = "form_action"
    NEW_MESSAGE = "new_message"
    USER_ACTION = "user_action" 


class UserInfo(BaseModel):
    id: int
    username: str
    first_name: str | None 
    last_name: str | None


class ReplyTo(BaseModel):
    when: float
    is_from_bot: bool = False
    text: Optional[str] = None
    audio: Optional[str] = None
    image: Optional[str] = None


class NewMessageData(BaseModel):
    message_id: int
    user_info: UserInfo
    reply_to_message: ReplyTo | None  


class FormActionData(BaseModel):
    form_name: str
    action: str


class MeowgramPayload(BaseModel):
    data: FormActionData | NewMessageData

    @property
    def type(self) -> PayloadType:
        if isinstance(self.data, FormActionData):
            return PayloadType.FORM_ACTION
        return PayloadType.NEW_MESSAGE   


def from_meowgram(func: Callable) -> Callable:
    """Decorator that checks if a message is from Meowgram before calling the function."""

    @wraps(func)
    def wrapper(*args, cat: StrayCat, **kwargs):
        user_message = cat.working_memory.user_message_json

        # Checking if `user_message` is from Meowgram
        if user_message and ("meowgram" in user_message.keys()):
            return func(*args, cat, **kwargs)

        log.debug("Message not coming from Meowgram.")

    return wrapper


def handle_form_action(cat: StrayCat, form_action: FormActionData) -> Union[None, Dict]:
    """Handle the form action from a user message."""
    active_form = cat.working_memory.active_form
    # Check if the form name matches the active form
    if not active_form or form_action.form_name != active_form.name:
        return

    # Validate action and update form state accordingly
    if form_action.action in {"confirm", "cancel"}:
        # Delete form from working memory
        log.debug("Deleting form form working memory")
        cat.working_memory.active_form = None

        # Close the form
        active_form._state = CatFormState.CLOSED
        
        # Submit the form if confirmed
        if form_action.action == "confirm":
           return active_form.submit(active_form._model)

        # Else closing message if cancelled
        return active_form.message()


def get_meowgram_settings(cat: StrayCat) -> Dict:
    """Retrieve Meowgram-specific settings."""
    settings = cat.mad_hatter.get_plugin().load_settings()
    return {
        "show_tts_text": settings[
            "show_tts_text"
        ]  # Include TTS text visibility setting
    }


def get_form_state(working_memory: WorkingMemory) -> Dict:
    """Get the current state of the active form."""
    if working_memory.active_form is None:
        return None

    # Return the form's name and its current state
    return {
        "name": working_memory.active_form.name,
        "state": working_memory.active_form._state.value,
    }
