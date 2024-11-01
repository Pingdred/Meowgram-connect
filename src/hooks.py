import json
from typing import Dict, Union

from cat.convo.messages import UserMessage
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.decorators import hook

from .utils import (
    get_form_state,
    get_meowgram_settings,
    get_name,
    get_send_params,
    handle_form_action,
    from_meowgram,
)


@hook
@from_meowgram
def agent_fast_reply(fast_reply, cat: StrayCat) -> Union[None, Dict]:
    """Handle fast replies to user messages."""
    user_message: UserMessage = cat.working_memory.user_message_json

    # Check if there is a form action
    if "form_action" in user_message["meowgram"].keys():
        form_action = user_message["meowgram"]["form_action"]

        return handle_form_action(cat, form_action)


@hook
@from_meowgram
def after_cat_recalls_memories(cat: StrayCat) -> Dict:
    """Update chat history with the user's name after recalling memories."""
    user_message: UserMessage = cat.working_memory.user_message_json

    # Parse the Telegram update and get the user's name
    telegram_update = json.loads(user_message["meowgram"]["update"])
    name = get_name(telegram_update)

    # Update the last entry in chat history with the user's name
    if name:
        cat.working_memory.history[-1]["who"] = name


@hook
@from_meowgram
def before_cat_sends_message(message, cat: StrayCat) -> Dict:
    """Prepare message with Meowgram-specific parameters before sending."""
    user_message: UserMessage = cat.working_memory["user_message_json"]

    # Parse the Telegram update
    telegram_update = json.loads(user_message["meowgram"]["update"])

    # Prepare Meowgram-specific parameters
    message["meowgram"] = {
        "send_params": get_send_params(cat, telegram_update),
        "settings": get_meowgram_settings(cat),
        "active_form": get_form_state(cat.working_memory),
    }
    return message
