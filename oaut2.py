from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException,status
from database import engine,SessionLocal

from tocken1 import verifytoken
import schemas 
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import model

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(data : str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verifytoken(data,credentials_exception)

async def get_current_active_user(data:str = Depends(oauth2_scheme),db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        id1  = payload.get("id")
        print(id1)
        user = db.query(model.user).filter(model.user.id == id1).first()
        return user
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid password")
    
async def adminlogin(data:str = Depends(oauth2_scheme),db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])
        role  = payload.get("role")
        uid1 = payload.get("uid")
        
        
        if role == "admin":
            user = db.query(model.user).filter(model.user.uid == uid1).first()
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not an admin")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid password")
    
    
    
async def storelogin(data:str = Depends(oauth2_scheme),db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])
        role  = payload.get("role")
        uid1 = payload.get("uid")
        
        
        if role == "store":
            user = db.query(model.user).filter(model.user.uid == uid1).first()
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not the store")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid password")
    
    

    
