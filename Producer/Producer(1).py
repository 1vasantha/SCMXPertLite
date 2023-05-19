import json 
import random
import time
import json
import errno
from kafka import KafkaProducer

bootstrap_servers=['localhost:9092']
topic_name="DeviceData"
producer=KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    retries=5
) 
try:
    for i in range(0, 20):
        route = ['Newyork,USA','Chennai, India','Bengaluru, India','London,UK']
        routefrom = random.choice(route)
        routeto = random.choice(route)
        if routefrom != routeto:
            data = {
                "Battery_Level": round(random.uniform(2.00, 5.00), 2),
                "Device_ID": random.randint(1150, 1158),
                "First_Sensor_temperature": round(random.uniform(10, 40.0), 1),
                "Route_From": routefrom,
                "Route_To": routeto
            }
            producer.send(topic_name, value=data)
            print(data)
            time.sleep(2)
        else:
            continue
except IOError as e:
    if e.errno == errno.EPIPE:
        pass