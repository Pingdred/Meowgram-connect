from enum import Enum
from pydantic import BaseModel, Field

from cat.mad_hatter.decorators import plugin

class NameType(Enum):
    DEFAULT = "Cheshire Cat default"
    NAME = "Name"
    USERNAME = "Username"


class MeogramConnectSettings(BaseModel):
    name_to_use: NameType = Field(
        title="Name",
        description="The Cheshire Cat can use the Name or Username of your Telegram account",
        default=NameType.NAME
    )
    reply_to: bool = Field(
        title="Reply to",
        description="The Cheshire cat will quote the message it is responding to",
        default=True
    )
    show_form_buttons: bool = Field(
        title="Show Form Buttons",
        description="Show buttons for form actions",
        default=True
    )
    show_tts_text: bool = Field(
        title="Show Voice Note Transciption",
        description="Show transcript when the message is a voice note",
        default=True
    )


@plugin
def settings_model():   
    return MeogramConnectSettings
