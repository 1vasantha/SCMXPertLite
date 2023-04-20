import pymongo
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["SignUpPage"]
collection1=db["SignUp"]
collection2=db["DeviceData"]
collection3=db["Shipment"]
