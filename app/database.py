from typing import Dict

from sqlalchemy import ForeignKey, create_engine, Column, select, update, exc
from sqlalchemy.sql import func
from sqlalchemy.types import *
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import couchdb


import utils.configs as configs


db_string = f'postgresql://{configs.pg_user}:{configs.pg_pwd}@{configs.pg_host}:{str(configs.pg_port)}/{configs.pg_database}'

engine = create_engine(db_string)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


base = declarative_base()

class Faceuser(base):
    __tablename__ = 'faceuser'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    email = Column('email', String(128))
    full_name = Column('only_adj', String(256))
    cpfcnpj = Column('cpfcnpj', String(128))
    external_code = Column('external_code', String(128))
    features = Column('features', JSON)
    submited_by = Column('submited_by', String(128))
    app_context = Column('context', String(128))
    created_at = Column('created_at', TIMESTAMP, server_default=func.now())
    updated_at = Column('updated_at', DateTime, onupdate=func.current_timestamp())


    def __init__(self, email, full_name, cpfcnpj, external_code, features, submited_by, app_context):
        self.email = email
        self.full_name = full_name
        self.cpfcnpj = cpfcnpj
        self.external_code = external_code
        self.features = features
        self.submited_by = submited_by
        self.app_context = app_context


class TwoFactorAuth(base):
    __tablename__ = 'face_2fa'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, ForeignKey('faceuser.id'))
    code = Column('code', String(128))
    submited_by = Column('submited_by', String(128))
    app_context = Column('context', String(128))
    created_at = Column('created_at', TIMESTAMP, server_default=func.now())
    updated_at = Column('updated_at', DateTime, onupdate=func.current_timestamp())


    def __init__(self, user_id, code, submited_by, app_context):
        self.user_id = user_id
        self.code = code
        self.submited_by = submited_by
        self.app_context = app_context


base.metadata.create_all(bind=engine)


def run_qry(statement, _type: str = 'all'):
    try:
        engine = create_engine(db_string, connect_args={'connect_timeout': 5})
        with Session(engine) as session:
            if _type == 'all':
                return session.execute(statement).scalars().all()
            
            return session.execute(statement).scalars().one()
    except exc.NoResultFound as e:
        return None


def get_all():
    statement = select(Faceuser)
    return run_qry(statement=statement)


def get_one(id: int):
    statement = select(Faceuser).filter_by(id=id)
    return run_qry(statement=statement, _type='one')


def get_by_cpfcnpj(cpfcnpj: str):
    statement = select(Faceuser).filter_by(cpfcnpj=cpfcnpj)
    return run_qry(statement=statement, _type='one')


def get_by_email(email: str):
    statement = select(Faceuser).filter_by(email=email)
    return run_qry(statement=statement, _type='one')


def save(obj: Faceuser):
    try:
        engine = create_engine(db_string)
        with Session(engine) as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
    except Exception as e:
        print(e)
        return None
    

def save_2fa(obj: TwoFactorAuth):
    try:
        engine = create_engine(db_string)
        with Session(engine) as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
    except Exception as e:
        print(e)
        return None


def get_2fa_by_id(id: int):
    statement = select(TwoFactorAuth).filter_by(id=id)
    return run_qry(statement=statement, _type='one')


def filter_by_submitted_by(user: str):
    statement = select(Faceuser).filter_by(submited_by=user)
    return run_qry(statement=statement)


def delete(id: int):
    statement = select(Faceuser).filter_by(id=id)
    obj = run_qry(statement=statement, _type='one')

    try:
        engine = create_engine(db_string)
        with Session(engine) as session:
            session.delete(obj)
            session.commit()
    except:
        return None


def update_features(id: int, features):
    stmt = update(Faceuser).where(Faceuser.id == id).values(features=features)

    Session = sessionmaker(engine)
    try:
        engine = create_engine(db_string)
        with Session(engine) as session:
            session.execute(stmt)
            session.commit()
            return True
    except Exception as e:
        print(e)
        return None


class DocumentDB:
    def __init__(self, host: str, port: str, username: str, password: str, database: str):
        self.couch_server = couchdb.Server(f'http://{username}:{password}@{host}:{port}/')

        try:
            self.db = self.couch_server.create(database)
        except:
            self.db = self.couch_server[database]
    

    def add(self, data: Dict):
        doc_id, doc_rev = self.db.save(data)
        return doc_id, doc_rev


    def add_attachment(self, _id: str, content: bytes, filename: str, content_type: str):
        doc = self.get_by_id(_id)
        return self.db.put_attachment(doc, content, filename, content_type)


    def get_by_id(self, _id: str):
        res = self.db.get(_id)

        if res is not None:
            return dict(res)
        return None
   

    def get_attachment(self, doc_id: str, filename: str):
        return self.db.get_attachment(doc_id, filename)
    

    def update(self, _id: str, data: Dict):
        data['_id'] = _id
        return self.db.save(data)