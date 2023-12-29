import json
from typing import Dict

from cat.log import log

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
def before_agent_starts(agent_input: Dict, cat) -> Dict:

    user_message = cat.working_memory["user_message_json"]

    # This key exist only if the message is from Meowgram
    # if not exists we don't need to do anything
    if "meowgram" not in user_message.keys():
        return
    
    telegram_update = json.loads(user_message["meowgram"]["update"])

    name = get_name(telegram_update)

    log.critical(f"BEFORE: {name}, {not name}")
    
    if name is None:
        log.critical("NO")
        return
    
    agent_input["chat_history"] = agent_input["chat_history"].replace("- Human:", f"- {name}:")

    return agent_input


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


@hook
def agent_prompt_suffix(suffix, cat):
    user_message = cat.working_memory["user_message_json"]

    # This key exist only if the message is from Meowgram
    # if not exists we don't need to do anything
    if "meowgram" not in user_message.keys():
        return

    telegram_update = json.loads(user_message["meowgram"]["update"])

    name = get_name(telegram_update)
    
    if name is None:
        return

    suffix = f"""
# Context
{{episodic_memory}}
{{declarative_memory}}
{{tools_output}}

## Conversation until now:{{chat_history}}
- {name}: {{input}}
- AI: """

    return suffix

        
