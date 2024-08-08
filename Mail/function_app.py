import azure.functions as func
import logging
import pickle
import smtplib
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

user = {
    'user' : os.environ.get('user'),
    'password': os.environ.get('password')
}

@app.route(route="email_alert")
def email_alert(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python HTTP trigger function processed a request.')
    
    try:

        EmailMessages = pickle.loads(req.get_body())

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(user=user['user'], password=user['password'])

        for EmailMessage in EmailMessages:
            EmailMessage['from'] = user['user']
            server.send_message(EmailMessage)
        server.quit()

        logging.info(f'{len(EmailMessages)} Email/s sent')
        return json.dumps(EmailMessages)
    except Exception as e:
        return e.__str__()
    else:
        pass