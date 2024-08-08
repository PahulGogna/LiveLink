from passlib.context import CryptContext
import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def formatUrl(url):
    return url if 'https://' in url else 'https://' + url

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

def hash(password):
    return pwd_context.hash(password)

def verify(input_password, hashed_password):
    return pwd_context.verify(input_password,hashed_password)