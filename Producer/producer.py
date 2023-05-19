import json 
import socket 
from kafka import KafkaProducer

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(('localhost', 8080))
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    api_version=(0, 11, 5),
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    retries=5
) 

try:
    for i in range(10):
        content = server_socket.recv(1024).decode('utf-8')
        info = json.loads(content)
        data = {
            "Battery_Level": info['Battery_Level'],
            "Device_ID": info['Device_ID'],
            "First_Sensor_temperature": info['First_Sensor_temperature'],
            "Route_From": info['Route_From'],
            "Route_To": info['Route_To']
        }
        producer.send("SCM", value=data)
        print(data)
    producer.flush()
except Exception as e: 
    print(e) 

server_socket.close()
