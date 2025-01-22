from pydantic import BaseModel
from datetime import date, datetime
from typing import Dict


class SurveyResultModel(BaseModel):
    id: int
    user_id: int
    answer: Dict
    created_at: datetime
