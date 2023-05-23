# packages
from fastapi import Request, Form,FastAPI,Response,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from email.message import EmailMessage
import random
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

#Database and its collections 
import pymongo
from pymongo.errors import ConnectionFailure 
mongouri=os.getenv("mongouri")
try:
    client = pymongo.MongoClient(mongouri)
except ConnectionFailure as e:#Handle the Connection Error
    error_msg = f"Error connecting to the database: {e}"
    print(error_msg)
    raise HTTPException(status_code=500, detail=error_msg)
database=os.getenv("database")
collection1=os.getenv("collection1")
collection2=os.getenv("collection2")
collection3=os.getenv("collection3")
signUp = client[database][collection1]
shipments = client[database][collection2]
deviceData = client[database][collection3]

#Models Designing
from pydantic import BaseModel
class Sign_Up(BaseModel):
    name:str
    email:str
    password:str
    permissions:list[str]
class DeviceData(BaseModel):
    Battery_Level: float
    Device_ID: int
    First_Sensor_temperature: float
    Route_From: str
    Route_To: str
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

# Global Variables
mainOtp=0
mainOtp2=0
session_storage = {}

#mail and password for mail sending
import smtplib
from smtplib import SMTPException
senderemail=os.getenv("senderemail")
senderpassword=os.getenv("senderpassword")

#for password encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#for linking html pages with fastapi
templates = Jinja2Templates(directory="templates")

# Our Main Application with fastapi
app=FastAPI()

secret_key=os.getenv("secret_key")
app.add_middleware(SessionMiddleware, secret_key=secret_key)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    if "text/html" in response.headers.get("content-type", "").lower():
        response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
        response.headers["expires"] = "0"
        response.headers["pragma"] = "no-cache"
    return response

#Get for SignUp page
@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    request.session.clear()
    return templates.TemplateResponse("SignUp.html",{"request":request})

 #Post for SignUp Page       
@app.post("/",response_class=HTMLResponse)
def create(request:Request,response: Response, name:str =Form(...), email:str =Form(...),password:str =Form(...)):
    user=signUp.find_one({"email": email})
    if user:
        return templates.TemplateResponse("SignUp.html",{"request":request,"msg":"Email is already exist"})
    else:
        global mainOtp2
        hashs_password = pwd_context.hash(password)
        otp = str(random.randint(1000, 9999))
        mainOtp2=otp
        msg = EmailMessage()
        msg.set_content(f"Your OTP is: {otp}")
        msg['Subject'] = 'Registering- OTP for SCMXPertLite'
        msg['From'] = senderemail
        msg['To'] = email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(senderemail, senderpassword)
                smtp.send_message(msg)
                return templates.TemplateResponse("SignUpOtp.html",{"request":request,"usname":name,"usemail":email,"uspassword":hashs_password})
        except SMTPException as e:# Handle the SMTP exception
            error_msg = f"Error sending email: {e}"
            raise HTTPException(status_code=500, detail=error_msg)

#Get for SignIn page
@app.get("/SignIn",response_class=HTMLResponse)
def login(request:Request):
        request.session.clear()
        return templates.TemplateResponse("SignIn.html", {"request": request})
    
@app.post("/SignIn",response_class=HTMLResponse,name="SignIn")
def login(request:Request, email:str=Form(...),password:str=Form(...)):
    user=signUp.find_one({"email":email})
    request.session.clear()
    if not user:
        return templates.TemplateResponse("SignIn.html",{"request":request,"detail":"This Email id not Existed. Use your registered Email or create one."})
    else:
        try:
            passw=user['password']
            permissions=user['permissions']
        except KeyError as e:
            error_msg = "Password key not found in user dictionary"
            raise HTTPException(status_code=500, detail=error_msg) from e
        if pwd_context.verify(password,passw):
            request.session["name"] = user["name"]
            request.session["email"]= user["email"]
            request.session["permissions"]=permissions
            request.session["is_authenticated"] = True
            if "maintain" in permissions:
                return templates.TemplateResponse("Dashboard.html", {"request": request, "name": user["name"],"Greet":" You have all your  superior Procurity","url": "/Dashboard"})
            elif  "write" in permissions: 
                return templates.TemplateResponse("Dashboard.html", {"request": request, "name": user["name"],"Greet":" You can have all your admin Ownership","url": "/Dashboard"})
            else:
                return templates.TemplateResponse("Dashboard.html", {"request":request,"name": user["name"]})
        else:
            return templates.TemplateResponse("SignIn.html",{"request":request,"detail":"Your Password is incorrect"})

