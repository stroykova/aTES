from kafka import KafkaConsumer
from main import con
import time
import json
from schemas.schemas.tasks.TaskCreated.v1 import TaskCreatedV1, TaskV1
from schemas.schemas.tasks.TaskCreated.v2 import TaskCreatedV2, TaskV2
from schemas.check import check_event

print('consumer connected')
jobs_done = 0
total_time = 0
while True:
    time.sleep(1)
    consumer = KafkaConsumer('tasks_stream',
                             bootstrap_servers=['kafka:29092', 'kafka2:29093'], api_version=(0, 10, 1))
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        check_event(data)
        if data['event_name'] == 'TaskCreated' and data['event_version'] == 1:
            task_event = TaskCreatedV1(**data)
            task_data = task_event.data
            statement = (
                "insert into tasks (id, description, assignee, initial_cost, done_cost) "
                f"values ('{task_data.id}', '{task_data.description}', '{task_data.assignee}', '{task_data.initial_cost}', '{task_data.done_cost}')"
            )
            print(statement)
            cur = con.cursor()
            cur.execute(statement)
            con.commit()
        elif data['event_name'] == 'TaskCreated' and data['event_version'] == 2:
            task_event = TaskCreatedV2(**data)
            task_data = task_event.data
            statement = (
                "insert into tasks (id, jira_id, title, assignee, initial_cost, done_cost) "
                f"values ('{task_data.id}', '{task_data.jira_id}', '{task_data.title}', '{task_data.assignee}', '{task_data.initial_cost}', '{task_data.done_cost}')"
            )
            print(statement)
            cur = con.cursor()
            cur.execute(statement)
            con.commit()
        
