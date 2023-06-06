
from fastapi import FastAPI,Depends,HTTPException,status
import schemas
from database import engine,SessionLocal
import model
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import pyqrcode
import png
from tocken1 import create_access_token
from sqlalchemy import desc
import uuid
import oaut2
# from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import relationship
# Generate QR code



app = FastAPI()
model.Base.metadata.create_all(engine)

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
    
    db.add(user1)
    db.commit()
    db.refresh(user1) 
    
    return user1
  

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
    user.points=request.point
    
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
async def dispose(request:schemas.prod,current_user: schemas.User= Depends(oaut2.get_current_active_user), db : Session = Depends(get_db)):
    
    # prodid = str(uuid.uuid4())  
    product1 = db.query(model.Product).filter((model.Product.pid == request.pid) & (model.Product.purchased == True) & (model.Product.disposed == False)).first()
    if not product1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    product1.disposed = True 
    db.commit() 
    db.refresh(product1)    
    
    if product1.user_id == current_user.id:
        id1=current_user.id
        user = db.query(model.user).filter(model.user.id == id1).first()
        user.points=user.points+10
        db.commit()
        return "updated 10 points"
    else:
        id1=product1.user_id
        user = db.query(model.user).filter(model.user.id == id1).first() 
        user.points=user.points-10
        id1=current_user.id
        user = db.query(model.user).filter(model.user.id == id1).first()
        user.points=user.points+10
        db.commit()
        return "decrement 10 points"
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
    
    return qr_data


@app.post('/garbage_validation',tags=['garbage'])
async def validatebin(request:schemas.garbage,current_user: schemas.User= Depends(oaut2.get_current_active_user),db : Session = Depends(get_db)):

    garb1 = model.garbage(gid = request.gid)
    if not garb1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid qr code")
    return garb1

 
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

 