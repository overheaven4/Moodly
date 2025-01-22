from pydantic import BaseModel
from datetime import time, datetime


class UserModel(BaseModel):
    id: int  # Telegram ID пользователя
    notification_time: time
    created_at: datetime
    updated_at: datetime
