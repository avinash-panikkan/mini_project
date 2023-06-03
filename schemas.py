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
   
class Points(BaseModel):
    uid: str
    points: int
    
    
     
class productB(BaseModel):
    pid:str
    
class product(productB):
    user_id: int
    class Config:
        orm_mode = True 
        
        
class prod(BaseModel):
    pid:str      

    


class garbage(BaseModel):
    gid:str

    
class Token(BaseModel):
    access_token: str
    token_type: str


# class TokenData(BaseModel):
#     name: str | None = None

class TokenData(BaseModel):
    name: Union[str, None] = None

    