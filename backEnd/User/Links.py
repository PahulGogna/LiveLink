from fastapi import HTTPException,status,APIRouter,Depends, Request
from utils import getStatusCodeData, formatUrl
import databaseFiles.Schemas as Schemas
from sqlalchemy import update, text, delete, or_, and_
from sqlalchemy.orm import Session
from databaseFiles.database import get_db
import databaseFiles.models as models
import OAuth
from rateLimiter import checkRateLimit

router = APIRouter(
    prefix= "/link",
    tags=["link"]
)

@router.get("/get/all")
def get_all_posts(request:Request, db: Session = Depends(get_db), get_current_user: int = Depends(OAuth.get_current_user)):
    
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    try:
        user_id = get_current_user.id
        posts = db.query(models.Link).filter(models.Link.by == user_id).order_by(models.Link.id).all()
        return posts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={e.__str__()})

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_link(post: Schemas.post, request:Request, db: Session = Depends(get_db), get_current_user: int = Depends(OAuth.get_current_user)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    try:
        posted_by = get_current_user.id

        checkInDb = db.query(models.Link).filter(and_(models.Link.by == posted_by, models.Link.url == formatUrl(post.url))).all()

        if checkInDb != []:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail':'A Monitor Already exists for this url'})

        returnedData = getStatusCodeData(post.url)

        if returnedData['exception']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail':'Enter a valid URL'})
        
        new_post = models.Link(**returnedData, by=posted_by)

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return  {"success":True, "detail": new_post}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__str__())


@router.post("/update/{id}")
def updatePost(id:int, post : Schemas.update_post, request:Request, db: Session = Depends(get_db),
                get_current_user: int = Depends(OAuth.get_current_user)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    posted_by = get_current_user.id
    LinkToBeUpdated = db.query(models.Link).where(and_(models.Link.id == id, models.Link.by == posted_by)).first()
    if LinkToBeUpdated:
        LinkToBeUpdated.running = post.running
        updated_link = models.Link(**LinkToBeUpdated.to_dict())
        db.execute(
            update(models.Link).where(models.Link.id == id).values(**updated_link.to_dict())
        )
        db.commit()
        return {'detail':'Monitor updated successfully'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'monitor was not found'})

@router.delete('/delete/{id}')
def delete_post(id:int,request:Request, db: Session = Depends(get_db),get_current_user: int = Depends(OAuth.get_current_user)):
    if not checkRateLimit(request):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    LinkToDelete = db.query(models.Link).where(and_(models.Link.id == id, models.Link.by == get_current_user.id)).first()
    if LinkToDelete:
        db.execute(
            delete(models.Link)
            .where(models.Link.id == id)
        )
        db.commit()
        return {'detail':f'Monitor for {LinkToDelete.url} was deleted'}

    else:
        print(get_current_user)
        if get_current_user == 1:
            db.execute(
                delete(models.Link)
                .where(models.Link.id == id)
            )
            db.commit()
            return
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)   