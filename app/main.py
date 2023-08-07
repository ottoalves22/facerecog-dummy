from typing import List
from fastapi import FastAPI, Depends, Form, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.http import HTTPBearer, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

import utils.configs as configs
from services import FacematchService, EmotionService
import models
from token_validation import validate_token

description = """

### Facerecog

Enpower apps with face recognition functionalities.

### User

You can register user with their pictures to be used for authentication later.

### 2FA

Mechanism to verify the user using their email, adding one new layer of security.

### Match

You will be able to compare a new person photo with all the pictures included on this service database.
"""

app = FastAPI(title='LIS Facerecog API', description=description, version='1.0.0', openapi_url='/facerecog/openapi.json', docs_url='/facerecog/docs', redoc_url='/facerecog/redoc')
# app = FastAPI(title='LIS Emotion Recog API', description=description, version='1.0.0', openapi_url='/emotion/openapi.json' , docs_url='/emotion/docs', redoc_url='/emotion/redoc')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/emotion/static", StaticFiles(directory="static"), name="static")

auth = HTTPBearer()


@app.on_event("startup")
async def startup():
    global facematch_svc
    facematch_svc = FacematchService(float(configs.distance_threshold))
    global emotion_svc
    emotion_svc = EmotionService()


async def get_current_user(authorization: HTTPBasicCredentials = Depends(auth)):
    return validate_token(authorization.credentials)

## User endpoints

