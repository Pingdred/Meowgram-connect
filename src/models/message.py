from typing import Optional

from langchain_core.messages import HumanMessage

from cat.convo.messages import UserMessage

from .user import UserInfo
from .enums import PayloadType
from .payload import MeowgramPayload, FormActionData


class CustomUserMessage(UserMessage):
    meowgram: MeowgramPayload

    def langchainfy(self) -> HumanMessage:
        message = super().langchainfy()

        image_uri = self.reply_to_image
        if image_uri:
            if image := self._langchainfy_image(image_uri):
                message.content.insert(0, image)

        text = self.reply_to_text
        if text:
            message.content.insert(0, {"type": "text", "text": f"**Replying to**: {text}"})    

        return message
    
    def _langchainfy_image(self, image: str) -> Optional[dict]:
        user_message = UserMessage(
            user_id=self.user_id,
            image=image
        )
        return user_message.langchainfy_image()

    @property
    def reply_to_text(self) -> Optional[str]:
        """
        Return the text of the message being replied to.
        Short hand for `.meowgram.data.reply_to_message.text` if the message is a new message
        and there is a message being replied to.
        
        Returns:
            text (str | None): The text of the message being replied to.
        """
        if self.meowgram.mtype != PayloadType.NEW_MESSAGE:
            return None
        
        if self.meowgram.data.reply_to_message is None:
            return None
        
        if self.meowgram.data.reply_to_message.is_from_bot:
            return f"**Your previous message**:\n {self.meowgram.data.reply_to_message.text}"
        return f"**User previous message**:\n {self.meowgram.data.reply_to_message.text}"

    @property
    def reply_to_image(self) -> Optional[str]:
        """
        Return the image uri/url of the message being replied to.
        Short hand for `.meowgram.data.reply_to_message.image` if the message is a new message
        and there is a message being replied to.
        
        Returns:
            image (str | None): The image uri/url of the message being replied to.
        """

        if self.meowgram.mtype != PayloadType.NEW_MESSAGE:
            return None
        
        if self.meowgram.data.reply_to_message is None:
            return None
        
        return self.meowgram.data.reply_to_message.image
        
    @property
    def user_info(self) -> Optional[UserInfo]:
        """
        Return the user info.
        Short hand for `.meowgram.data` if the message is a new message.
        
        Returns:
            user_info (UserInfo | None): The user info if the message is a new message.
        """
        if self.meowgram.mtype != PayloadType.NEW_MESSAGE:
            return None
        return self.meowgram.data.user_info
    
    @property
    def message_id(self) -> Optional[int]:
        """
        Return the message id.
        Short hand for `.meowgram.data` if the message is a new message.
        
        Returns:
            message_id (int | None): The message id if the message is a new message.
        """
        if self.meowgram.mtype != PayloadType.NEW_MESSAGE:
            return None
        return self.meowgram.data.message_id
    
    @property
    def form_action(self) -> Optional[FormActionData]:
        """
        Return the form action data.
        Short hand for `.meowgram.data` if the message is a form action.

        Returns:
            form action (FormActionData, None): The form action data if the message is a form action.
        """
        if self.meowgram.mtype != PayloadType.FORM_ACTION:
            return None
        return self.meowgram.data
    
    @property
    def message_type(self) -> PayloadType:
        """
        Return the meowgram message type.
        Short hand for `.meowgram.type`.
        """
        return self.meowgram.type
