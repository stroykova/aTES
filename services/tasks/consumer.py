from kafka import KafkaConsumer
from main import con
import time
import json


print('consumer connected')
jobs_done = 0
total_time = 0
while True:
    time.sleep(1)
    consumer = KafkaConsumer('accounts_stream',
                             bootstrap_servers=['kafka:29092', 'kafka2:29093'], api_version=(0, 10, 1))
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        if data['event_name'] == 'AccountCreated':
            d = data['data']
            username = d["username"]
            role = d["role"]
            statement = f"insert into users values ('{username}', '{role}')"
            print(statement)
            cur = con.cursor()
            cur.execute(statement)
            con.commit()
