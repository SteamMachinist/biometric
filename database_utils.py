import os

from sqlalchemy import create_engine, Column, Integer, String, Sequence, ARRAY, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    password = Column(String(50))
    intervals_min = Column(String)
    intervals_max = Column(String)


class DatabaseUtil:
    def __init__(self):
        self.db_folder = 'database'
        os.makedirs(self.db_folder, exist_ok=True)

        self.db_path = os.path.join(self.db_folder, 'biometric.db')
        self.engine = create_engine(f'sqlite:///{self.db_path}')

        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_user(self, user):
        self.session.add(user)
        self.session.commit()

    def get_all_users(self):
        return self.session.query(User).all()

    def select_by_username(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def select_by_id(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()
