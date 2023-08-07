import logging
import uuid
import datetime
from elasticsearch import Elasticsearch


class ELSLoggerHandler(logging.StreamHandler):
    def __init__(self, host, port, username, password):
        logging.StreamHandler.__init__(self)
        self.connect_to_database(host, port, username, password, 'logs')


    def connect_to_database(self, host, port, username, password, index):
        if username is None or password is None:
            url = f'{host}:{port}'
        else:
            url = f'{username}:{password}@{host}:{port}'

  
        self._es = Elasticsearch(hosts=url)
        self._index = index

    
    def close(self):
        self._es.close()
    

    def write(self, _id, data):
        self._es.index(index=self._index, doc_type='logevent', body=data, id=_id)


    def emit(self, record):
        try:
            data = record.__dict__
            data['@timestamp'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f0+00:00')
            data['level'] = self.get_level(data['levelname'])
            data['messageTemplate'] = data['msg']
            data['message'] = data['msg']
            _id = str(uuid.uuid4())
            self.write(_id, data)
            self.flush()
        except:
            self.handleError(record)
    
    def get_level(self, level):
        if level == 'INFO':
            return 'Information'
        elif level == 'ERROR':
            return 'Error'
        elif level == 'WARN':
            return 'Warning'
        return level
