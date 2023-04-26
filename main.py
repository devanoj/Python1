from typing import Union
from fastapi import FastAPI
import uvicorn

import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm 

import os
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from base64 import urlsafe_b64decode, urlsafe_b64encode


from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(r'C:\Users\devan\PythonFirebaseKey\animalfostering-a4143-firebase-adminsdk-2g5z6-de60aaf28a.json')


firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://animalfostering-a4143-default-rtdb.firebaseio.com/'
})

SCOPES = r'https://mail.google.com/'
our_email = 'devanojose4@gmail.com'
keyJsonFirebase = r"C:\Users\devan\PythonFirebaseKey\credentials.json"

class CBRecommend():
    def __init__(self, df):
        self.df = df
        
    def cosine_sim(self, v1,v2):
       
        num_cols = len(v1) - 1
        dot_prod = np.dot(v1[:num_cols], v2[:num_cols])
        norm_prod = norm(v1[:num_cols]) * norm(v2[:num_cols])
        if norm_prod == 0:
            return 0
        return dot_prod / norm_prod
    
    def recommend(self, name, n_rec): 
      
        inputVec = self.df.loc[name].values
        self.df['sim']= self.df.apply(lambda x: self.cosine_sim(inputVec, x.values), axis=1)

        # returns top animal
        return self.df.nlargest(columns='sim',n=n_rec).to_dict()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/getRecommendation/{name}")
def get_recommendation(name: str):
    # constants
    #PATH = r'C:\Users\devan\Python\output1.json'
    PATH = r'C:\Users\devan\PythonFileCall\JSON\output.json'

    # import data
    df = pd.read_json(PATH)
    
    df.set_index('name', inplace = True)
    
    # ran on a sample as an example
    t = df.copy()
    cbr = CBRecommend(df = t)
    result = cbr.recommend(name=name, n_rec=5)
    return result



@app.get("/getValue")
def read_root1():
    # constants
    PATH = r'C:\Users\devan\Python\output1.json'

    # import data
    df = pd.read_json(PATH)
    
    
    df.set_index('name', inplace = True)
    
    # ran on a sample as an example
    t = df.copy()
    cbr = CBRecommend(df = t)
    #result = cbr.recommend(animal_id = t.index[0], n_rec = 3)
    result = cbr.recommend(name = 'American Bulldog', n_rec = 3)
    return result  


def gmail_authenticate():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)


    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(keyJsonFirebase, SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


service = gmail_authenticate()


def add_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(filename, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(filename, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(filename, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)


def build_message(destination, obj, body, attachments=[]):
    if not attachments: 
        message = MIMEText(body)
        message['to'] = destination
        message['from'] = our_email
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = destination
        message['from'] = our_email
        message['subject'] = obj
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, destination, obj, body, attachments=[]):
    return service.users().messages().send(
      userId="me",
      body=build_message(destination, obj, body, attachments)
    ).execute()


@app.get("/email")
def send_email():
    send_message(service, "devanojose4@gmail.com", "This is a subject", "This is the body of the email")
    return "Sent Email"


@app.get("/send/{gmail}")
def email_send(gmail: str, dogName: str):

    send_message(service, gmail, "RE: Aniaml Fostering", "Hello"
                 + f"\nYou have selected to foster {dogName}"
                 + f"\n\nWe will soon reach out to you"
                 + f"\nRegards"
                 + f"\nAniFost Team")
    return "Sent email to user"
   

@app.get("/EmailShelter/{sheltergmail}")
def email_send(sheltergmail: str, id: str, Dname: str, sT: str, sD: str, eD: str):
    safetyID = db.reference(f'User/{id}/safetyIDfUser')
    s = safetyID.get()
    nameUser = db.reference(f'User/{id}/name')
    uName = nameUser.get()
    email = db.reference(f'User/{id}/email')
    email1 = email.get()

    s = str(s)

    adult1 = db.reference(f'Safety/{s}/adult')
    adult2 = adult1.get()
    garden1 = db.reference(f'Safety/{s}/garden')
    garden2 = garden1.get()
    hrsAlone = db.reference(f'Safety/{s}/hoursAlone')
    hAlone = hrsAlone.get()
    property = db.reference(f'Safety/{s}/property')
    property1 = property.get()
    criminal = db.reference(f'Safety/{s}/criminal')
    criminal1 = criminal.get()
    otherAnimal = db.reference(f'Safety/{s}/otherAnimal')
    otherA1 = otherAnimal.get()

    #Dog Name
    send_message(service, sheltergmail, "RE: User Adopted Animal", f"Hello \nDog {Dname} has been selected to be adopted by {uName}."
                 + f"\n\n\nGeneral Info:"
                 + f"\nNumber of adults: {adult2} \nGarden: {garden2} \nHours Alone: {hAlone} \nCriminal Record: {criminal1} \nOther Animals: {otherA1}" 
                 + f"\nProperty: {property1}"
                 + f"\nIdeal Start Time: {sT}"
                 + f"\nPreferred Start Date: {sD}"
                 + f"\nEnd Date: {eD}"
                 + f"\nEmail if you think this is a good fit: {email1}")
    return "Sent email to shelter"
