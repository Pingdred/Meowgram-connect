from typing import Dict, Union

from cat.convo.messages import UserMessage, ConversationMessage, CatMessage
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.decorators import hook
from cat.log import log

from .settings import MeogramConnectSettings, NameType
from .utils import (
    get_form_state,
    get_meowgram_settings,
    handle_form_action,
    from_meowgram,
    MeowgramPayload,
    PayloadType
)

    
@hook
@from_meowgram
def agent_fast_reply(_, cat: StrayCat) -> Union[None, Dict]:
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
def before_agent_starts(_, cat: StrayCat):
    chat_history = cat.working_memory.history
    settings = MeogramConnectSettings(**cat.mad_hatter.get_plugin().load_settings())

    user_message: UserMessage = cat.working_memory.user_message_json
    meowgram_payload = MeowgramPayload(**user_message.meowgram)

    if meowgram_payload.type != PayloadType.NEW_MESSAGE:
        return
    
    if meowgram_payload.data.reply_to_message is None:
        return
    
    # Get the user's name to use
    match settings.name_to_use:
        case NameType.NAME:
            name = meowgram_payload.data.user_info.first_name
        case NameType.USERNAME:
            name = meowgram_payload.data.user_info.username
        case _:
            name = None
        
    log.critical(meowgram_payload.data.reply_to_message)

    data = {
        "user_id": cat.user_id,
        "when": meowgram_payload.data.reply_to_message.when,
        "text": meowgram_payload.data.reply_to_message.text,
        "image": meowgram_payload.data.reply_to_message.image,
    }

    if meowgram_payload.data.reply_to_message.is_from_bot:
        reply_to_message = CatMessage(
            **data
        )
        chat_history.insert(-1, reply_to_message)
        return

    reply_to_message = UserMessage(
        **data
    )
    if name:
        reply_to_message.who = name
    chat_history.insert(-1, reply_to_message)


@hook
@from_meowgram
def after_cat_recalls_memories(cat: StrayCat) -> None:
    """Update chat history with the user's name after recalling memories."""
    user_message: UserMessage = cat.working_memory.user_message_json
    settings = MeogramConnectSettings(**cat.mad_hatter.get_plugin().load_settings())
    meowgram_payload = MeowgramPayload(**user_message.meowgram)

    if meowgram_payload.type != PayloadType.NEW_MESSAGE:
        return
    
    # Get the user's name to use
    match settings.name_to_use:
        case NameType.NAME:
            name = meowgram_payload.data.user_info.first_name
        case NameType.USERNAME:
            name = meowgram_payload.data.user_info.username
        case _:
            return
        
    # Update the last entry in chat history with the user's name
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
    telegram_update = meowgram_payload.data

    reply_to = {
        "reply_to": telegram_update.message_id,
    }

    # Prepare Meowgram-specific parameters
    message.meowgram = {
        "send_params": reply_to if settings.reply_to else {},
        "settings": get_meowgram_settings(cat),
        "active_form": get_form_state(cat.working_memory) if settings.show_form_buttons else None,
    }
    return message
