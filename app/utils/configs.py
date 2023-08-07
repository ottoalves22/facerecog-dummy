try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import logging
from utils.els_logger import ELSLoggerHandler
import json
import os
from pathlib import Path


data = ConfigParser()
data.read('settings.ini')

#[secret]
secret_key = data.get('secret', 'SECRET_KEY', vars=os.environ)


#[elasticsearch]
els_host = data.get('elasticsearch', 'ELASTICSEARCH_HOST', vars=os.environ)
els_port = data.get('elasticsearch', 'ELASTICSEARCH_PORT', vars=os.environ)
els_user = data.get('elasticsearch', 'ELASTICSEARCH_USERNAME', vars=os.environ)
els_pwd = data.get('elasticsearch', 'ELASTICSEARCH_PASSWORD', vars=os.environ)

#[postgresql]
pg_host = data.get('postgres', 'PG_HOST', vars=os.environ)
pg_port = data.get('postgres', 'PG_PORT', vars=os.environ)
pg_user = data.get('postgres', 'PG_USERNAME', vars=os.environ)
pg_pwd = data.get('postgres', 'PG_PASSWORD', vars=os.environ)
pg_database = data.get('postgres', 'PG_DATABASE', vars=os.environ)

#[smtp]
smtp_host = data.get('smtp', 'SMTP_HOST', vars=os.environ)
smtp_port = data.get('smtp', 'SMTP_PORT', vars=os.environ)
smtp_use_tls = data.get('smtp', 'SMTP_USE_TLS', vars=os.environ)
smtp_user = data.get('smtp', 'SMTP_USER', vars=os.environ)
smtp_pwd = data.get('smtp', 'SMTP_PASSWORD', vars=os.environ)

#[couch]
couch_host = data.get('couchdb', 'COUCHDB_HOST', vars=os.environ)
couch_port = data.get('couchdb', 'COUCHDB_PORT', vars=os.environ)
couch_user = data.get('couchdb', 'COUCHDB_USERNAME', vars=os.environ)
couch_pwd = data.get('couchdb', 'COUCHDB_PASSWORD', vars=os.environ)
couch_database = data.get('couchdb', 'COUCHDB_DATABASE', vars=os.environ)


#[face_config]
distance_threshold = data.get('face_config', 'DISTANCE_THRESHOLD', vars=os.environ)

def get_logger():
    logger = logging.getLogger('alice_auth_api')
    logger.setLevel(logging.DEBUG)

    els_handler = ELSLoggerHandler(els_host, els_port, els_user, els_pwd)
    logger.addHandler(els_handler)
    return logger
