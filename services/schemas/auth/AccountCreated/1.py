from pydantic import BaseModel, Field

EVENT_NAME = 'AccountCreated'


class UserV1(BaseModel):
    username: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)


class AccountCreatedV1(BaseModel):
    event_name: str = Field(EVENT_NAME, const=True)
    data: UserV1