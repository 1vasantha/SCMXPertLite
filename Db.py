import pymongo
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["Sign_UP"]
collection=db["SignUp"]
collection2=db["Sign_In"]
collection3=db["Shipment"]
def create(data):
    data=dict(data)
    response=collection.insert_one(data) 
    return str(response.inserted_id )
def all():
    response=collection.find()
    data=[]
    for i in response:
        i["_id"]=str(i["_id"])
        data.append(i)
    return data
def get_one(condition):
    response=collection.find_one({"email":condition})
    response["_id"]=str(response["_id"])
    return response
def update(data):
    data=dict(data)
    response=collection.update_one({"email":data["email"]},{"$set":{"password":data["password"],"name":data["name"]}})
    return response.modified_count
def delete(email):
    response=collection.delete_one({"email":email})
    return response.deleted_count