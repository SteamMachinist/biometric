import random
import os

from PyQt5 import QtWidgets
from main_window_ui import Ui_MainWindow as MainWindowUI
from keyboard_tracking_another import start_tracking, stop_tracking
# from database_utils import User, DatabaseUtil

import string

from sqlalchemy import create_engine, Column, Integer, String, Sequence, ARRAY, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


latin_lower = string.ascii_lowercase
latin_upper = string.ascii_uppercase
cyrillic_lower = ''.join([chr(code) for code in range(1072, 1104)])
cyrillic_upper = ''.join([chr(code) for code in range(1040, 1072)])
digits = string.digits
punctuation = string.punctuation

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    intervals = Column(String)

# Create an in-memory SQLite database
db_folder = 'database'
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, 'biometric.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create the table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

def add_user(user):
    session.add(user)
    session.commit()

def get_all_users():
    return session.query(User).all()


class MainWindow(QtWidgets.QMainWindow, MainWindowUI):
    def __init__(self, database_util):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.database_util = database_util
        self.lineEditPasswordStrength.setReadOnly(True)
        self.show()
        self.pushButtonGeneratePassword.clicked.connect(self.generate_password)
        self.pushButtonCalculatePasswordStrength.clicked.connect(self.calculate_password_strength)
        self.current_alphabet = ''
        self.current_length = 0
        self.lineEditRegistrationPassword.installEventFilter(self)
        self.pushButtonRegister.clicked.connect(self.stop_tracking_password)
        # self.db_folder = 'database'
        # os.makedirs(self.db_folder, exist_ok=True)
        #
        # self.db_path = os.path.join(self.db_folder, 'biometric.db')
        # self.engine = create_engine(f'sqlite:///{self.db_path}')
        #
        # Base.metadata.create_all(self.engine)
        #
        # Session = sessionmaker(bind=self.engine)
        # self.session = Session()

    def generate_password(self):
        length = self.spinBoxPasswordLength.value()
        use_latin_lowercase = self.checkBoxLatinLowercase.isChecked()
        use_latin_uppercase = self.checkBoxLatinUppercase.isChecked()
        use_cyrillic_lowercase = self.checkBoxCyrillicLowercase.isChecked()
        use_cyrillic_uppercase = self.checkBoxCyrillicUppercase.isChecked()
        use_digits = self.checkBoxDigits.isChecked()
        use_punctuation = self.checkBoxPunctuation.isChecked()

        alphabet = ""
        if use_latin_lowercase:
            alphabet += latin_lower
        if use_latin_uppercase:
            alphabet += latin_upper
        if use_cyrillic_lowercase:
            alphabet += cyrillic_lower
        if use_cyrillic_uppercase:
            alphabet += cyrillic_upper
        if use_digits:
            alphabet += digits
        if use_punctuation:
            alphabet += punctuation

        if len(alphabet) == 0:
            return

        self.current_alphabet = alphabet
        self.current_length = length

        password = ''.join(random.choice(alphabet) for _ in range(length))
        self.lineEditPassword.setText(password)

    def calculate_password_strength(self):
        a = len(self.current_alphabet)
        l1 = self.current_length

        if a == 0 or l1 == 0:
            return

        t = self.spinBoxPasswordLifetime.value()
        v = self.spinBoxBruteforceSpeed.value()

        p = (v * t) / (a * l1)
        self.lineEditPasswordStrength.setText(str(p))

    def start_tracking_password(self):
        stop_tracking()
        start_tracking()

    @staticmethod
    def transform(feature_dict, reference_str):
        feature_readable = []
        feature = []
        for char in reference_str:
            key = char
            features_from_dict = feature_dict[key]

            if features_from_dict:
                feature_value = features_from_dict.pop(0)
                # if feature_value > 10.0:
                #     continue
                feature_readable.append((key, feature_value))
                feature.append(feature_value)
        return feature_readable, feature

    def stop_tracking_password(self):
        durations, intervals = stop_tracking()
        password = self.lineEditRegistrationPassword.text()
        # durations_readable, durations_feature = self.transform(durations, password)
        intervals_readable, intervals_feature = self.transform(intervals, password)
        # print(durations_readable)
        print(intervals_readable)
        self.register_user(intervals_feature)

    def register_user(self, intervals_feature):
        user = User(username=self.lineEditUsername.text(),
                    password=self.lineEditRegistrationPassword.text(),
                    intervals=', '.join(str(f) for f in intervals_feature))
        add_user(user)
        # self.update_users_table()

    def update_users_table(self):
        users = get_all_users()
        print(users)

    def eventFilter(self, obj, event):
        if obj == self.lineEditRegistrationPassword:
            if event.type() == event.FocusIn:
                self.start_tracking_password()
            elif event.type() == event.FocusOut:
                pass
        return super().eventFilter(obj, event)