#Get for Dashboard Page
@app.get("/Dashboard",response_class=HTMLResponse)
def home(request:Request):
    is_authenticated = request.session.get("is_authenticated")
    email= request.session.get("email")
    name=request.session.get("name")
    permissions=request.session.get("permissions")
    if  not is_authenticated or not email:
        return templates.TemplateResponse("SignIn.html", {"request": request,"detail":"You are not authorized.Please login and get authorized"})
    if "maintain" in permissions:
        return templates.TemplateResponse("Dashboard.html", {"request": request, "name": name,"user_type": "superior","Greet":" , You have all your  superior Procurity"})
    elif "write" in permissions:
        return templates.TemplateResponse("Dashboard.html", {"request": request, "name": name,"user_type": "admin","Greet":", You can have all your admin Ownership"})
    else:
        return templates.TemplateResponse("Dashboard.html", {"request": request, "name": name,"Greet":""})
    
#Get for Shipment Creation Page
@app.get("/Shipment",response_class=HTMLResponse)
def shipping(request:Request):
    is_authenticated = request.session.get("is_authenticated")
    email= request.session.get("email")
    name=request.session.get("name")
    permissions=request.session.get("permissions")
    if not is_authenticated or not email:
        return templates.TemplateResponse("SignIn.html", {"request": request,"detail":"You are not authorized.Please login and get authorized"})
    if "maintain" in permissions:
        return templates.TemplateResponse("Shipment.html", {"request": request,"detail":"Hi Superior, You too can place your order"})
    elif "write" in permissions:
        return templates.TemplateResponse("Shipment.html", {"request": request,"detail":"Hey Admin, You can also place the orders"})
    else:
        return templates.TemplateResponse("Shipment.html", {"request": request, "name": name})
   
#Post for Shipment Creation Page        
@app.post("/Shipment",response_class=HTMLResponse,name="Shipping")
def shipping(request:Request, ShipNum:int=Form(...), RoutDet:str=Form(...),Device:int=Form(...),PoNum:int=Form(...),NdcNum:int=Form(...),SeNumOfGoods:int=Form(...),ContNum:int=Form(...),GoodType:str=Form(...),ExpDelDate:str=Form(...),DelNum:int=Form(...),BatchId:int=Form(...),ShipDes:str=Form(...)):
    is_authenticated = request.session.get("is_authenticated")
    email= request.session.get("email")
    name=request.session.get("name")
    if is_authenticated and email:
        shipments.insert_one(dict(Shipment(uname=name,uemail=email,ShipNum=ShipNum,RoutDet=RoutDet,Device=Device,PoNum=PoNum,NdcNum=NdcNum,SeNumOfGoods=SeNumOfGoods,ContNum=ContNum,GoodType=GoodType,ExpDelDate=ExpDelDate,DelNum=DelNum,BatchId=BatchId,ShipDes=ShipDes))) 
        return templates.TemplateResponse("Shipment.html",{"request":request,"detail":"Your order placed successfully. Feel free to place another if u need"}) 
    else:
        return templates.TemplateResponse("Shipment.html",{"request":request,"detail":"you are logged out. So we can't place your order"}) 

#Get for MYAcoount Page
@app.get("/MyAccount", response_class=HTMLResponse)
def account(request: Request):
    is_authenticated = request.session.get("is_authenticated")
    email = request.session.get("email")
    name = request.session.get("name")
    permissions = request.session.get("permissions")
    if not is_authenticated or not email:
        return templates.TemplateResponse("SignIn.html", {"request": request, "detail": "You are not authorized. Please login and get authorized"})
    if "maintain" in permissions:
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        try:
            for user in users:
                if "maintain" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
            return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": name, "email": email, "users": "users", "user_type": "superior"}) 
        except KeyError as e:
            error_msg = "Password key not found in user dictionary"
            raise HTTPException(status_code=500, detail=error_msg) from e
    elif "write" in permissions:
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        try:
            for user in users:
                if "write" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
            return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": name, "email": email, "users": "users", "user_type": "admin"})
        except KeyError as e:
            error_msg = "Password key not found in user dictionary"
            raise HTTPException(status_code=500, detail=error_msg) from e
    else:
        return templates.TemplateResponse("MyAccount.html", {"request": request, "name": name, "email": email})

