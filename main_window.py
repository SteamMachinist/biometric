import random

from PyQt5 import QtWidgets

from main_window_ui import Ui_MainWindow as MainWindowUI
from keyboard_tracking import start_tracking, stop_tracking
from database_utils import User
import numpy as np

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
        self.lineEditPasswordStrength.setReadOnly(True)
        self.show()

        self.pushButtonGeneratePassword.clicked.connect(self.generate_password)
        self.pushButtonCalculatePasswordStrength.clicked.connect(self.calculate_password_strength)
        self.current_alphabet = ''
        self.current_length = 0

        self.lineEditRegistrationPassword.installEventFilter(self)
        self.lineEditVerificationPassword.installEventFilter(self)

        self.pushButtonRegister.clicked.connect(self.stop_tracking_registration_password)

        self.database_util = database_util
        self.registrationVariants = []

        self.pushButtonReset.clicked.connect(self.reset_registration)
        self.pushButtonVerify.clicked.connect(self.verify)

        self.currentPassword = ''

        self.update_users_table()
        self.tableWidgetUsersList.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

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

    def reset_registration(self):
        self.registrationVariants.clear()
        self.lineEditRegistrationPassword.clear()
        self.currentPassword = ''
        self.textBrowserRegisterLog.append("Сброс")

    @staticmethod
    def start_tracking_password():
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

    def stop_tracking_registration_password(self):
        _, intervals = stop_tracking()
        password = self.lineEditRegistrationPassword.text()
        intervals_readable, intervals_feature = self.transform(intervals, password)
        self.register_user(intervals_feature)

    def stop_tracking_verification_password(self):
        _, intervals = stop_tracking()
        password = self.lineEditVerificationPassword.text()
        intervals_readable, intervals_feature = self.transform(intervals, password)
        return intervals_feature

    def form_min_max_vector(self):
        maxs = np.array(self.registrationVariants).max(axis=0)
        mins = np.array(self.registrationVariants).min(axis=0)
        return mins.tolist(), maxs.tolist()

    def register_user(self, intervals_feature):
        if len(self.registrationVariants) == 0:
            self.currentPassword = self.lineEditRegistrationPassword.text()
        elif self.currentPassword != self.lineEditRegistrationPassword.text():
            self.textBrowserRegisterLog.append("Пароли не совпадают")
            self.reset_registration()

        self.registrationVariants.append(intervals_feature)
        self.textBrowserRegisterLog.append(f"{len(self.registrationVariants)}/5 вариантов:{intervals_feature}")
        if len(self.registrationVariants) == 5:
            mins, maxs = self.form_min_max_vector()
            user = User(password=self.lineEditRegistrationPassword.text(),
                        intervals_min=', '.join(str(f) for f in mins),
                        intervals_max=', '.join(str(f) for f in maxs))
            self.database_util.add_user(user)
            self.textBrowserRegisterLog.append(f"Успешная регистрация, ваш ID: {str(user.id)}")
            self.reset_registration()
            self.update_users_table()

        self.lineEditRegistrationPassword.clear()

    def update_users_table(self):
        self.tableWidgetUsersList.clear()
        users = self.database_util.get_all_users()
        rows = len(users)
        columns = 2
        self.tableWidgetUsersList.setRowCount(rows)
        self.tableWidgetUsersList.setColumnCount(columns)
        self.tableWidgetUsersList.setHorizontalHeaderLabels(['ID пользователя', 'Пароль'])
        users = [[str(user.id), user.password] for user in users]
        for i in range(rows):
            for j in range(columns):
                self.tableWidgetUsersList.setItem(i, j, QtWidgets.QTableWidgetItem(users[i][j]))
        self.tableWidgetUsersList.setColumnWidth(0, 130)
        self.tableWidgetUsersList.setColumnWidth(1, 100)

    def reset_verification(self):
        self.lineEditVerificationPassword.clear()
        self.lineEditUserID.clear()
        self.textBrowserVerificationLog.append("Сброс")

    def verify(self):
        features = self.stop_tracking_verification_password()
        user_id = self.lineEditUserID.text()
        user = self.database_util.select_by_id(user_id)
        if user is None:
            self.textBrowserVerificationLog.append("Пользователь с таким ID не существует")
            self.reset_verification()
            return
        password = self.lineEditVerificationPassword.text()
        if user.password != password:
            self.textBrowserVerificationLog.append("Неверный пароль")
            self.reset_verification()
            return
        mins = [float(value) for value in user.intervals_min.split(', ')]
        maxs = [float(value) for value in user.intervals_max.split(', ')]
        e = []
        for i in range(len(features)):
            e.append(1 if mins[i] <= features[i] <= maxs[i] else 0)
        if sum(e) / float(len(e)) >= 0.5:
            self.textBrowserVerificationLog.append(f"Успешно авторизован с ID: {user.id}")
        else:
            self.textBrowserVerificationLog.append("Чужой биометрический признак")
        self.reset_verification()



    def eventFilter(self, obj, event):
        if obj == self.lineEditRegistrationPassword:
            if event.type() == event.FocusIn:
                self.start_tracking_password()
            elif event.type() == event.FocusOut:
                pass
        if obj == self.lineEditVerificationPassword:
            if event.type() == event.FocusIn:
                self.start_tracking_password()
            elif event.type() == event.FocusOut:
                pass
        return super().eventFilter(obj, event)
