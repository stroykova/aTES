from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import pathlib
from typing import Literal
import json

EVENT_VERSION = 2


class Event(BaseModel):
    event_id: UUID
    event_version: Literal[2]
    event_domain: Literal['tasks']
    event_name: str = Field(..., min_length=1)
    event_time: str = Field(..., min_length=1)  # format???
    producer: str = Field(..., min_length=1)
    data: dict


class TaskV2(BaseModel):
    title: str
    jira_id: str = Field(pattern=r"^[^\[\]]+$")
    assignee: str = Field(..., min_length=1)
    initial_cost: int
    done_cost: int
    id: int


class TaskCreatedV2(Event):
    event_name: Literal['TaskCreated']
    data: TaskV2


EVENT_CLASS = TaskCreatedV2


if __name__ == '__main__':
    file_path = pathlib.Path(__file__).parent / f'v{EVENT_VERSION}.json'
    print(file_path)
    with open(file_path, 'w') as f:
        print(EVENT_CLASS.model_json_schema())
        json.dump(EVENT_CLASS.model_json_schema(), f, indent=4)