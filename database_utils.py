import os

from sqlalchemy import create_engine, Column, Integer, String, Sequence, ARRAY, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    intervals = Column(String)
    durations = Column(String)


class DatabaseUtil:
    def __init__(self):
        db_folder = 'database'
        os.makedirs(db_folder, exist_ok=True)

        db_path = os.path.join(db_folder, 'biometric.db')
        engine = create_engine(f'sqlite:///{db_path}')

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_user(self, user):
        print('hello')
        self.session.add(user)
        print('ok')
        self.session.commit()
        print('bye')

    def get_all_users(self):
        return self.session.query(User).all()
