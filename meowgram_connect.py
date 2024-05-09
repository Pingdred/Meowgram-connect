import json
from typing import Dict

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import hook

from .settings import NameType

def get_name(telegram_update):
    settings = MadHatter().get_plugin().load_settings()
    
    name = telegram_update["message"]["chat"].get("first_name", None)
    username = telegram_update["message"]["chat"].get("username", None)

    if settings["name_to_use"] == NameType.NAME.value and name:
        return name
    elif settings["name_to_use"] == NameType.USERNAME.value and username:
        return username
    
    return None

@hook
def after_cat_recalls_memories(cat) -> Dict:

    user_message = cat.working_memory.user_message_json
    # This key exist only if the message is from Meowgram
    # if not exists we don't need to do anything
    if "meowgram" not in user_message.keys():
        return
    
    # Get the name from the telegram update
    telegram_update = json.loads(user_message["meowgram"]["update"])
    name = get_name(telegram_update)    

    # Update name in chat history
    cat.working_memory.history[-1]["who"] = name


@hook
def before_cat_sends_message(message, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    user_message = cat.working_memory["user_message_json"]

    # This key exist only if the message is from Meowgram
    # if not exists we don't need to do anything
    if "meowgram" not in user_message.keys():
        return
    
    telegram_update = json.loads(user_message["meowgram"]["update"])

    message["meowgram"] = {
        "send_params": {},
    }
    send_params = message["meowgram"]["send_params"]

    if settings["reply_to"]:
        send_params["reply_to_message_id"] = telegram_update["message"]["message_id"]
    

    return message     
