from datetime import datetime, time

from pydantic import BaseModel


class UserModel(BaseModel):
    id: int
    notification_time: time
    created_at: datetime
    updated_at: datetime
