from functools import wraps
from typing import Callable, Dict, Union

from cat.experimental.form import CatFormState
from cat.log import log
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemory

from .settings import NameType


def from_meowgram(func: Callable) -> Callable:
    """Decorator that checks if a message is from Meowgram before calling the function."""

    @wraps(func)
    def wrapper(*args, cat: StrayCat, **kwargs):
        user_message = cat.working_memory.user_message_json

        # Checking if `user_message` is from Meowgram
        if user_message and "meowgram" in user_message.keys():
            return func(*args, cat, **kwargs)

        log.debug("Message not coming from Meowgram.")

    return wrapper


def get_name(telegram_update) -> str | None:
    """Retrieve the user's name or username based on settings."""
    settings = MadHatter().get_plugin().load_settings()

    # Extract user information from the Telegram update
    user_info = telegram_update.get("message", {}).get("from", {})
    name = user_info.get("first_name")
    username = user_info.get("username")

    # Determine which name to use based on settings
    name_type = settings["name_to_use"]
    if name_type == NameType.NAME.value and name:
        return name
    elif name_type == NameType.USERNAME.value and username:
        return username

    return None


def handle_form_action(cat: StrayCat, form_action) -> Union[None, Dict]:
    """Handle the form action from a user message."""
    active_form = cat.working_memory.active_form
    # Check if the form name matches the active form
    if not active_form or form_action["form_name"] != active_form.name:
        return

    # Validate action and update form state accordingly
    if form_action["action"] in {"confirm", "cancel"}:
        active_form._state = CatFormState.CLOSED
        if form_action["action"] == "confirm":
            message = active_form.submit(active_form._model)

        message = active_form.message()

        # Delete form from working memory
        cat.working_memory.active_form = None

        return message


def get_send_params(cat: StrayCat, telegram_update) -> Dict:
    """Get parameters to send back to Meowgram."""
    settings = cat.mad_hatter.get_plugin().load_settings()
    send_params = {}
    # If replying to a message, set the reply_to_message_id
    if settings["reply_to"] and telegram_update.get("message"):
        send_params["reply_to_message_id"] = telegram_update["message"]["message_id"]
    return send_params


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
