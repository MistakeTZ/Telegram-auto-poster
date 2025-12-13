import logging

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# Base model
Base = declarative_base()


# Articles model
class Article(Base):
    __tablename__ = "articles"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    theme = Column(String, nullable=False)
    level = Column(String, nullable=False)
    article_type = Column(String, nullable=False)
    text = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())

    is_posted = Column(Boolean, default=False)
    posted_id = Column(Integer, nullable=True)
    posted_channel = Column(String, nullable=True)
    posted_photo = Column(String, nullable=True)
    posted_time = Column(DateTime(timezone=True), nullable=True)

    links = relationship("Link", back_populates="article")


class Link(Base):
    __tablename__ = "links"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    article_id = Column(ForeignKey("articles.id"), nullable=False)
    link = Column(String, nullable=False)

    article = relationship("Article", back_populates="links")


# Init DB
def init_db(db_path="database/db.sqlite3") -> Session:
    logging.info("Initializing DB...")

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)

    logging.info("DB initialized")
    return session_maker()
