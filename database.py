from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///gossip.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import the model I need, otherwise I have to import them before init_db()
    from model import User, Player, Gossip, Friend, Invite
    Base.metadata.bind = engine
    Base.metadata.create_all()
