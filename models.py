from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import *

Base = declarative_base()
engine = create_engine(DATABASE_URI)
db = scoped_session(sessionmaker(bind=engine))


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mambu_client_id = Column(String, nullable=False)

    def add_account(self, mambu_acc_id):
        acc = Account(
            mambu_acc_id=mambu_acc_id,
            client_id=self.id,
            secondary_client_id=None,
        )
        db.add(acc)
        db.commit()


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    mambu_acc_id = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    secondary_client_id = Column(Integer, ForeignKey("clients.id"))

    def update_secondary_client_id(self, secondary_client_id):
        self.secondary_client_id = secondary_client_id
        db.commit()


class Database:
    def validate(self, name):
        res = db.query(Client).filter(Client.first_name == name).all()
        if len(res) == 0:
            return False
        else:
            return True

    def get_client_id(self, name):
        return (
            db.query(Client)
            .filter(Client.first_name == name)
            .all()[0]
            .mambu_client_id
        )

    def get_accounts(self, name):
        client = db.query(Client).filter(Client.first_name == name).all()[0]
        res = (
            db.query(Account)
            .filter(
                or_(
                    Account.client_id == client.id,
                    Account.secondary_client_id == client.id,
                )
            )
            .all()
        )
        return res


if __name__ == "__main__":
    pass