#Get for Our Shipments Display
@app.get("/MyShipment",response_class=HTMLResponse)
def shipmentDisplay(request:Request):
    is_authenticated = request.session.get("is_authenticated")
    email= request.session.get("email")
    name=request.session.get("name")
    permissions=request.session.get("permissions")
    if not is_authenticated or not email:
        return templates.TemplateResponse("SignIn.html", {"request": request, "detail": "You are not authorized. Please login and get authorized"})
    if "write" in permissions:
        headings=("placed By","from email","Shipment Number","Route Details","Device","Po Number","Ndc Number","Serial Number Of Goods","Container Number","Good Type","Expected Delivery Date","Delivery Number","BatchId","Shipment Description")
        data=[]
        good=shipments.find()
        if shipments.find_one({}) is not None:
            for i in good:
                b=list(i.values())
                c=list(map(str, b))
                c.pop(0)
                d=tuple(c)
                data.append(d)
            return templates.TemplateResponse("MyShipment.html",{"request":request,"headings":headings,"data":tuple(data)})    
        else:
            return templates.TemplateResponse("MyShipment.html",{"request":request,"Shipments":"Oops!No one placed any shipment"})
    else:
                headings=("Shipment Number","Route Details","Device","Po Number","Ndc Number","Serial Number Of Goods","Container Number","Good Type","Expected Delivery Date","Delivery Number","BatchId","Shipment Description")
                data=[]
                a=shipments.find()
                if shipments.find_one({"uemail":email}):
                    for i in a:
                        if i["uemail"]==email:
                            b=list(i.values())
                            c=list(map(str, b))
                            for i in range(3):
                                c.pop(0)
                            d=tuple(c)
                            data.append(d)
                    return templates.TemplateResponse("MyShipment.html",{"request":request,"header":"Your","headings":headings,"data":tuple(data)})
                else:
                    return templates.TemplateResponse("MyShipment.html",{"request":request,"Shipments":"You Have No Shipments As of Now"})

#Get for DeviceData Page
@app.get("/DeviceData",response_class=HTMLResponse)
def DeviceData(request:Request):
    is_authenticated = request.session.get("is_authenticated")
    email= request.session.get("email")
    if is_authenticated and email:
        user=deviceData.find()
        headings=("Battery Level","Device Id","First Sensor Temperature","Route From","Route To")
        data=[]
        for i in user:
            if i==None:
                return templates.TemplateResponse("DeviceData.html",{"request":request,"detail":"No data Found"})
            else:
                b=list(i.values())
                c=list(map(str, b))
                c.pop(0)
                d=tuple(c)
                data.append(d)
        return templates.TemplateResponse("DeviceData.html",{"request":request,"headings":headings,"data":tuple(data)})
    else:
        return templates.TemplateResponse("SignIn.html",{"request":request,"detail":"You are not authorized.Please login and get authorized"})

#Get for EmailChecking for Forgot Password
@app.get("/Emailcheck/ForForgotpass", response_class=HTMLResponse)
def EmailCheck(request: Request):
    return templates.TemplateResponse("EmailCheck.html", {"request": request}) 

#Post for EmailChecking for Forgot Password
@app.post("/Emailcheck/ForForgotpass", response_class=HTMLResponse, name="EmailCheck")
async def EmailCheck(request: Request, email: str = Form(...)):
    global mainOtp
    user =signUp.find_one({"email": email})
    if user:
        otp = str(random.randint(1000, 9999))
        mainOtp=otp
        msg = EmailMessage()
        msg.set_content(f"Your OTP is: {otp}")
        msg['Subject'] = 'Forgot Password - OTP for SCMXPertLite'
        msg['From'] = senderemail
        msg['To'] = email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(senderemail, senderpassword)
                smtp.send_message(msg)
            return templates.TemplateResponse("ForgotPass.html", {"request": request, "message": "Otp has been sent to your mail. Please check and enter", "email": email})
        except SMTPException as e:# Handle the SMTP exception
            error_msg = f"Error sending email: {e}"
            raise HTTPException(status_code=500, detail=error_msg)
    else:
        return templates.TemplateResponse("EmailCheck.html", {"request": request, "detail": "No such email. Please enter your registered email"})

# Get for Forgot Password to reset the password
@app.get("/forgotpass", response_class=HTMLResponse)
def PasswordSetUp(request: Request):
    return templates.TemplateResponse("ForgotPass.html", {"request": request})

# Post for Forgot Password to reset the password
@app.post("/forgotpass", response_class=HTMLResponse, name="ForgotPass")
def PasswordSetUp(request: Request, email: str = Form(...), otp: str = Form(...), password: str = Form(...)):
    user =signUp.find_one({"email": email})
    global mainOtp
    if not user:
        return templates.TemplateResponse("ForgotPass.html", {"request": request, "detail": "No such email. Please enter your registered email"})
    if mainOtp != otp:
        return templates.TemplateResponse("ForgotPass.html", {"request": request, "detail": "You have entered the wrong OTP", "email": email})
    hashs_password = pwd_context.hash(password)
    signUp.update_one({"email": email}, {"$set": {"password":hashs_password}})
    return templates.TemplateResponse("SignIn.html", {"request": request, "message": "Password updated successfully"})

