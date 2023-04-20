from fastapi import Request, Form, HTTPException,FastAPI
from SCMXPertLiteDb import collection1
from Models import Sign_Up
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

app= FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="HTMLDirectory/")
@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("SignUp.html",{"request":request})
@app.get("/SignIn",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("SignIn.html",{"request":request})
@app.get("/Dashboard",response_class=HTMLResponse)
def create(request:Request, name:str =Form(...), email:str =Form(...),password:str =Form(...) ,confpassword: str =Form(...)):
    
    ref=collection1.find_one({"email": email})
    if ref:
        raise HTTPException(status_code=400, detail="Email address already used")
    else:
        hashs_password = pwd_context.hash(password)
        collection1.insert_one(dict(Sign_Up(name=name,email=email,password=hashs_password,confpassword=confpassword)))
        return templates.TemplateResponse("SignIn.html",{"request":request})
@app.post("/SignIn",response_class=HTMLResponse,name="SignIn")
def login(request:Request, email:str=Form(...),password:str=Form()):
    ref=collection1.find_one({"email":email})
    if not ref:
        raise HTTPException(status_code=400,detail="This Email id not Existed. Use your registered Email or create one.")
    else:
        name=ref["name"]
        passw=ref["password"]
        if pwd_context.verify(password,passw):
            return templates.TemplateResponse("Dashboard.html",{"request":request,"name":name})
        else:
            raise HTTPException(status_code=400,detail="Your Password is incorrect")
@app.post("/Shipment",response_class=HTMLResponse,name="Shipping")
def shipping(request:Request, ShipNum:int=Form(...), RoutDet:str=Form(...),Device:int=Form(...),PoNumb:int=Form(...),NdcNum:int=Form(...),SeNumOfGoods:int=Form(...),ContNum:int=Form(...),GoodType:str=Form(...),ExpDelDate:str=Form(...),DelNum:int=Form(...),BatchId:int=Form(...),ShipDes:str=Form(...)):
    collection1.inser_one()        