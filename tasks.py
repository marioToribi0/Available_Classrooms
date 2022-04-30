##CELERY TO TASK asynchronously
import os
from celery import Celery
import smtplib

#ENVIROMENT VARIABLES
from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

EMAIL = environ["USER_CLASSROOMS"]
GMAIL = environ["GMAIL"]
PASSWORD = environ['PASSWORD_CLASSROOMS']

url = os.environ.get("REDIS_URL",'redis://localhost:6379/0')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
celery = Celery("main", broker=url, backend=url)

@celery.task
#Function to send messages
def send_email_message(subject: str,body: str, mail_to_send):
    text = f"Subject: {subject}\nFrom: From Person {EMAIL}\n{body}"
    text = text.encode("UTF-8")
    with smtplib.SMTP("smtp.office365.com", 587, timeout=120) as connection:
                connection.starttls()
                connection.login(user=EMAIL, password=PASSWORD)
                connection.sendmail(from_addr=EMAIL, to_addrs=mail_to_send, 
                                    msg=text)