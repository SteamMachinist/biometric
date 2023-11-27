import random

from PyQt5 import QtWidgets
from main_window_ui import Ui_MainWindow as MainWindowUI
from keyboard_tracking_another import start_tracking, stop_tracking

import string

latin_lower = string.ascii_lowercase
latin_upper = string.ascii_uppercase
cyrillic_lower = ''.join([chr(code) for code in range(1072, 1104)])
cyrillic_upper = ''.join([chr(code) for code in range(1040, 1072)])
digits = string.digits
punctuation = string.punctuation


class MainWindow(QtWidgets.QMainWindow, MainWindowUI):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.lineEditPasswordStrength.setReadOnly(True)
        self.show()
        self.pushButtonGeneratePassword.clicked.connect(self.generate_password)
        self.pushButtonCalculatePasswordStrength.clicked.connect(self.calculate_password_strength)
        self.current_alphabet = ''
        self.current_length = 0
        self.lineEditRegistrationPassword.installEventFilter(self)
        self.pushButtonRegister.clicked.connect(self.stop_tracking)
        self.tracking = False

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

    def start_tracking(self):
        print("Tracking started")
        self.tracking = True
        start_tracking()

    @staticmethod
    def transform(d, s):
        result = []
        ordered = []
        for char in s:
            key = char
            durations = d[key]

            if durations:
                duration = durations.pop(0)  # Remove the first duration from the list
                result.append((key, duration))
                # ordered.append(duration)
        return result

    def stop_tracking(self):
        print("Tracking stopped")
        self.tracking = False
        durations, intervals = stop_tracking()
        print(self.transform(durations, self.lineEditRegistrationPassword.text()))
        print(self.transform(intervals, self.lineEditRegistrationPassword.text()))

    def eventFilter(self, obj, event):
        if obj == self.lineEditRegistrationPassword:
            if event.type() == event.FocusIn:
                self.start_tracking()
            elif event.type() == event.FocusOut and not self.tracking:
                self.stop_tracking()
        return super().eventFilter(obj, event)