@app.get('/facerecog/user',
          tags=['face_user'],
          description="Returns all registered users. *Will not return the features array. For that, use get_one*",
          responses={
            200: {
                "description": "Returns  all users information object.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=List[models.UserListOutputModel]
)
async def get_users(current_user: dict = Depends(get_current_user)):
    global facematch_svc
    res = facematch_svc.get_users(current_user)
    return [models.UserListOutputModel(id=u.id, email=u.email, cpfcpnj=u.cpfcnpj, full_name=u.full_name, external_code=u.external_code, num_photos=len(u.features), submited_by=u.submited_by, app_context=u.app_context) for u in res]


@app.get('/facerecog/user/{id}',
          tags=['face_user'],
          description="Returns an user detail.",
          responses={
            200: {
                "description": "Returns  the user information object.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=models.UserOutputModel
)
async def get_one(id: int, current_user: dict = Depends(get_current_user)):
    global facematch_svc
    u = facematch_svc.get_one(id, current_user)
    return models.UserOutputModel(id=u.id, email=u.email, cpfcpnj=u.cpfcnpj, full_name=u.full_name, external_code=u.external_code, features=u.features, num_photos=len(u.features), submited_by=u.submited_by, app_context=u.app_context)


@app.post('/facerecog/user',
          tags=['face_user'],
          description="Creates a new user on the facerecog system.",
          responses={
            200: {
                "description": "Returns  the created user information object.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=models.UserOutputModel
)
async def create_user(email: str = Form(..., description='User email that will be used for 2 factor authentication.'),\
                cpfcnpj: str = Form(None, description="CPF or CNPJ of the user."),\
                full_name: str = Form(..., description="First and last name of the user."),\
                external_code: str = Form(None, description="Some external code to bind this user to another system, like *SAS ID, for example*."),
                photo: UploadFile = File(..., description="File containing user face. *Can only contain one face.*"),\
                current_user: dict = Depends(get_current_user)):
    global facematch_svc
    res = facematch_svc.create_user(email, cpfcnpj, full_name, external_code, photo.filename, photo.file.read(), current_user)
    return models.UserOutputModel(id=res.id, email=res.email, cpfcpnj=res.cpfcnpj, full_name=res.full_name, external_code=res.external_code, features=res.features, num_photos=len(res.features), submited_by=res.submited_by, app_context=res.app_context)


@app.post('/facerecog/user/{id}/photo',
          tags=['face_user'],
          description="Add a new photo to an user.",
          responses={
            200: {
                "description": "Returns  the user information object with the new picture.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=bool
)
async def add_photo_to_user(id: int,
                      photo: UploadFile = File(..., description="File containing user face. *Can only contain one face.*"),
                      current_user: dict = Depends(get_current_user)):
    global facematch_svc
    res = facematch_svc.add_photo_to_user(id, photo.filename, photo.file.read(), photo.content_type, current_user)
    return True


@app.delete('/facerecog/user/{id}/photo',
          tags=['face_user'],
          description="Deletes all users photos. *This action will prevent the user to authenticate.*",
          responses={
            200: {
                "description": "Returns true if deleted with success",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=bool
)
async def delete_user_photos(id: int, current_user: dict = Depends(get_current_user)):
    global facematch_svc
    facematch_svc.delete_user_photos(id, current_user)
    return True


@app.delete('/facerecog/user/{id}',
          tags=['face_user'],
          description="Deletes the user",
          responses={
            200: {
                "description": "Returns true if deleted with success",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=bool
)
async def delete_user(id: int, current_user: dict = Depends(get_current_user)):
    global facematch_svc
    facematch_svc.delete_user(id, current_user)
    return True

## Face match endpoints

@app.post('/facerecog/facematch',
          tags=['match'],
          description="Makes the face match comparing the given photo with all users in database.",
          responses={
            200: {
                "description": "Returns the matched users (plural, because it can find similarity with more than one user).",
            },
            401: {
               "description": "The provided auth token is invalid.",
            },
            404: {
               "description": "User not found.",
            }
          },
          response_model=models.FacematchOutputModel
)
async def face_match(photo: UploadFile = File(..., description="File containing user face. *Can only contain one face.*"),
               force_2fa: bool = Query(False, description='If two factor authentication will be forced even if user is found with high similarity.'),
               current_user: dict = Depends(get_current_user)):
    global facematch_svc
    res = facematch_svc.face_match(photo.filename, photo.file.read(), force_2fa, current_user)

    users_output = [models.FacematchUserOutputModel(user_id=u['user_id'], email=u['email'], cpfcnpj=u['cpfcnpj'], distance=u['distance']) for u in res['users']]
    
    if 'id_2fa' in res:
        return models.FacematchOutputModel(type=res['type'], id_2fa=res['id_2fa'], users=users_output)
    return models.FacematchOutputModel(type=res['type'], users=users_output)


# 2FA endpoints
@app.post('/facerecog/2fa/{user_id}/generate',
          tags=['2fa'],
          description="Generates a new 2fa code and send it to the given user / email.",
          responses={
            200: {
                "description": "Returns the 2fa object (without the code - the code is only sent via email to the user).",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=models.TwoFactorAuthOutputModel
)
async def generate_2fa_code(user_id: int,email: str = Query(..., description='Email to send the code for verification.'),
                      current_user: dict = Depends(get_current_user)):
    global facematch_svc
    res = facematch_svc.send_2FACode(user_id, email, current_user)
    return models.TwoFactorAuthOutputModel(id=res.id, user_id=res.user_id)


# 2FA endpoints
@app.get('/facerecog/2fa/{id_2fa}/validate',
          tags=['2fa'],
          description="Validates a 2fa code.",
          responses={
            200: {
                "description": "Returns true if valid and false if not valid.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            },
            404: {
               "description": "2fa register not found.",
            }
          },
          response_model=bool
)
async def validate_2fa_code(id_2fa: int, code: str = Query(..., description='The validation code.'),
                      current_user: dict = Depends(get_current_user)):
    global facematch_svc
    return facematch_svc.validate_2FACode(id_2fa, code, current_user)

# emotion recognition:
@app.post('/emotion', 
tags=['emotion'], 
description="Process an human face image and retrieves emotion object",
responses={
            200: {
                "description": "Returns the emotion object within aspects.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=models.EmotionRecogOutputModel
)
async def process_emotion(cpfcnpj = Query(None, description="CPF or CNPJ of the user binded with the image."), 
file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    global emotion_svc
    content = await file.read()

    data = emotion_svc.emotion_detect(filename=str(file.filename), content=content, cpfcnpj=cpfcnpj, submited_by=current_user['sub'], app_context=current_user['context'])
    return models.EmotionRecogOutputModel(emotion = data.emotion, cpfcnpj=cpfcnpj)


@app.get('/emotion', 
tags=['emotion'], 
description="Get all processed images",
responses={
            200: {
                "description": "Returns the emotion object within aspects.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=List[models.EmotionRecogOutputModel]
)
async def retrieve_all_emotionrecog(cpfcnpj: str = Query(None, description='filter for specific CPF or CNPJ. *not mandatory*'), current_user: dict = Depends(get_current_user)):
    global emotion_svc

    if cpfcnpj is None:
        results = emotion_svc.get_all()
    else:
        results = emotion_svc.get_by_cpfcnpj(cpfcnpj)

    return [models.EmotionRecogOutputModel(id=res.id, emotion=res.emotion, cpfcnpj=res.cpfcnpj) for res in results]


@app.get('/emotion/{id}', 
tags=['emotion'], 
description="Get one processed images by id",
responses={
            200: {
                "description": "Returns the emotion object within aspects.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            }
          },
          response_model=models.EmotionRecogOutputModel
)
async def retrieve_emotion(id: int, current_user: dict=Depends(get_current_user)):
        global emotion_svc
        res = emotion_svc.get_one(id)
        return models.EmotionRecogOutputModel(
            emotion=res.emotion,
            cpfcnpj=res.cpfcnpj
        )


@app.delete('/emotion/{id}', 
tags=['emotion'], 
description="Delete one processed images by id",
responses={
            200: {
                "description": "Returns the emotion object within aspects.",
            },
            401: {
               "description": "The provided auth token is invalid.",
            },
            404: {
               "description": "Process not found.",
            }
          },
          response_model=models.EmotionRecogOutputModel
)
async def delete_emotion(id: int, current_user: dict = Depends(get_current_user)):
    global emotion_svc
    return emotion_svc.delete_one(id, current_user['sub'])