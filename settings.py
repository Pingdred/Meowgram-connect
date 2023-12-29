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
        description="Choose if you want to use the Name or Username",
        default=True
    )
    

@plugin
def settings_model():   
    return MeogramConnectSettings