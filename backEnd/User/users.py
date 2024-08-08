from fastapi import HTTPException,status,Depends, FastAPI, Request
from utils import hash,verify
import databaseFiles.Schemas as Schemas
from sqlalchemy.orm import Session
from sqlalchemy import delete
from databaseFiles.database import get_db, engine
import databaseFiles.models as models
import OAuth
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import Links
from rateLimiter import checkRateLimit

count = 0
while count < 5:
    count += 1
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        continue
    break
else: raise Exception({'Could not connect to the database'})


app = FastAPI(root_path='/users',
              openapi_tags=["Users"])
app.include_router(Links.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/create')
def create_user(user_data:Schemas.create_user, request:Request, db: Session = Depends(get_db)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        existing_users = db.query(models.Users).filter(models.Users.email==user_data.email).first()
        if existing_users:
            return {"success": False,"detail": "email already exists"}
        password = user_data.password
        if len(password) < 7:
            return {"success": False,"detail": "password should atleast be 7 letters long"}
        user_data.password = hash(password)
        new_user = models.Users(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success" :True,"detail": new_user}
    
    except Exception as error:
        return {'Success': False, 'detail': error.__str__()}


@app.post('/login')
def user_login(request:Request, payLoad: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    # if not checkRateLimit(request):
    #     raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        user = db.query(models.Users).filter(models.Users.email == payLoad.username).first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,detail="Invalid Credentials")
        
        if verify(payLoad.password, user.password):

            created_token = OAuth.create_access_token({"user_id": user.id})

            return {"Token":created_token, "token_type":"bearer"}
        
        return {"user not found"}
        
    except Exception as error:
        return {'Success': False, 'detail': error.__str__()}


@app.get("/get")
def get_by_id(request:Request, db: Session = Depends(get_db), get_current_user: int = Depends(OAuth.get_current_user)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        user = db.query(models.Users).where(models.Users.id == get_current_user.id).first()
        return {'name':user.name, 'email':user.email}
        
    except Exception as error:
        return {'Success': False, 'detail': error.__str__()}


@app.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(request:Request, db: Session = Depends(get_db), get_current_user: int = Depends(OAuth.get_current_user)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        LinkToDelete = db.query(models.Users).where(models.Users.id == get_current_user.id).first()
        if LinkToDelete:
            db.execute(
                delete(models.Users)
                .where(models.Users.id == get_current_user.id)
            )
            db.commit()
            return {'detail':f'User deleted'}
        else:
            return {'detail':'User not found'}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)