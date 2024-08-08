from databaseFiles.database import get_db, engine
import databaseFiles.models as models
from sqlalchemy import update, select
import threading
import requests
from codes import codes
from email.message import EmailMessage
import pickle
import  os


models.Base.metadata.create_all(bind=engine)


def getStatusCodeData(url) -> dict:
    if 'https://' not in url:
        url = 'https://' + url
    try:
        data = requests.head(url, allow_redirects=True).status_code

        if data >= 400 and data <= 599:
            return {'url':url, 'status_code': data, 'exception':False, 'working':False, 'running': True, 'error': None}
        else:    
            return {'url':url, 'status_code': data, 'exception':False, 'working':True, 'running': True, 'error': None}
    except Exception as error:
        return {'url':url, 'status_code':0, 'exception':True, 'error':error.__str__(), 'working':False, 'running': False}


def getAllRunningUrls():
    with get_db() as db:
        return db.query(models.Link).filter(models.Link.running == True).all()


def HandleLink(link, db):
    Mails = []

    newChecked = getStatusCodeData(link.url)
    if link.status_code != newChecked['status_code']:
        if not newChecked['working']:
            try:
                selectIds = db.execute(
                    select(models.Link.by).where(models.Link.url == link.url)
                    ).all()

                users_emails = db.query(models.Users).where(models.Users.id.in_([i[0] for i in selectIds])).all()
                for user in users_emails:
                    body = f'Your Monitor for the url "{link.url}" returned ' +  str(newChecked['status_code']) + f' {codes[str(newChecked["status_code"])]}. CHECK URGENTLY!!'
                    subject = f'Alert!! {user.name}'
                    msg = EmailMessage()
                    msg.set_content(body)
                    msg['subject'] = subject
                    msg['to'] = user.email
                    Mails.append(msg)
                try:
                    requests.post(os.environ.get('mcl'), data=pickle.dumps(Mails))
                except:
                    pass

            except Exception as e:
                print('Error sending mails! ', e)
                return 'Error sending emails' + e.__str__()

        try:
            db.execute(
                update(models.Link).where(models.Link.url == link.url).values(**newChecked)
                    )
        except Exception as e:
            return e.__str__()


def HandleLinks(data, db):
    threads = [threading.Thread(target=HandleLink, args=(data[linkURL], db)) for linkURL in data]
    for thread in threads:
        thread.start()

    for t in threads:
        t.join()


def main():
    try:
        data = getAllRunningUrls()
        HMData = {link.url:link for link in data} # this removes the duplicates
        with get_db() as db:
            HandleLinks(HMData, db)
            
            db.commit()
        return {'detail':'Executed'}
    except Exception as error:
        return {'detail': error.__str__()}