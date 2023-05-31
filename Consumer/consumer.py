from kafka import KafkaConsumer
import json
import pymongo
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

topicName = os.getenv("topicName")
mongouri = os.getenv("mongouri")
from pymongo.errors import ConnectionFailure

mongouri = os.getenv("mongouri")
try:
    client = pymongo.MongoClient(mongouri)
except ConnectionFailure as e:  # Handle the Connection Error
    error_msg = f"Error connecting to the database: {e}"
    print(error_msg)
    raise HTTPException(status_code=500, detail=error_msg)

database = os.getenv("database")
collection = os.getenv("collection")
deviceData = client[database][collection]
bootstrap_servers = os.getenv('bootstrap_servers')

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

except KeyboardInterrupt:
    consumer.close()
