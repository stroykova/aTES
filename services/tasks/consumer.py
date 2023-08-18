from kafka import KafkaConsumer
from main import con
import time
import json
from schemas.schemas.auth.AccountCreated.v1 import AccountCreatedV1
from schemas.check import check_event

print('consumer connected')
jobs_done = 0
total_time = 0
while True:
    time.sleep(1)
    consumer = KafkaConsumer('accounts_stream',
                             bootstrap_servers=['kafka:29092', 'kafka2:29093'], api_version=(0, 10, 1))
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        check_event(data)
        if data['event_name'] == 'AccountCreated' and data['event_version'] == 1:
            d = data['data']
            username = d["username"]
            role = d["role"]
            statement = f"insert into users values ('{username}', '{role}')"
            print(statement)
            cur = con.cursor()
            cur.execute(statement)
            con.commit()
        
