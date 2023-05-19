
import json
from pathlib import Path 
from kafka import KafkaConsumer 
from SCMXPertLiteDb import collection4
from Models import DeviceData

bootstrap_servers = ['localhost:9092']
topic_name ="DeviceData" 

try: 
    consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers, auto_offset_reset="earliest") 
    for message in consumer:
        print(message)
        value = message.value.decode('utf-8')
        data_dict = json.loads(value)
        data = DeviceData(**data_dict)
        count = collection4.count_documents({})
        if count > 20:
            documents_to_keep = collection4.find().sort("_id", -1).limit(20)
            document_ids_to_keep = [doc['_id'] for doc in documents_to_keep]
            delete_result = collection4.delete_many({"_id": {"$nin": document_ids_to_keep}})
        collection4.insert_one(data.dict())
except Exception as e: 
    pass





