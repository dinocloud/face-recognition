from sqlalchemy import *
import yaml

with open('config/db.yml', 'r') as file:
    config = yaml.load(file)

db_config = config.get("database")

engine_string = '%s://%s:%s@%s/%s' % (db_config.get("engine"), db_config.get("username"), db_config.get("password"),
                                  db_config.get("server"), db_config.get("database"))
print engine_string

full_engine = create_engine(engine_string)



