from pydantic import BaseModel
from datetime import time, datetime


class UserModel(BaseModel):
    id: int
    notification_time: time
    created_at: datetime
