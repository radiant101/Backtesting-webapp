from pydantic import BaseModel,Field,EmailStr
from datetime import datetime
from typing import Literal
from typing import Optional

class Strategy_Input(BaseModel):
    strat_name: str
    symbol : str
    start_date:datetime
    end_date:datetime
    short_window:int = Field(gt=0,)
    long_window: int =Field(gt=0,)

class Rsi_Input(BaseModel):
    strat_name: str
    symbol : str=Field()
    start_date:datetime=Field()
    end_date:datetime=Field()

class user_create(BaseModel):
     email_id : EmailStr
     password: str

class user_out(BaseModel):
     user_id : int
     email_id : EmailStr
     created_at :datetime


class Config:
        orm_mode = True