import socket
from django.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if socket.gethostname() != "domU-12-31-39-06-B1-21":
    database_name = 'cah'
    database_user = 'cah'
    database_password = 'BerryPunch'
    database_host = ''
    if database_host == '':
        database_host = 'localhost'

    engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
        user=database_user,
        password=database_password,
        host=database_host,
        db=database_name))
else:
    database_name = 'cah'
    database_host = ''
    if database_host == '':
        database_host = 'localhost'

    engine = create_engine('postgresql://{host}/{db}'.format(
         host=database_host,
        db=database_name))

Session = sessionmaker(bind=engine)
