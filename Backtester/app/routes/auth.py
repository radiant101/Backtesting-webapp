from fastapi import APIRouter,Depends,HTTPException,responses,status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserLogin
from ..models import User
from ..utils import verify
router=APIRouter(tags=['Authentication'])

@router.post('/login')
def login(user_credentials:UserLogin,db :Session =Depends(get_db)):

    user=db.query(User).filter(User.email_id==user_credentials.email).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not verify(user_credentials.password,user.password):
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid credential")
    
    #create token
    return {"token" : "example token"}