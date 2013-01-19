from django.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_name = 'cah'
database_host = ''
if database_host == '':
    database_host = 'localhost'

engine = create_engine('postgresql://{host}/{db}'.format(
     host=database_host,
    db=database_name))

Session = sessionmaker(bind=engine)
