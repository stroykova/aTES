from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import pathlib
from typing import Literal
import json

EVENT_VERSION = 1


class Event(BaseModel):
    event_id: UUID
    event_version: Literal[1]
    event_domain: Literal['tasks']
    event_name: str = Field(..., min_length=1)
    event_time: str = Field(..., min_length=1)  # format???
    producer: str = Field(..., min_length=1)
    data: dict



class TasksShuffledV1(Event):
    event_name: Literal['TasksShuffled']
    data: dict = {}


EVENT_CLASS = TasksShuffledV1


if __name__ == '__main__':
    file_path = pathlib.Path(__file__).parent / f'v{EVENT_VERSION}.json'
    print(file_path)
    with open(file_path, 'w') as f:
        print(EVENT_CLASS.model_json_schema())
        json.dump(EVENT_CLASS.model_json_schema(), f, indent=4)