
from fastapi import FastAPI,Depends,HTTPException,status
import schemas
from database import engine,SessionLocal
import model
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import pyqrcode
import png
from tocken1 import create_access_token
from sqlalchemy import desc, func
import uuid 
import oaut2
# from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import math

#image upload
from fastapi import File, UploadFile, Form
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image

from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
model.Base.metadata.create_all(engine)

#static file setup config
app.mount("/static", StaticFiles(directory="static"), name="static")


origins = [
    "http://localhost",
    "http://localhost:8000"
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

PRIVATE_KEY = "9efc7501-bd41-438b-9fe4-53b12456da65"


@app.post('/user',tags=['user'])
async def user(request:schemas.User1,db : Session = Depends(get_db)):
    
    user2 = db.query(model.user).filter(model.user.name == request.Name).first()
    
    if user2:
        return {"error":"already exist"}
    
    
    if request.role == "admin":
        userid = "rubbishrevolutionadmin " + str(uuid.uuid4())
    elif request.role == "store":
        userid = "rubbishrevolutionstore " + str(uuid.uuid4())
    elif request.role == "user":
        userid = "rubbishrevolutionuser " + str(uuid.uuid4())
    else:
        return "Invalid role"
    
    user1 = model.user(name = request.Name,email = request.email,password = request.password,uid =  userid,role =request.role)
    
    
    
    
    response = requests.put('https://api.chatengine.io/users/',
        data={
                "username": request.Name,
                "secret": request.Name,
                "first_name": request.Name,
        },
        headers={ "Private-Key": PRIVATE_KEY }
    ) 
    
    
    
    db.add(user1)
    db.commit()
    db.refresh(user1) 
    
    return {"user":user,"chat":response.json()}
  

@app.get('/user/{id1}',tags=['user'])
async def user(id1:int,db : Session = Depends(get_db),get_current_user : schemas.User = Depends(oaut2.get_current_user)):
    
    user = db.query(model.user).filter(model.user.id == id1).first()
    return user


@app.get('/users',tags=['user'])
async def user(db : Session = Depends(get_db),get_current_user : schemas.User = Depends(oaut2.adminlogin)):
    
    user1 = db.query(model.user).all()
    return user1


@app.get('/qr_gen',tags=['user'])
async def qr(db : Session = Depends(get_db),current_user: schemas.User= Depends(oaut2.get_current_active_user)):
    # user = db.query(model.user).filter(model.user.id == id1).first()
    key = current_user.uid
    code = pyqrcode.create(key)
    qr_data = code.png_as_base64_str(scale=5)
    

    
    return {'qrdata':qr_data}

# @app.put('/pointincrement',tags=['user'],)
# async def user(db : Session = Depends(get_db),current_user: schemas.User= Depends(oaut2.get_current_active_user)):
#     id1=current_user.id
#     user = db.query(model.user).filter(model.user.id == id1).first()
#     user.points=user.points+10
#     db.commit()
#     return "updated 10 points"



@app.put('/adminedit',tags=['user'],)
async def adminedit(request:schemas.username,db : Session = Depends(get_db),current_user: schemas.User= Depends(oaut2.adminlogin)):
    
    id1=current_user.id
    user = db.query(model.user).filter(model.user.name == request.name).first()
    user.points=user.points+request.point
    
    db.commit()
    return "updated users points"




@app.get('/user_leaderboadrd',tags=['user'])
async def user(db : Session = Depends(get_db)):
    
    users = db.query(model.user).order_by(desc(model.user.points)).all()
    return users

#login






@app.post('/login',tags=['authentication'])
def login(request:OAuth2PasswordRequestForm= Depends(),db : Session = Depends(get_db)):
    user = db.query(model.user).filter(model.user.name == request.username).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid credential")
    if (user.password != request.password ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid credential")
    
    access_token = create_access_token(data={"sub": user.name,"id":user.id,"role":user.role,"uid":user.uid})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=None)
async def read_users_me(current_user: schemas.User= Depends(oaut2.get_current_active_user)):
    return current_user
    

 




# route for the product





@app.post('/add_product',tags=['product'])
async def add(request:schemas.prod,current_user: schemas.User= Depends(oaut2.storelogin), db : Session = Depends(get_db)):
    
    # prodid = str(uuid.uuid4())
    user2 = db.query(model.user).filter(model.user.uid == request.uid).first()
    if not user2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    for prod in request.pid:
        product1 = model.Product(pid = prod, purchased=True,user_id=user2.id)
        
        db.add(product1)
        db.commit() 
        db.refresh(product1)   
    return product1


@app.put('/dispose_product', tags=['product'])
async def dispose(request:schemas.prod1,current_user: schemas.User= Depends(oaut2.get_current_active_user), db : Session = Depends(get_db)):
    
    # prodid = str(uuid.uuid4())  
    for prod in request.pid:
        product1 = db.query(model.Product).filter((model.Product.pid == prod) & (model.Product.purchased == True) & (model.Product.disposed == False)).first()
        
        if product1:
            product1.disposed = True 
            db.commit() 
            db.refresh(product1)    
        
            if product1.user_id == current_user.id:
                id1=current_user.id
                user = db.query(model.user).filter(model.user.id == id1).first()
                user.points=user.points+10
                db.commit()
                
            else:
                id1=product1.user_id
                user = db.query(model.user).filter(model.user.id == id1).first() 
                user.points=user.points-10
                id1=current_user.id
                user = db.query(model.user).filter(model.user.id == id1).first()
                user.points=user.points+10
                db.commit()
        
            
    return "updated points"
    # product2 = model.Product(pid = request.pid, purchased=True, user_id= current_user.id)
    
    
    
@app.get('/show_product',tags=['product'])
async def show_product(db : Session = Depends(get_db)):
    product1 = db.query(model.Product).all()
    return product1
    


#garbage can


@app.get('/garbage',tags=['garbage'])
async def getbin(db : Session = Depends(get_db)):
    
    garbageid = "rubbishgarbage " + str(uuid.uuid4())
    garb1 = model.garbage(gid = garbageid)
    
    db.add(garb1)
    db.commit()
    db.refresh(garb1) 
    
    
    key = garbageid
    code = pyqrcode.create(key)
    qr_data = code.png_as_base64_str(scale=5)
    
    return {"qrdata":qr_data}


@app.post('/garbage_validation',tags=['garbage'])
async def validatebin(request:schemas.garbage,current_user: schemas.User= Depends(oaut2.get_current_active_user),db : Session = Depends(get_db)):
    gid1 = request.gid
    garb1 =db.query(model.garbage).filter((model.garbage.gid == gid1)&(model.garbage.used == False)).first()
    if not garb1:
        return {"status":"no"}
    else:
        garb1.used=True
        db.add(garb1)
        db.commit()
        db.refresh(garb1) 
        return {"status":"yes"}
 
  
 #redeem
 
@app.put('/redeem', tags=['product'])
async def redeem(request:schemas.Points, current_user: schemas.User= Depends(oaut2.get_current_active_user), db : Session = Depends(get_db)):
    
    # prodid = str(uuid.uuid4())  
    user_pts = db.query(model.user).filter((model.user.uid == current_user.uid)).first()
    if user_pts.points >= request.points:
        user_pts.points = user_pts.points - request.points
    
    store_pts = db.query(model.user).filter(model.user.uid == request.uid).first()
    if store_pts is not None:
        store_pts.points = store_pts.points + request.points
        
        db.commit() 
        return "Success" 
    else:
        return "Store not found"
    # product2 = model.Product(pid = request.pid, purchased=True, user_id= current_user.id)
    # db.add(product1)
    # db.refresh(product1)    

 # plots


#plots
 
@app.post('/plots', tags=["plots"])
async def addplot(name: str = Form(), points: int = Form(), file: UploadFile = File(),
                  current_user: schemas.User= Depends(oaut2.adminlogin),db : Session = Depends(get_db)):
    
    # Generate a unique filename for the uploaded image
    FILEPATH = "static/plots/"
    filename = file.filename
    extension = filename.split(".")[-1]
    
    if extension not in ["png","jpg","jpeg","webp","heif"]:
        return {
            "status": "error",
            "detail": "File extension not allowed"
        }
    
    token_name = secrets.token_hex(10) + "." + extension  
    generated_name = FILEPATH + token_name
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)
        
    #PILLOW - reduce size
    img = Image.open(generated_name)
    img = img.resize(size= (200, 200))
    img.save(generated_name)
    
    plot1 = model.Plots(name= name, points= points, path= generated_name)
    db.add(plot1)
    db.commit()
    db.refresh(plot1)
    
    return { 
        "name": name,
        "points": points,
        "file_path": generated_name
    }  
    
    
    
    # delete user
    
