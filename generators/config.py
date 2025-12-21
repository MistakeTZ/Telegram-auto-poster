import logging
from sys import stdout

from dotenv import load_dotenv

from database.orm import Session, init_db

logging.basicConfig(level=logging.DEBUG, stream=stdout)
load_dotenv()

session: Session = init_db()
