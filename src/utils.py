from typing import Dict
from functools import wraps
from typing import Callable, Optional

from cat.looking_glass.stray_cat import StrayCat
from cat.memory.working_memory import WorkingMemory
from cat.log import log

from .models.message import CustomUserMessage

def from_meowgram(func: Optional[Callable] = None, *, message_type: Optional[str] = None) -> Callable:
    """
    Decorator that checks if a message is from Meowgram before calling the function.
    
    Args:
        message_type (str, optional): The type of message to check for. Defaults to None.
    """      

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, cat: StrayCat, **kwargs):
            user_message = cat.working_memory.user_message_json
            if not user_message:
                return
            
            user_message = CustomUserMessage(**user_message.model_dump())
    
            if not user_message.meowgram:
                log.debug("Message not coming from Meowgram.")
                return
            
            log.info("Message coming from Meowgram.")
            if (message_type is None) or (message_type == user_message.message_type):
                return func(*args, cat, **kwargs)

        return wrapper
    
    if func is not None:
        return decorator(func)

    return decorator


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