@app.delete('/userdelete', tags=["delete"]) 
async def delete_user(request:schemas.username1, db : Session = Depends(get_db)):
    # Find the user with the specified user_id
    
    user1 = db.query(model.user).filter(model.user.name == request.name).first()
    if not user1:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user1)
    db.commit()
    return {"message": "User deleted successfully"}
    # User not found
    
    
    
@app.get('/reminder', tags=["reminder"]) 
async def reminder(current_user: schemas.User= Depends(oaut2.get_current_active_user), db : Session = Depends(get_db)):
    
    prod_all = db.query(model.Product).filter((model.Product.user_id == current_user.id) & (model.Product.disposed == False)).all()
    if not prod_all:
        raise HTTPException(status_code=404, detail="No products to dispose")
    
    return prod_all 


#calculate value

@app.put('/calculate_value', tags=["calculate_value"]) 
async def calculate_value(request:schemas.value,current_user: schemas.User= Depends(oaut2.adminlogin), db : Session = Depends(get_db)):
    
    # Calculate the sum of points using SQLAlchemy's func.sum
    total_points = db.query(func.sum(model.user.points)).filter(model.user.points >= 0).scalar()
    if total_points is None:
        total_points = 0
        
    value = math.floor((request.recycle_value)/total_points) 
    
    add_value = model.Value(value4m= value)
    db.add(add_value) 
    db.commit()
    db.refresh(add_value)
    
    limit = db.query(func.avg(model.user.points)).scalar()
    print (limit)
    
    user1 = db.query(model.user).filter(model.user.points >= limit).all()
    for user_info in user1:
        user_info.money = user_info.points * add_value.value4m
        db.commit()
        #should clear the points of those whos money is added
    return {"value": add_value.value4m}  
      
@app.post('/authenticate')
async def authenticate(user: schemas.User6):
    response = requests.put('https://api.chatengine.io/users/',
        data={
            "username": user.username,
            "secret": user.username,
            "first_name": user.username,
        },
        headers={ "Private-Key": PRIVATE_KEY }
    )
    return response.json()      