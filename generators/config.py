import logging
from sys import stdout

from dotenv import load_dotenv

from database.orm import Session, init_db

load_dotenv()

session: Session = init_db()


def setup_logging():
    logging.basicConfig(level=logging.DEBUG, stream=stdout)
