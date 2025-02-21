import sys

from typing import Dict

from cat.mad_hatter.decorators import hook
from cat.looking_glass.stray_cat import StrayCat

from ..models import PayloadType, CustomUserMessage
from ..settings import MeogramConnectSettings, NameType
from ..utils import get_form_state, get_meowgram_settings, from_meowgram


@hook(priority=sys.maxsize)
@from_meowgram
def before_cat_reads_message(_, cat: StrayCat) -> None:
    # If the message is from mewogram, convert the user message to a custom user message
    # to have acces to utility methods
    user_message = cat.working_memory.user_message_json
    return CustomUserMessage(**user_message.model_dump())


@hook
@from_meowgram(message_type=PayloadType.NEW_MESSAGE)
def after_cat_recalls_memories(cat: StrayCat) -> None:
    """Update chat history with the user's name after recalling memories."""
    user_message: CustomUserMessage = cat.working_memory.user_message_json
    settings = MeogramConnectSettings(**cat.mad_hatter.get_plugin().load_settings())

    if not user_message.user_info:
        # Use the default name
        return
    
    # Here there should be at least one entry in the chat history
    # the enstry for the last message sent by the user
    last_entry = cat.working_memory.history[-1]

    if settings.name_to_use == NameType.USERNAME:
        last_entry.who = user_message.user_info.username
        return
    
    if settings.name_to_use == NameType.NAME:
        last_entry.who = user_message.user_info.first_name

    # else, use the default name    


@hook
@from_meowgram(message_type=PayloadType.NEW_MESSAGE)
def before_cat_sends_message(message, cat: StrayCat) -> Dict:
    """Prepare message with Meowgram-specific parameters before sending."""
    user_message: CustomUserMessage = cat.working_memory.user_message_json
    settings = MeogramConnectSettings(**cat.mad_hatter.get_plugin().load_settings())

    reply_to = {
        "reply_to": user_message.message_id,
    }

    # Prepare Meowgram-specific parameters
    message.meowgram = {
        "send_params": reply_to if settings.reply_to else {},
        "settings": get_meowgram_settings(cat),
        "active_form": get_form_state(cat.working_memory) if settings.show_form_buttons else None,
    }
    return message


