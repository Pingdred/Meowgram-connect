from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    id: int
    username: str
    first_name: Optional[str] 
    last_name: Optional[str]

