from pydantic import BaseModel
class Sign_Up(BaseModel):
    name:str
    email:str
    password:str
    confpassword:str
class DeviceData(BaseModel):
    DevId:int
    BatLvl:int
    FstSenTemp:str
    RotFrom:str
    RotTo:str
    TimStmp:str
class Shipment(BaseModel):
    uname:str
    uemail:str
    ShipNum:int
    RoutDet:str
    Device:int
    PoNum:int
    NdcNum:int
    SeNumOfGoods:str
    ContNum:int
    GoodType:str
    ExpDelDate:str
    DelNum:int
    BatchId:int
    ShipDes:str
