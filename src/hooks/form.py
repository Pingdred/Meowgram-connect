from typing import Dict, Union

from cat.looking_glass.stray_cat import StrayCat
from cat.experimental.form import CatFormState
from cat.mad_hatter.decorators import hook
from cat.log import log

from ..models import PayloadType, FormActionData, CustomUserMessage
from ..utils import from_meowgram

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


@hook
@from_meowgram(message_type=PayloadType.FORM_ACTION)
def agent_fast_reply(_, cat: StrayCat) -> Union[None, Dict]:
    """Handle fast replies to user messages."""
    try:    
        user_message: CustomUserMessage = cat.working_memory.user_message_json
        return handle_form_action(cat, user_message.form_action)
    except Exception as e:
        log.error(f"Error handling form action: {e}")


