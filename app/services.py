import os
from typing import Dict
import uuid
import base64
import random
import string
from fastapi import HTTPException
import numpy as np
import cv2
import face_recognition
import database
import utils.configs as configs
from utils.emails import send_email
import tempfile
from fer import FER
from sqlalchemy import true


class FacematchService:
    def __init__(self, distance_threshold: float):
        self.distance_threshold = distance_threshold


    def get_users(self, current_user):
        return database.filter_by_submitted_by(current_user['sub'])


    def get_one(self, id: int, current_user):
        user = database.get_one(id)

        if user is None:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        if user.submited_by != current_user['sub']:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )

        return user

    def create_user(self, email: str, cpfcnpj: str, full_name: str, external_code: str, photo_name: str, photo: bytes, current_user: Dict):
        
        user_already_exists = database.get_by_email(email)
        if user_already_exists is not None and user_already_exists.submited_by == current_user['sub']:
            raise HTTPException(
            status_code=400,
            detail="Um usuário já foi registrado com este email.",
            )

        if cpfcnpj is not None and database.get_by_cpfcnpj(cpfcnpj) is not None:
            raise HTTPException(
            status_code=400,
            detail="Um usuário CPF/CNPJ já foi cadastrado.",
            )

        features = []
        features.append(self.generate_image_object(photo_name, photo))

        faceuser = database.Faceuser(email=email, full_name=full_name, cpfcnpj=cpfcnpj, external_code=external_code, features=features, submited_by=current_user['sub'], app_context=current_user['context'])
        faceuser = database.save(faceuser)
        return faceuser


    def add_photo_to_user(self, id: int, photo_name: str, photo: bytes, content_type: str, current_user):
        user = database.get_one(id)

        if user is None:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        if user.submited_by != current_user['sub']:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        features = user.features
        feature = self.generate_image_object(photo_name, photo, content_type)
        features.append(feature)

        return database.update_features(id, features)


    def delete_user_photos(self, id: int, current_user):
        user = database.get_one(id)

        if user is None:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        if user.submited_by != current_user['sub']:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )

        database.update_features(id, [])


    def delete_user(self, id: int, current_user):
        user = database.get_one(id)

        if user is None:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        if user.submited_by != current_user['sub']:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )

        database.delete(id)


    def generate_image_object(self, photo_name: str, photo: bytes, content_type: str = None):
        _id = str(uuid.uuid4())
        extension = photo_name.split('.')[-1]

        filepath = f'static/{_id}.{extension}'
        with open(filepath, 'wb') as f:
            f.write(photo)

        encoding = self.encode_image(filepath)

        data = {'filename': photo_name, 'filepath': filepath, 'encoding': encoding}

        doc_db = database.DocumentDB(configs.couch_host, configs.couch_port, configs.couch_user, configs.couch_pwd, configs.couch_database)
        doc_id, _ = doc_db.add(data)

        if content_type is None:
            content_type = f'image/{extension}'
        doc_db.add_attachment(doc_id, photo, f'{doc_id}.{extension}', content_type)

        return data


    def encode_image(self, filepath):
        img = cv2.imread(filepath)
        encoding = face_recognition.face_encodings(img)
        
        if len(encoding) == 0:
            raise HTTPException(
            status_code=400,
            detail="Nenhum rosto detectado.",
            )
        if len(encoding) > 1:
            raise HTTPException(
            status_code=400,
            detail="Mais de um rosto detectado.",
            )

        b64 = base64.b64encode(encoding[0].tobytes()).decode("utf-8", "ignore")

        return b64
    

    def face_match(self, photo_name: str, photo: bytes, force_2fa: bool, current_user: Dict):
        obj = self.generate_image_object(photo_name, photo)
        os.remove(obj['filepath'])

        target_encoding = np.frombuffer(base64.b64decode(obj['encoding']))

        all_users = database.filter_by_submitted_by(current_user['sub'])

        user_mapping = {}
        for user in all_users:
            user_mapping[user.id] = user

        all_encodings = []
        user_sequence = []

        for user in all_users:
            if user.features is not None:
                for f in user.features:
                    all_encodings.append(np.frombuffer(base64.b64decode(f['encoding'])))
                    user_sequence.append(user.id)

        face_distances = face_recognition.face_distance(all_encodings, target_encoding)

        similar_users_id = []
        final_users = []
        distances = []

        for i, face_distance in enumerate(face_distances):
            if face_distance < self.distance_threshold: ## normalmente .6
                user_id = user_sequence[i]
                if user_id not in similar_users_id:
                    similar_users_id.append(user_id)
                    final_users.append(user_mapping[user_id])
                    distances.append(face_distance)

        if len(final_users) == 0:
            raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
            )
        
        if len(final_users) == 1:
            final_users = [{'user_id': u.id, 'email': u.email, 'cpfcnpj': u.cpfcnpj, 'distance': distances[i]} for (i, u) in enumerate(final_users)]
            if force_2fa == True or distances[0] > self.distance_threshold - 0.1:
                twofactorobj = self.send_2FACode(final_users[0]['user_id'], final_users[0]['email'], current_user)

                if twofactorobj is not None:
                    return {'type': 'needs_2fa', 'id_2fa': twofactorobj.id, 'users': final_users}
                else:
                    raise HTTPException(
                    status_code=400,
                    detail="Não foi possível gerar o código de autenticação 2 fatores. Tente novamente.",
                    )
            else:
                return {'type': 'ok', 'users': final_users}
        else:
            final_users = [{'user_id': u.id, 'email': self.mask_email(u.email), 'cpfcnpj': u.cpfcnpj, 'distance': distances[i]} for (i, u) in enumerate(final_users)]
            return {'type': 'more_than_one', 'users': final_users}
    

    def send_2FACode(self, user_id: int, email: str, current_user: Dict):
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6)).upper()

        twofactorauth_obj = database.TwoFactorAuth(user_id=user_id, code=code, submited_by=current_user['sub'], app_context=current_user['context'])
        twofactorauth_obj = database.save_2fa(twofactorauth_obj)

        placeholders = {
            '__CODE__': code
        }

        email_response = send_email(
            email_recipient=email,
            email_subject='[LIS] Código de acesso',
            placeholders=placeholders
        )

        if email_response == False:
            raise HTTPException(
            status_code=400,
            detail="O email não pode ser enviado para " + str(email),
            )

        return twofactorauth_obj
    

    def validate_2FACode(self, id_2fa: int, code: str, current_user):
        obj = database.get_2fa_by_id(id_2fa)

        if obj is None:
            raise HTTPException(
            status_code=404,
            detail=f"Código {str(code)} não existe.",
            )

        return obj.code == code


    def mask_email(self, email):
        email, domain = email.split('@')[0], email.split('@')[1]
        num_chars = len(email)
        num_randoms = int(num_chars/2)

        for i in range(num_randoms):
            n = random.randint(0,num_chars - 1)
            word = email[n:n+1]
            email = email.replace(word, '*')
        return email + '@' + domain
    


