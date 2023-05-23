import json 
import socket 
from kafka import KafkaProducer
import os 
from dotenv import load_dotenv
load_dotenv()

PORT = int(os.getenv("PORT"))
SERVER = os.getenv("SERVER")
bootstrap_servers=os.getenv("bootstrap_servers")
topicName=os.getenv("topicName")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((SERVER, PORT))
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    api_version=(0, 11, 5),
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    retries=5
) 

try:
    content = server_socket.recv(1024).decode('utf-8')
    info = json.loads(content)
    data = {
        "Battery_Level": info['Battery_Level'],
        "Device_ID": info['Device_ID'],
        "First_Sensor_temperature": info['First_Sensor_temperature'],
        "Route_From": info['Route_From'],
        "Route_To": info['Route_To']
    }
    producer.send(topicName, value=data)
    print(data)
    
except Exception as e: 
    print(e) 
producer.flush()
server_socket.close()
