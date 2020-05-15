from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from settings import *

engine = create_engine(DATABASE_URI)
db = scoped_session(sessionmaker(bind=engine))


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
    client_id = Column(
        Integer, ForeignKey("clients.id"), nullable=False
    )


if __name__ == "__main__":
    pass
