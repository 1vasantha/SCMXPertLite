from fastapi import Request, Form,FastAPI
from SCMXPertLiteDb import collection1,collection2,collection3
from Models import Sign_Up,Shipment
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
app= FastAPI()
usname="NA"
usemail="NA"
uShipNum=None
uRoutDet:str
uDevice:int
uPoNum:int
uNdcNum:int
uSeNumOfGoods:int
uContNum:int
uGoodType:str
uExpDelDate:str
uDelNum:int
uBatchId:int
uShipDes:str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="HTMLDirectory/")
@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("SignUp.html",{"request":request})
@app.get("/SignIn",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("SignIn.html",{"request":request})
@app.get("/Shipment",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("Shipment.html",{"request":request})
@app.get("/DeviceData",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("DeviceData.html",{"request":request})
@app.get("/Dashboard",response_class=HTMLResponse)
def home(request:Request):
    global usname
    return templates.TemplateResponse("Dashboard.html",{"request":request,"name":usname})
@app.get("/MyAccount",response_class=HTMLResponse)
def home(request:Request):
    global usname
    global usemail
    return templates.TemplateResponse("MyAccount.html",{"request":request,"name":usname,"email":usemail})
@app.get("/MyShipment",response_class=HTMLResponse)
def home(request:Request):
    global usemail
    global uShipNum
    uShipNum=collection3.find_one({"uemail":usemail})
    headings=("Shipment Number","Route Details","Device","Po Number","Ndc Number","Serial Number Of Goods","Container Number","Good Type","Expected Delivery Date","Delivery Number","BatchId","Shipment Description")
    if(usemail!="NA" and uShipNum!=None):
        data=[]
        a=collection3.find()
        for i in a:
            if i["uname"]==usname:
                b=list(i.values())
                c=list(map(str, b))
                for i in range(3):
                    c.pop(0)
                d=tuple(c)
                data.append(d)
    else:
        return templates.TemplateResponse("MyShipment.html",{"request":request,"Shipments":"You Have No Shipments As of Now"})
    return templates.TemplateResponse("MyShipment.html",{"request":request,"headings":headings,"data":tuple(data)})
@app.post("/",response_class=HTMLResponse)
def create(request:Request, name:str =Form(...), email:str =Form(...),password:str =Form(...) ,confpassword: str =Form(...)):
    ref=collection1.find_one({"email": email})
    if ref:
        return templates.TemplateResponse("SignUp.html",{"request":request,"msg":"Email is already used"})
    else:
        hashs_password = pwd_context.hash(password)
        collection1.insert_one(dict(Sign_Up(name=name,email=email,password=hashs_password,confpassword=confpassword)))
        return templates.TemplateResponse("SignIn.html",{"request":request})
@app.post("/SignIn",response_class=HTMLResponse,name="SignIn")
def login(request:Request, email:str=Form(...),password:str=Form(...)):
    ref=collection1.find_one({"email":email})
    if not ref:
        return templates.TemplateResponse("SignIn.html",{"request":request,"detail":"This Email id not Existed. Use your registered Email or create one."})
    else:
        global usname
        global usemail
        name=ref["name"]
        email=ref["email"]
        passw=ref["password"]
        if pwd_context.verify(password,passw):
            usname=name
            usemail=email
            return templates.TemplateResponse("Dashboard.html",{"request":request,"name":name})
        else:
            return templates.TemplateResponse("SignIn.html",{"request":request,"detail":"Your Password is incorrect"})
@app.post("/Shipment",response_class=HTMLResponse,name="Shipping")
def shipping(request:Request, ShipNum:int=Form(...), RoutDet:str=Form(...),Device:int=Form(...),PoNum:int=Form(...),NdcNum:int=Form(...),SeNumOfGoods:int=Form(...),ContNum:int=Form(...),GoodType:str=Form(...),ExpDelDate:str=Form(...),DelNum:int=Form(...),BatchId:int=Form(...),ShipDes:str=Form(...)):
    global uShipNum;global uRoutDet;global uDevice;global uPoNum;global uNdcNum;global uSeNumOfGoods;global uContNum;global uGoodType;global uExpDelDate;global uDelNum;global uBatchId;global uShipDes
    uShipNum=ShipNum;uRoutDet=RoutDet;uDevice=Device;uPoNum=PoNum;uNdcNum=NdcNum;uSeNumOfGoods=SeNumOfGoods;uContNum=ContNum;uGoodType=GoodType;uExpDelDate=ExpDelDate;uDelNum=DelNum;uBatchId=BatchId;uShipDes=ShipDes
    collection3.insert_one(dict(Shipment(uname=usname,uemail=usemail,ShipNum=ShipNum,RoutDet=RoutDet,Device=Device,PoNum=PoNum,NdcNum=NdcNum,SeNumOfGoods=SeNumOfGoods,ContNum=ContNum,GoodType=GoodType,ExpDelDate=ExpDelDate,DelNum=DelNum,BatchId=BatchId,ShipDes=ShipDes))) 
    return templates.TemplateResponse("Dashboard.html",{"request":request})       
@app.post("/DeviceData",response_class=HTMLResponse,name="Devicedata")
def fetching(request:Request,DeviceId:int=Form(...)):
    ref=collection2.find()
    headings=("Device Id","Battery Level","First Sensor Temperature","Route From","Route To", "Time Stamp")
    data=[]
    for i in ref:
        if i["DevId"]==DeviceId:
            b=list(i.values())
            c=list(map(str, b))
            c.pop(0)
            d=tuple(c)
            data.append(d)
        else:
            return templates.TemplateResponse("DeviceData.html",{"request":request,"detail":"No such device"})
    return templates.TemplateResponse("DeviceData.html",{"request":request,"headings":headings,"data":tuple(data)})