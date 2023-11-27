import random

from PyQt5 import QtWidgets
from main_window_ui import Ui_MainWindow as MainWindowUI
from keyboard_tracking_another import start_tracking, stop_tracking
from database_utils import User, DatabaseUtil

import string

latin_lower = string.ascii_lowercase
latin_upper = string.ascii_uppercase
cyrillic_lower = ''.join([chr(code) for code in range(1072, 1104)])
cyrillic_upper = ''.join([chr(code) for code in range(1040, 1072)])
digits = string.digits
punctuation = string.punctuation


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
                feature_readable.append((key, feature_value))
                feature.append(feature_value)
        return feature_readable, feature

    def stop_tracking_password(self):
        durations, intervals = stop_tracking()
        password = self.lineEditRegistrationPassword.text()
        durations_readable, durations_feature = self.transform(durations, password)
        intervals_readable, intervals_feature = self.transform(intervals, password)
        print(durations_readable)
        print(intervals_readable)
        self.register_user(durations_feature, intervals_feature)

    def register_user(self, durations_feature, intervals_feature):
        user = User(username=self.lineEditUsername,
                    password=self.lineEditRegistrationPassword.text(),
                    intervals=', '.join(intervals_feature),
                    durations=', '.join(durations_feature))
        self.database_util.add_user(user)
        self.update_users_table()

    def update_users_table(self):
        users = self.database_util.get_all_users()
        print(users)

    def eventFilter(self, obj, event):
        if obj == self.lineEditRegistrationPassword:
            if event.type() == event.FocusIn:
                self.start_tracking_password()
            elif event.type() == event.FocusOut:
                pass
        return super().eventFilter(obj, event)
