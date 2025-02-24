from pydantic import BaseModel
from typing import Optional

from .enums import PayloadType
from .user import UserInfo

class ReplyTo(BaseModel):
    when: float
    is_from_bot: bool = False
    text: Optional[str] = None
    audio: Optional[str] = None
    image: Optional[str] = None


class NewMessageData(BaseModel):
    message_id: int
    user_info: UserInfo
    reply_to_message: Optional[ReplyTo]


class FormActionData(BaseModel):
    form_name: str
    action: str


class MeowgramPayload(BaseModel):
    data: FormActionData | NewMessageData

    @property
    def mtype(self) -> Optional[PayloadType]:
        types_lookup = {
            FormActionData: PayloadType.FORM_ACTION,
            NewMessageData: PayloadType.NEW_MESSAGE,
        }

        if t := types_lookup.get(type(self.data)):
            return t
    

