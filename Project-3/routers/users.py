from typing import Annotated
from starlette import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from models import Users
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PasswordRequest(BaseModel):
    password: str
    new_password: str

class PhoneNumber(BaseModel):
    phone_number: str


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.post('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password_request: PasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail='Current Password Invalid')
    user_model.hashed_password = bcrypt_context.hash(password_request.new_password)

    db.add(user_model)
    db.commit()


@router.put('/update-phone-number', status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency, phone_number_request: PhoneNumber):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number_request.phone_number

    db.add(user_model)
    db.commit()