@app.get("/my-form",response_class=HTMLResponse,name="Operations")
def my_form(request:Request):
    is_authenticated = request.session.get("is_authenticated")
    email = request.session.get("email")
    name = request.session.get("name")
    permissions = request.session.get("permissions")
    if not is_authenticated or not email:
        return templates.TemplateResponse("SignIn.html", {"request": request, "detail": "You are not authorized. Please login and get authorized"})
    if "maintain" in permissions:
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        try:
            for user in users:
                if "maintain" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
            return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": name, "email": email, "users": "users", "user_type": "superior"}) 
        except KeyError as e:
            error_msg = "Password key not found in user dictionary"
            raise HTTPException(status_code=500, detail=error_msg) from e
    elif "write" in permissions:
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        try:
            for user in users:
                if "write" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
            return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": name, "email": email, "users": "users", "user_type": "admin"})
        except KeyError as e:
            error_msg = "Password key not found in user dictionary"
            raise HTTPException(status_code=500, detail=error_msg) from e
    else:
        return templates.TemplateResponse("MyAccount.html", {"request": request, "name": name, "email": email})


@app.post("/my-form",response_class=HTMLResponse, name="Operations")
def my_form(request: Request,email:str=Form(...),action:str=Form(...)):
    usemail= request.session.get("email")
    usname=request.session.get("name")
    uspermissions=request.session.get("permissions")
    if action == "makeAdmin":
        permissions = ["read", "write"]
        result = signUp.update_one({"email": email}, {"$set": {"permissions": permissions}})
        if result.modified_count == 1:
            message = "User has been made as an admin successfully"
            color = "green"
        else:
            color = "red"
            message = "This user is already an admin"
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        for user in users:
            if "maintain" not in user["permissions"]:
                data.append((user["name"], user["email"], user["permissions"]))
        return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": usname, "email": usemail, "users": "users", "user_type": "superior","message":message,"color":color})
    elif action == "makeUser":
        permissions=["read"]
        result = signUp.update_one({"email": email}, {"$set": {"permissions": permissions}})
        if result.modified_count == 1:
            message = "Admin has been made as an user successfully"
            color = "green"
        else:
            color = "red"
            message = "This is already an user"
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        for user in users:
            if "maintain" not in user["permissions"]:
                data.append((user["name"], user["email"], user["permissions"]))
        return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": usname, "email": usemail, "users": "users", "user_type": "superior","message":message,"color":color})
    elif action == "deleteUser":
        document = signUp.find_one({"email":email })
        signUp.delete_one(document)
        message= "User deleted successfully."
        color = "green"
        headings = ("Username", "Registered Email", "Permissions")
        users = signUp.find()
        data = []
        for user in users:
            if "maintain" in uspermissions:
                if "maintain" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
            elif "write" in uspermissions:
                if "write" not in user["permissions"]:
                    data.append((user["name"], user["email"], user["permissions"]))
        return templates.TemplateResponse("MyAccount.html", {"request": request, "headings": headings, "data": data, "name": usname, "email": usemail, "users": "users", "user_type": "admin","color":color,"message":message})
    else:
        return templates.TemplateResponse("MyAccount.html", {"request": request,"message": "Invalid action."})

@app.get("/logout",response_class=HTMLResponse)
def logout(request:Request):
    request.session.clear()
    return templates.TemplateResponse("SignIn.html",{"request":request})

@app.get("/SignUpOtp",response_class=HTMLResponse)
def SignUpOtp(request:Request):
    return templates.TemplateResponse("SignUpOtp.html",{"request":request})

@app.post("/SignUpOtp",response_class=HTMLResponse) 
def SignUpOtp(request:Request,usname:str=Form(...),usemail:str=Form(...),uspassword:str=Form(...),otp:str=Form(...)):
    if otp != mainOtp2:
        return templates.TemplateResponse("SignUpOtp.html",{"request":request,"detail":"You have entered a wrong otp, Try to enter the exact otp that you received to ur mail"})
    signUp.insert_one(dict(Sign_Up(name=usname,email=usemail,password=uspassword,permissions=["read"])))
    return templates.TemplateResponse("SignIn.html",{"request":request,"message":"You have registered Successfully. Please login"})