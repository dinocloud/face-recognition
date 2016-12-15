from sqlalchemy import *
import datetime
import time

full_engine = None

def configure_database_connection(engine, host, user, password, database):
    global full_engine
    engine_string = '%s://%s:%s@%s/%s' % (engine, user, password, host, database)
    print engine_string
    full_engine = create_engine(engine_string)

def save_movement(type, id_camera):
    timestamp = time.time()
    formatted_timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
    connection = full_engine.connect()
    result = connection.execute("insert into movements (timestamp, type, id_camera) "
                                "values ('{timestamp}','{type}',{id_camera})".format(timestamp=formatted_timestamp,
                                                                                     type=type,
                                                                                     id_camera=str(id_camera)))