class EmotionService:
    def __init__(self):
        self.detector = FER(mtcnn=True)

    def emotion_detect(self, filename, content, cpfcnpj, submited_by, app_context):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content)
            img = cv2.imread(tmp.name)            

        result = self.detector.detect_emotions(img)

        doc_db = database.DocumentDB(configs.couch_host, configs.couch_port, configs.couch_user, configs.couch_pwd, configs.couch_database)
        doc_id, _ = doc_db.add({'filename': filename})
        doc_db.add_attachment(doc_id, content, f'{doc_id}.jpg', 'image/jpg')

        if len(result) == 0:
            raise Exception('No face detected.')
        if len(result) > 1:
            return Exception('More  than one face detected.')

        # return result[0]['emotions']
        emotion_obj = database.Emotion(doc_id, result[0]['emotions'], cpfcnpj, submited_by, app_context)
        database.save(emotion_obj)
        return emotion_obj

    def get_by_cpfcnpj(self, cpfcnpj: str):
        return database.get_by_cpfcnpj(cpfcnpj)

    def get_all(self):
        return database.get_all()

    def delete_one(self, id: int, sub: str):
        res = database.delete(id, sub)


        if res is not None:
            exp = HTTPException(
                status_code=404,
                detail="Emoção não encontrada.",
            )
            raise exp

        return true
        

    def get_one(self, id: int):
        res = database.get_one(id)

        if res is not None:
            return res

        exp = HTTPException(
            status_code=404,
            detail="Emoção não encontrada.",
        )
        raise exp
