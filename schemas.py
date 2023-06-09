from pydantic import BaseModel
from typing import Union


class User(BaseModel):
    Name:str
    password:str
    email:str
    
    
class User1(BaseModel):
    Name:str
    password:str
    email:str
    role:str
    
    
class login(BaseModel):
    Name:str
    password:str
    
    
class UserInDB(User):
    password: str 
   
   
class Money(BaseModel):
    uid: str
    money: int
    
    
class username(BaseModel):
    name: str
    point:int
    
class username1(BaseModel):
    name: str
    
class productB(BaseModel):
    pid:str
    
    
class product(productB):
    user_id: int
    class Config:
        orm_mode = True 
        
        
class prod(BaseModel):
    pid:list=[]
    uid:str      


class value(BaseModel):
    recycle_value: float
    

class prod1(BaseModel):
    pid:list=[]      
    
class garbage(BaseModel):
    gid:str

    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    name: Union[str, None] = None


class Plot(BaseModel):
    name: str
    points: int
    image: str
    
    
class User6(BaseModel):
    username: str