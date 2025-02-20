from typing import Dict, Union

from cat.convo.messages import UserMessage
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.decorators import hook
from cat.log import log

from .settings import MeogramConnectSettings
from .utils import (
    get_form_state,
    get_meowgram_settings,
    get_name,
    get_send_params,
    handle_form_action,
    from_meowgram,
    MeowgramPayload,
    PayloadType
)

    
@hook
@from_meowgram
def agent_fast_reply(fast_reply, cat: StrayCat) -> Union[None, Dict]:
    """Handle fast replies to user messages."""
    user_message: UserMessage = cat.working_memory.user_message_json
    meowgram_payload = MeowgramPayload(**user_message.meowgram)

    if meowgram_payload.type == PayloadType.FORM_ACTION:
        form_action = meowgram_payload.data

        try:    
            return handle_form_action(cat, form_action)
        except Exception as e:
            log.error(f"Error handling form action: {e}")


@hook
@from_meowgram
def after_cat_recalls_memories(cat: StrayCat) -> None:
    """Update chat history with the user's name after recalling memories."""
    user_message: UserMessage = cat.working_memory.user_message_json
    meowgram_payload = MeowgramPayload(**user_message.meowgram)

    if meowgram_payload.type != PayloadType.NEW_MESSAGE:
        return

    # Parse the Telegram update and get the user's name
    name = get_name(meowgram_payload.data.update)

    # Update the last entry in chat history with the user's name
    if name:
        cat.working_memory.history[-1].who = name


@hook
@from_meowgram
def before_cat_sends_message(message, cat: StrayCat) -> Dict:
    """Prepare message with Meowgram-specific parameters before sending."""
    user_message: UserMessage = cat.working_memory.user_message_json
    settings = MeogramConnectSettings(**cat.mad_hatter.get_plugin().load_settings())

    meowgram_payload = MeowgramPayload(**user_message.meowgram)

    if meowgram_payload.type != PayloadType.NEW_MESSAGE:
        return message

    # Parse the Telegram update
    telegram_update = meowgram_payload.data.update

    # Prepare Meowgram-specific parameters
    message.meowgram = {
        "send_params": get_send_params(cat, telegram_update),
        "settings": get_meowgram_settings(cat),
        "active_form": get_form_state(cat.working_memory) if settings.show_form_buttons else None,
    }
    return message
