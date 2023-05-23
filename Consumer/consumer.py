from kafka import KafkaConsumer
import json
import pymongo
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

topicName=os.getenv("topicName")
mongouri=os.getenv("mongouri")
client = pymongo.MongoClient(mongouri)
database=os.getenv("database")
collection=os.getenv("collection")
deviceData = client[database][collection]
bootstrap_servers=os.getenv('bootstrap_servers')

class DeviceData(BaseModel):
    Battery_Level: float
    Device_ID: int
    First_Sensor_temperature: float
    Route_From: str
    Route_To: str

consumer = KafkaConsumer(topicName,
                         group_id='my-group',
                         api_version=(0, 11, 5),
                         bootstrap_servers=bootstrap_servers)
try:
    for message in consumer:
        data_dict = json.loads(message.value.decode('utf-8'))
        data = DeviceData(**data_dict)
        count = deviceData.count_documents({})
        if count > 20:
            documents_to_keep = deviceData.find().sort("_id", -1).limit(20)
            document_ids_to_keep = [doc['_id'] for doc in documents_to_keep]
            delete_result = deviceData.delete_many({"_id": {"$nin": document_ids_to_keep}})
        print(data)
        deviceData.insert_one(data.dict())
except Exception as e: 
    pass
