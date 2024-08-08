from jose import JWTError, jwt
from datetime import datetime, timedelta
import databaseFiles.Schemas as Schemas
from fastapi import HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer
import os

OAuth_schema = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

        id : str = payload.get("user_id")

        if payload is None:
            raise credentials_exception
        
        token_data = Schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return token_data
    
def get_current_user(token:str = Depends(OAuth_schema)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)