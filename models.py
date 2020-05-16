from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import *

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mambu_client_id = Column(String, nullable=False)

    def add_account(self, mambu_acc_id):
        acc = Account(mambu_acc_id=mambu_acc_id, client_id=self.id)
        db.add(acc)
        db.commit()


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    mambu_acc_id = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)


class Database:
    def __init__(self):
        engine = create_engine(DATABASE_URI)
        self.db = scoped_session(sessionmaker(bind=engine))

    def validate(self, name):
        res = self.db.query(Client).filter(Client.first_name == name).all()
        if len(res) == 0:
            return False
        else:
            return True


if __name__ == "__main__":
    pass
