from database import get_db, engine
import models
from sqlalchemy import update
from rUtils import getStatusCodeData
import threading

models.Base.metadata.create_all(bind=engine)

def getAllRunningUrls():
    with get_db() as db:
        return db.query(models.Link).filter(models.Link.running == True).all()


def HandleLinks(data, db):
    for link in data:
            newChecked = getStatusCodeData(link.url)
            if link.status_code != newChecked['status_code']:
                db.execute(
                    update(models.Link).where(models.Link.id == link.id).values(id=link.id, by = link.by, **newChecked)
                )

def main():
    data = getAllRunningUrls()
    with get_db() as db:
        if len(data) >= 4:
            thread1 = threading.Thread(target=HandleLinks, args=(data[:len(data)//2], db))
            thread2 = threading.Thread(target=HandleLinks, args=(data[len(data)//2:], db))
            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()
        else:
            HandleLinks(data, db)

        db.commit()


if __name__ == "__main__":
    main()