################################################################
################################################################
import os
import re
import sys
import PIL
import json
import time
import uuid
import socket
import random
import hashlib
import asyncio
import sqlite3
import psycopg2
import threading
from PIL import Image
from resources import resources
##################################################################

import datetime
import components
from collections import Counter
###################################################################

import numpy as np
import pandas as pd
import pandas, requests
###################################################################

from PyQt5 import QtWidgets
###################################################################

import asyncio
import telegram
from telethon import TelegramClient
from telegram.ext import Updater, MessageHandler, CommandHandler
###################################################################

from googleapiclient.discovery import build
from TelegramCrawler import TelegramCrawler
from TelegramUpdate import TelegramUpdate
###################################################################

from PyQt5 import uic
from PyQt5.uic import loadUi
from qframelesswindow import FramelessWindow
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QDesktopServices
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer, QThread, pyqtSignal, QFile, QTextStream, QUrlQuery, QEventLoop, QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QToolTip, QWidget, QPushButton, QLineEdit, QTextEdit, QProgressBar, QMessageBox, QFontComboBox, QFileDialog, QLabel, QComboBox, QGraphicsView, QTableView, QHBoxLayout
################################################################

_DEFAULT_PAGE_SIZE = 1000

## --> GLOBALS
counter = 0
max_value = 10

class TelegramCrawlerThread(QThread):
    signal = pyqtSignal(str, str, str, str)
    def __init__(self, selected_pair):
        QThread.__init__(self)
        self.selected_pair = selected_pair

    def run(self):
        self.telegram_crawler = TelegramCrawler()
        self.telegram_crawler.init(self.selected_pair)
        signal, currency, entry, time = self.telegram_crawler.get_result()
        self.signal.emit(signal, currency, entry, time)

# Custom QObject to monitor and emit signals for date, time, and day
class DateTimeMonitor(QObject):
    dateChanged = pyqtSignal(str)
    timeChanged = pyqtSignal(str)
    dayChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def startMonitoring(self):
        while True:
            now = datetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            current_day = now.strftime("%A")

            self.dateChanged.emit(current_date)
            self.timeChanged.emit(current_time)
            self.dayChanged.emit(current_day)

            QTimer.singleShot(1000, QThread.currentThread().quit)
            QThread.currentThread().exec_()

# Custom QThread to handle updating the QLabel text
class LabelUpdaterThread(QThread):
    def __init__(self, label, signal):
        super().__init__()
        self.label = label
        self.signal = signal

    def run(self):
        self.signal.connect(self.updateLabel)
        self.exec_()

    @pyqtSlot(str)
    def updateLabel(self, text):
        self.label.setText(text)

class TelegramUpdateThread(QThread):
    updateReceived = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()

    def set_event_loop(self, loop):
        asyncio.set_event_loop(loop)

    def run(self):
        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        telegram_update = TelegramUpdate()
        telegram_update.init()
        while True:
            messages = telegram_update.get_latest_message()
            self.updateReceived.emit(messages[:4])
            self.sleep(5)

class OptionGenerator(QObject):
    optionChanged = pyqtSignal(str)

    @pyqtSlot()
    def generateOption(self):
        options = ["Buy", "Sell"]
        random_option = random.choice(options)
        self.optionChanged.emit(random_option)

class MyThread(QtCore.QThread):
    update_signal = QtCore.pyqtSignal(str)
    reset_signal = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.counter = None

    def run(self):
        while self.counter > 0:
            hours = self.counter // 3600
            minutes = (self.counter % 3600) // 60
            seconds = self.counter % 60
            display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.update_signal.emit(display_text)
            QtCore.QThread.sleep(1)
            self.counter -= 1

        # emit reset signal when counter reaches 0
        self.reset_signal.emit()

########################################################################
########################################################################
class ApplicationScreen(QDialog):
    def __init__(self):
        super(ApplicationScreen, self).__init__()
        loadUi("components/loaderWidget.ui", self)
        self.lockDownInfo.hide()
        try:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            
            cur = conn.cursor()
            cur.execute("SELECT shut FROM Updates ORDER BY id DESC LIMIT 1")
            lockDown = cur.fetchone()

            # Check if the query returned any result
            if lockDown is None or lockDown[0] is None:
                self.lockDownInfo.hide()
            else:
                self.lockDownInfo.show()
                self.introText.setPlainText(str(lockDown[0]))

            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.about(self, "Notice", "<center><strong><small><center>An Error Occurred</center></small></strong><br> <p><small>Check your Network Connection!!!</small></p></center><br/>")


        ########################################################################
        ########################################################################
        
        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        self.proceedBtn.clicked.connect(self.gotologinscreen)
        ########################################################################
        ########################################################################
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.progress)
        self.timer.start(80)

        self.load.setText(" ")
        QtCore.QTimer.singleShot(2000, lambda: self.load.setText("Loading."))
        QtCore.QTimer.singleShot(3000, lambda: self.load.setText("Loading.."))
        QtCore.QTimer.singleShot(4000, lambda: self.load.setText("Loading..."))
        QtCore.QTimer.singleShot(5000, lambda: self.load.setText("Loading."))
        QtCore.QTimer.singleShot(6000, lambda: self.load.setText("Loading.."))
        QtCore.QTimer.singleShot(8000, lambda: self.load.setText("Loading..."))
        QtCore.QTimer.singleShot(10000, lambda: self.load.setText("Welcome to FX SignalSpot Binary Trader"))
        self.show()

        self.facebookBtn.clicked.connect(self.facebook_browser)
        self.twitterBtn.clicked.connect(self.twitter_browser)
        self.instagramBtn.clicked.connect(self.instagram_browser)
        self.gmailBtn.clicked.connect(self.gmail_browser)

    def facebook_browser(self):
        url = QUrl("https://web.facebook.com/")
        QDesktopServices.openUrl(url)

    def instagram_browser(self):
        url = QUrl("https://www.instagram.com/fxsignalspot/")
        QDesktopServices.openUrl(url)

    def twitter_browser(self):
        url = QUrl("https://twitter.com/fx_signalspot9")
        QDesktopServices.openUrl(url)

    def gmail_browser(self):
        url = QUrl("https://gmail.com/micelwin@gmail.com")
        QDesktopServices.openUrl(url)

    def progress(self):
        global counter
        self.progressBar.setValue(counter)
        if counter > 100:
            self.proceedBtn.show()
        else:
            self.proceedBtn.hide()
        counter += 1

    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

################################################################################################################################################################################################
################################################################################################################################################################################################
class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("components/loginWidget.ui", self)
        self.check_saved_login()
        self.passwordfield.setEchoMode(QLineEdit.Password)
        ########################################################################
        ########################################################################
        
        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        self.signUpBtn.clicked.connect(self.gotosignupScreen)
        self.loginBtnSubmit.clicked.connect(self.loginfunction)
        self.facebookBtn.clicked.connect(self.facebook_browser)
        self.twitterBtn.clicked.connect(self.twitter_browser)
        self.instagramBtn.clicked.connect(self.instagram_browser)
        self.gmailBtn.clicked.connect(self.gmail_browser)

    def facebook_browser(self):
        url = QUrl("https://web.facebook.com/")
        QDesktopServices.openUrl(url)

    def instagram_browser(self):
        url = QUrl("https://www.instagram.com/fxsignalspot/")
        QDesktopServices.openUrl(url)

    def twitter_browser(self):
        url = QUrl("https://twitter.com/fx_signalspot9")
        QDesktopServices.openUrl(url)

    def gmail_browser(self):
        url = QUrl("https://gmail.com/micelwin@gmail.com")
        QDesktopServices.openUrl(url)
        ########################################################################
        ########################################################################
    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.message.setText("Please fill all Fields !!! ")
            return

        try:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            cur = conn.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cur.execute(query, (user,))
            result_pass = cur.fetchone()
            if result_pass:
                result_pass = result_pass[0]
                # hash the input password using sha256
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if hashed_password == result_pass:
                    self.message.setText("Login Successful !!! ")
                    QtCore.QTimer.singleShot(2000, lambda: self.gotomainscreen())
                    if self.remember_me_checkbox.isChecked():
                        data = {"username": user, "password": password}
                        with open("login_details.json", "w") as f:
                            json.dump(data, f)
                    else:
                        try:
                            os.remove("login_details.json")
                        except:
                            pass
                else:
                    self.message.setText("Password or Username incorrect !!! ")
            else:
                self.message.setText("Password or Username incorrect !!! ")
        except Exception as e:
            QMessageBox.about(self, "Notice", "<strong><small><center>An Error Occurred</center></small></strong><br> <p><small></small></p><br/>" + str(e))

    def check_saved_login(self):
        try:
            with open("login_details.json", "r") as f:
                data = json.load(f)
                self.emailfield.setText(data["username"])
                self.passwordfield.setText(data["password"])
                self.remember_me_checkbox.setChecked(True)
        except:
            pass
        
    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotosignupScreen(self):
        signupScreen = SignupScreen()
        widget.addWidget(signupScreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

################################################################################################################################################################################################
################################################################################################################################################################################################
class SignupScreen(QDialog):
    def __init__(self):
        super(SignupScreen, self).__init__()
        loadUi("components/signUpWidget.ui", self)
        self.passwordfield_2.setEchoMode(QLineEdit.Password)
        self.confirmpassword.setEchoMode(QLineEdit.Password)

        ########################################################################
        ########################################################################
        
        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("fonts/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)


        self.goToLogInPage.clicked.connect(self.gotologinscreen)
        self.signUpBtnSubmit.clicked.connect(self.signupfunction)

        self.facebookBtn.clicked.connect(self.facebook_browser)
        self.twitterBtn.clicked.connect(self.twitter_browser)
        self.instagramBtn.clicked.connect(self.instagram_browser)
        self.gmailBtn.clicked.connect(self.gmail_browser)

    def facebook_browser(self):
        url = QUrl("https://web.facebook.com/")
        QDesktopServices.openUrl(url)

    def instagram_browser(self):
        url = QUrl("https://www.instagram.com/fxsignalspot/")
        QDesktopServices.openUrl(url)

    def twitter_browser(self):
        url = QUrl("https://twitter.com/fx_signalspot9")
        QDesktopServices.openUrl(url)

    def gmail_browser(self):
        url = QUrl("https://gmail.com/micelwin@gmail.com")
        QDesktopServices.openUrl(url)
        ########################################################################
        ########################################################################

    def signupfunction(self):
        try:
            name = self.namerfield.text()
            username = self.usernamerfield.text()
            email = self.emailfield_2.text()
            password = self.passwordfield_2.text()
            confirmpassword = self.confirmpassword.text()

            # Check if all fields are filled
            if len(username) == 0 or len(password) == 0 or len(confirmpassword) == 0 or len(name) == 0 or len(email) == 0:
                self.message_2.setText("Please fill all Fields !!! ")

            # Check if passwords match
            elif password!=confirmpassword:
                self.message_2.setText("Password do not match !!! ")

            # Check if email is valid
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                self.message_2.setText("Invalid email address !!! ")

            else:
                conn = psycopg2.connect(
                    host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                    database="fx_signal_spot_forex_database",
                    user="fx_signal_spot_forex_database_user",
                    password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
                )
                cur = conn.cursor()
                password = hashlib.sha256(password.encode()).hexdigest()
                Users = (username, password, name, email)
                cur.execute('INSERT INTO users (username, password, name, email) VALUES(%s,%s,%s,%s)', Users)
                conn.commit()
                self.message_2.setText("<strong><small><center>User Successfully Signed Up, click again to proceed.</center></small></strong>")
                QtCore.QTimer.singleShot(2000, lambda: self.gotomainscreen())
        except Exception as e:
            QMessageBox.about(self, "Notice", "<strong><small><center>An Error Occurred</center></small></strong><br><p><small>Please be sure you are connected to the Internet to use this Service.</small></p><br/><small><p>Check that your Username, Email are different from previous Logged in Details</p></small><br/><small><p>If you tried signup before now, go to the login page and try to login with your signed up details</p></small>")

    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

################################################################################################################################################################################################
################################################################################################################################################################################################
class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        self.trade_screen = TradeScreen(self)
        loadUi("components/mainWidget.ui", self)
        self.telegram_update_thread = TelegramUpdateThread()
        self.telegram_update_thread.updateReceived.connect(self.updateLabels)
        self.telegram_update_thread.start()  # Start the thread

        # Create and start the DateTimeMonitor thread
        self.monitor_thread = QThread()
        self.monitor = DateTimeMonitor()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.startMonitoring)
        self.monitor_thread.start()

        # Create and start the LabelUpdaterThreads for each label
        self.date_updater_thread = LabelUpdaterThread(self.date_label, self.monitor.dateChanged)
        self.time_updater_thread = LabelUpdaterThread(self.time_label, self.monitor.timeChanged)
        self.day_updater_thread = LabelUpdaterThread(self.day_label, self.monitor.dayChanged)
        self.date_updater_thread.start()
        self.time_updater_thread.start()
        self.day_updater_thread.start()
        self.notificationMessage = "The weekend trade would only be active on the weekend days of Saturday and Sunday. Note: The Weekend Trade are as dangerous as the weekly trade, manage your risk and trade well."
        self.notificationMessage_2 = "Your weekend <br> Binary Trader <br> is now <br> available."

        weekendTrades = self.day_label.text()

        if 'Saturday' in weekendTrades:
            self.tradingScreenBtn.setEnabled(True)
            self.signalBtn.setEnabled(False)
            self.wekkendUpdates.show()

            # Append the notification message
            self.wekkendUpdates.setText(self.notificationMessage_2)
            # Append the notification message
            self.notificationBrowser.append(self.notificationMessage)

        elif 'Sunday' in weekendTrades:
            self.tradingScreenBtn.setEnabled(True)
            self.signalBtn.setEnabled(False)
            self.wekkendUpdates.show()

            # Append the notification message
            self.wekkendUpdates.setText(self.notificationMessage_2)
            # Append the notification message
            self.notificationBrowser.append(self.notificationMessage)

        else:
            self.tradingScreenBtn.setEnabled(False)
            self.signalBtn.setEnabled(True)
            self.wekkendUpdates.hide()

        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        self.brokerBtn.clicked.connect(self.gotobrokerScreen)
        self.infoBtn.clicked.connect(self.gotobrokerScreen)
        self.helpBtn.clicked.connect(self.gotobrokerScreen)
        self.youtubeurl.clicked.connect(self.open_browser)
        self.websiteUrl.clicked.connect(self.web_browser)
        ########################################################################
        ########################################################################

        self.signalBtn.clicked.connect(self.gototradeScreen)
        self.tradingScreenBtn.clicked.connect(self.gotosyntheticScreen)
        self.notificationBtn.clicked.connect(self.gotologinscreen)
        self.syntheticTradeBtn.clicked.connect(self.gotosyntheticScreen)

        conn = psycopg2.connect(
            host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
            database="fx_signal_spot_forex_database",
            user="fx_signal_spot_forex_database_user",
            password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
        )
        cur = conn.cursor()
        cur.execute("SELECT content FROM Notifications ORDER BY id DESC LIMIT 1")
        notifying = cur.fetchone()

        if notifying is None or notifying[0] is None:
            self.notificationBrowser.append(self.notificationMessage)
        else:
            self.notificationBrowser.append(str(notifying[0]))

        conn.commit()
        conn.close()

    def closeEvent(self, event):
        # Clean up threads on application exit
        self.monitor_thread.quit()
        self.monitor_thread.wait()
        event.accept()

    def gotosyntheticScreen(self):
        syntheticScreen = SyntheticScreen()
        widget.addWidget(syntheticScreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def updateLabels(self, messages):
        # Update the labels based on the received messages
        # Retrieve the messages from the TelegramUpdateThread
        widgets = [
            (self.signal_widget, self.currency_widget, self.price_widget),
            (self.signal_widget2, self.currency_widget2, self.price_widget2),
            (self.signal_widget3, self.currency_widget3, self.price_widget3),
            (self.signal_widget4, self.currency_widget4, self.price_widget4)
        ]

        for i, message in enumerate(messages):
            if i < len(widgets):
                # Update the labels with the message data
                signal_label, currency_label, price_label = widgets[i]
                signal_label.setText(message.get('Time'))
                currency_label.setText(message.get('Currency'))
                price_label.setText(message.get('Entry'))
            else:
                # Set "Not Available" if there are fewer than 4 messages
                signal_label, currency_label, price_label = widgets[i]
                signal_label.setText("Not Available")
                currency_label.setText("Not Available")
                price_label.setText("Not Available")

    def open_browser(self):
        url = QUrl("https://www.youtube.com/@fxsignalspot/")
        QDesktopServices.openUrl(url)

    def web_browser(self):
        url = QUrl("https://fxsignalspot.com/")
        QDesktopServices.openUrl(url)
    
    def gotobrokerScreen(self):
        brokerscreen = BrokerScreen()
        if self.sender() == self.infoBtn:
            brokerscreen.getInformationScreen()
        elif self.sender() == self.helpBtn:
            brokerscreen.getHelpScreen()
        elif self.sender() == self.brokerBtn:
            brokerscreen.getBrokerScreen()

        widget.addWidget(brokerscreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gototradeScreen(self):
        tradescreen = TradeScreen(self)
        widget.addWidget(tradescreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

################################################################################################################################################################################################
################################################################################################################################################################################################
class TradeScreen(QDialog):
    def __init__(self, parent=None):
        super(TradeScreen, self).__init__(parent)
        loadUi("components/tradeWidget.ui", self)
        self.telegram_crawler = TelegramCrawler()

        # Initialize advert_view to None
        self.youtube_view = None

        ########################################################################
        ########################################################################
        
        self.timerBar_2.hide()
        self.signalBanner.hide()
        self.signalBanner_2.hide()
        self.telegramAction.hide()
        self.trade_infomation = "<strong></center>ENJOY YOUR TRADE</center></strong><br/> Check out our premuim version also <br/> to get the best trading experience."

        ########################################################################
        ########################################################################
        
        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        # Add a button to get the selected trading pair and rate
        self.get_pair_button = self.findChild(QPushButton, "getPairButton")
        self.get_pair_button.clicked.connect(self.runSignal)

        ########################################################################
        ########################################################################
        
        fixedPair = ['EUR/USD', 'AUD/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'USD/CAD', 'NZD/USD', 'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY', 'CHF/JPY', 'EUR/AUD', 'EUR/CAD', 'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/NZD', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF', 'GBP/JPY', 'GBP/NZD', 'NZD/CAD', 'NZD/CHF', 'NZD/JPY', 'XAU/USD']
        self.combo_1 = self.findChild(QComboBox, "comboPair")
        self.trade_pair = fixedPair
        self.trade_pair_list = list(self.trade_pair)
        self.combo_1.addItems(self.trade_pair_list)
        self.combo_1.setCurrentText("EUR/USD")

        comboTimes = ["1 mins", "2 mins", "3 mins", "4 mins", "5 mins", "10 mins", "15 mins", "30 mins"]
        self.combo_2 = self.findChild(QComboBox, "comboTimer")
        self.combo_2.addItems(comboTimes)
        self.combo_2.setCurrentText("1 mins")

        self.combo_2.currentTextChanged.connect(self.combo_selection_changed)
        self.my_thread = MyThread()
        self.my_thread.update_signal.connect(self.update_progress_bar)
        self.my_thread.reset_signal.connect(self.reset)

        self.homeBtn.clicked.connect(self.gotomainscreen)
        self.brokerBtn.clicked.connect(self.gotobrokerScreen)
        self.infoBtn.clicked.connect(self.gotobrokerScreen)
        self.helpBtn.clicked.connect(self.gotobrokerScreen)
        self.notificationBtn.clicked.connect(self.gotologinscreen)
    
    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotobrokerScreen(self):
        brokerscreen = BrokerScreen()
        if self.sender() == self.infoBtn:
            brokerscreen.getInformationScreen()
        elif self.sender() == self.helpBtn:
            brokerscreen.getHelpScreen()
        elif self.sender() == self.brokerBtn:
            brokerscreen.getBrokerScreen()

        widget.addWidget(brokerscreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def delayresult(self):
        self.getPairButton.setEnabled(False)
        self.comboPair.setEnabled(False)
        self.comboTimer.setEnabled(False)
        self.connectingLabel.show()
        self.connectingLabel.setText("Getting signal")
        QtCore.QTimer.singleShot(4000, lambda: self.connectingLabel.setText("Getting signal please wait..."))
        QtCore.QTimer.singleShot(5000, lambda: self.connectingLabel.setText("Getting signal please wait"))
        QtCore.QTimer.singleShot(6000, lambda: self.connectingLabel.setText("Getting signal please wait."))
        QtCore.QTimer.singleShot(7000, lambda: self.connectingLabel.setText("Getting signal please wait.."))
        QtCore.QTimer.singleShot(8000, lambda: self.connectingLabel.setText("Getting signal please wait..."))
        QtCore.QTimer.singleShot(9500, lambda: self.connectingLabel.setText(self.trade_infomation))
     
    def startAds(self):
        if self.youtube_view is None:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            cur = conn.cursor()
            cur.execute("SELECT youtube FROM Links ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()

            if result:
                video_url = result[0]
                youtubeWidget = self.youtubeContainer

                # Clear the previous screen
                if youtubeWidget.layout() is not None:
                    while youtubeWidget.layout().count() > 0:
                        item = youtubeWidget.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)

                # Modify the video URL to include the ads
                modified_video_url = video_url + "?advertising=1"

                self.youtube_view = QWebEngineView()
                self.youtube_view.load(QUrl(modified_video_url))
                youtubeWidget.layout().addWidget(self.youtube_view)

            def play_video():
                self.youtube_view.page().runJavaScript("document.querySelector('video').currentTime = 0; document.querySelector('video').play();")
            self.youtube_view.loadFinished.connect(play_video)
        else:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            cur = conn.cursor()
            cur.execute("SELECT youtube FROM Links ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()

            if result:
                video_url = result[0]

                youtubeWidget = self.youtubeContainer
                if youtubeWidget.layout() is not None:
                    while youtubeWidget.layout().count() > 0:
                        item = youtubeWidget.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)

                # Modify the video URL to include the ads
                modified_video_url = video_url + "?advertising=1"

                self.youtube_view.load(QUrl(modified_video_url))
                youtubeWidget.layout().addWidget(self.youtube_view)

            def play_video():
                self.youtube_view.page().runJavaScript("document.querySelector('video').currentTime = 0; document.querySelector('video').play();")
            self.youtube_view.loadFinished.connect(play_video)

    def get_trading_pairs_from_combo_box(self):
        try:
            self.selected_pair = self.combo_1.currentText()
            selected_pair = self.combo_1.currentText()
            if selected_pair not in self.trade_pair:
                QMessageBox.about(self, "Notice", "<strong><small><center>You either did not select any Trading Pair or your Trading Pair is not found in the list.</center></small></strong>")
            else:
                base_currency = selected_pair.split("/")[0]
                quote_currency = selected_pair.split("/")[1]

                base_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

                # Make a GET request to the API
                response = requests.get(base_url)

                # Check the status code of the response to make sure it was successful
                if response.status_code == 200:
                    # Parse the response data as JSON
                    data = response.json()

                    # Get the exchange rate for the selected pair from the response data
                    rate = data['rates'][quote_currency]

                    # Return the currency pair and exchange rate as a tuple
                    return (selected_pair, rate)
                else:
                    # If the request was not successful, return None
                    return None
        except Exception as e:
            QMessageBox.about(self, "Notice", "<strong><small><center>An Error Occurred</center></small></strong><br> <p><small></small></p><br/>" + str(e))

    def get_selected_pair(self):
        try:
            # Get the selected trading pair and rate
            selected_pair, rate = self.get_trading_pairs_from_combo_box()
            if selected_pair is None:
                QMessageBox.about(self, "Notice", "<strong><small><center>You either did not select any Trading Pair or your Trading Pair is not found in the list.</center></small></strong>")
            else:
                #set to a label
                self.labelPair.setText(selected_pair)
                self.labelPair_1.setText(str(rate))

                # Calculate the signal strength (you can use any method you want to calculate the signal strength)
                signal_strength = rate * 80
                
                signal_strength = random.uniform(0.85, 0.95)
                getPercentage = round(int(signal_strength*100), 3)
                self.strengthBar_5.setText(str(getPercentage) + " %")
        except Exception as e:
            QMessageBox.about(self, "Notice", "<center><strong><small><center>An Error Occurred</center></small></strong><br> <p><small>Check your Network Connection!!!</small></p></center><br/>" + str(e))

    def start_timer_thread(self,counter_value):
        self.my_thread.counter = counter_value
        self.my_thread.start()
    
    def combo_selection_changed(self):
        combo_value = self.combo_2.currentText()
        if combo_value == "1 mins":
            counter_value = 60
        elif combo_value == "2 mins":
            counter_value = 120
        elif combo_value == "3 mins":
            counter_value = 180
        elif combo_value == "4 mins":
            counter_value = 240
        elif combo_value == "5 mins":
            counter_value = 300
        elif combo_value == "10 mins":
            counter_value = 600
        elif combo_value == "15 mins":
            counter_value = 900
        elif combo_value == "30 mins":
            counter_value = 1800
        elif combo_value == "1 hrs":
            counter_value = 3600
        elif combo_value == "2 hrs":
            counter_value = 7200
        elif combo_value == "3 hrs":
            counter_value = 10800
        elif combo_value == "4 hrs":
            counter_value = 14400
        elif combo_value == "5 hrs":
            counter_value = 18000

        self.start_timer_thread(counter_value)

    def update_progress_bar(self, display_text):
        hours, minutes, seconds = map(int, display_text.split(':'))
        total_seconds = 3600*hours + 60*minutes + seconds
        self.timerBar.display(display_text)
        if total_seconds <= 20:
            self.timerBar.hide()
            self.timerBar_2.show()
            self.telegramAction.show()
            self.telegramAction_2.hide()
            self.timerBar_2.display(display_text)
            # Stop the video playback and remove the widget from the layout
            self.youtubeContainer.layout().removeWidget(self.youtube_view)
            self.youtube_view = None
            self.youtubeWidget.setEnabled(False)
            self.premiumAds.show()
        else:
            self.premiumAds.hide()
            self.youtubeWidget.setEnabled(True)
            self.timerBar.show()
            self.timerBar_2.hide()
            self.telegramAction.hide()
            self.telegramAction_2.show()
            self.timerBar.display(display_text)

    def reset(self):
        self.menuContainer.setEnabled(True)
        self.getPairButton.setEnabled(True)
        self.comboPair.setEnabled(True)
        self.comboTimer.setEnabled(True)
        self.signalBanner.hide()
        self.signalBanner_2.hide()
        self.connectingLabel.hide()

    def runSignal(self):
        self.get_selected_pair()
        self.combo_selection_changed()
        self.delayresult()
        self.startAds()
        self.premiumAds.hide()
        self.menuContainer.setEnabled(False)
        selected_pair = self.combo_1.currentText()
        plain_pair = selected_pair
        plain_trade_pair = plain_pair.replace('/', '')
        tc = TelegramCrawler()
        tc.init(plain_trade_pair)
        signal, currency, entry, time = tc.get_result()
        self.telegramAction.setText(signal)
        self.telegramAction_2.setText(signal)
        self.telegramEntry.setText(entry)
        self.telegramCurrency.setText(currency)
        self.telegramTime.setText(time)
        self.signalLabel.setText("Subscribe <br> to our <br> Premuim <br> Version")
        if signal == 'Buy\nCurrency':
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.show())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.hide())
        elif signal == 'Sell\nCurrency':
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.hide())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.show())
        else:
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.hide())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.hide())

class BrokerScreen(QDialog):
    def __init__(self):
        super(BrokerScreen, self).__init__()
        loadUi("components/brokerWidget.ui", self)
        # Get the stacked widget page named telegramContent
        telegramContainer = self.telegramContent
        # Create a WebEngineView widget and set the URL to the Telegram channel
        telegram_view = QWebEngineView()
        telegram_view.setUrl(QUrl("https://t.me/fxsignalspot"))
        # Add the WebEngineView widget to the layout of the page widget
        telegramContainer.layout().addWidget(telegram_view)

        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        self.homeBtn.clicked.connect(self.gotomainscreen)
        self.signalBtn.clicked.connect(self.gototradeScreen)
        self.brokerBtn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.brokerPage))
        self.infoBtn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.infoPage))
        self.helpBtn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.helpPage))
        self.notificationBtn.clicked.connect(self.gotologinscreen)
    
    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gototradeScreen(self):
        tradescreen = TradeScreen(self)
        widget.addWidget(tradescreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def getInformationScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.infoScreen)

    def getHelpScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.helpScreen)

    def getBrokerScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.helpScreen)

class SyntheticScreen(QDialog):
    def __init__(self):
        super(SyntheticScreen, self).__init__()
        loadUi("components/syntheticWidget.ui", self)
        
        # Create the OptionGenerator object
        self.option_generator = OptionGenerator()
        
        # Connect the optionChanged signal to updateLabel slot
        self.option_generator.optionChanged.connect(self.updateLabel)

        # Initialize advert_view to None
        self.youtube_view = None

        ########################################################################
        ########################################################################
        
        self.timerBar_2.hide()
        self.signalBanner.hide()
        self.signalBanner_2.hide()
        self.telegramAction.hide()
        self.trade_infomation = "<strong></center>ENJOY YOUR TRADE</center></strong><br/> Check out our premuim version also <br/> to get the best trading experience."

        ########################################################################
        ########################################################################
        
        # Step 1: Download the font file and store it in the project directory
        font_file = QFile("font/WorkSans-Medium.ttf")
        font_file.open(QFile.ReadOnly)
        # Step 2: Create a QFont object and set its properties
        font_id = QFontDatabase.addApplicationFontFromData(font_file.readAll())
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_name)
        for widget in app.allWidgets():
            widget.setFont(font)

        # Add a button to get the selected trading pair and rate
        self.get_pair_button = self.findChild(QPushButton, "getPairButton")
        self.get_pair_button.clicked.connect(self.runSignal)

        ########################################################################
        ########################################################################
        
        fixedPair = ['EUR/USD', 'AUD/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'USD/CAD', 'NZD/USD', 'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY', 'CHF/JPY', 'EUR/AUD', 'EUR/CAD', 'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/NZD', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF', 'GBP/JPY', 'GBP/NZD', 'NZD/CAD', 'NZD/CHF', 'NZD/JPY', 'XAU/USD']
        self.combo_1 = self.findChild(QComboBox, "comboPair")
        self.trade_pair = fixedPair
        self.trade_pair_list = list(self.trade_pair)
        self.combo_1.addItems(self.trade_pair_list)
        self.combo_1.setCurrentText("EUR/USD")

        comboTimes = ["1 mins", "2 mins", "3 mins", "4 mins", "5 mins", "10 mins", "15 mins", "30 mins"]
        self.combo_2 = self.findChild(QComboBox, "comboTimer")
        self.combo_2.addItems(comboTimes)
        self.combo_2.setCurrentText("1 mins")

        self.combo_2.currentTextChanged.connect(self.combo_selection_changed)
        self.my_thread = MyThread()
        self.my_thread.update_signal.connect(self.update_progress_bar)
        self.my_thread.reset_signal.connect(self.reset)

        self.homeBtn.clicked.connect(self.gotomainscreen)
        self.brokerBtn.clicked.connect(self.gotobrokerScreen)
        self.infoBtn.clicked.connect(self.gotobrokerScreen)
        self.helpBtn.clicked.connect(self.gotobrokerScreen)
        self.notificationBtn.clicked.connect(self.gotologinscreen)

    def gotologinscreen(self):
        loginscreen = LoginScreen()
        widget.addWidget(loginscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gototradeScreen(self):
        tradescreen = TradeScreen(self)
        widget.addWidget(tradescreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def getInformationScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.infoScreen)

    def getHelpScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.helpScreen)

    def getBrokerScreen(self):
        # Get the stacked widget
        stacked_widget = self.stackedWidget
        # Set the current widget to settingScreen
        stacked_widget.setCurrentWidget(self.helpScreen)

    def gotobrokerScreen(self):
        brokerscreen = BrokerScreen()
        if self.sender() == self.infoBtn:
            brokerscreen.getInformationScreen()
        elif self.sender() == self.helpBtn:
            brokerscreen.getHelpScreen()
        elif self.sender() == self.brokerBtn:
            brokerscreen.getBrokerScreen()

    def delayresult(self):
        self.getPairButton.setEnabled(False)
        self.comboPair.setEnabled(False)
        self.comboTimer.setEnabled(False)
        self.connectingLabel.show()
        self.connectingLabel.setText("Getting signal")
        QtCore.QTimer.singleShot(4000, lambda: self.connectingLabel.setText("Getting signal please wait..."))
        QtCore.QTimer.singleShot(5000, lambda: self.connectingLabel.setText("Getting signal please wait"))
        QtCore.QTimer.singleShot(6000, lambda: self.connectingLabel.setText("Getting signal please wait."))
        QtCore.QTimer.singleShot(7000, lambda: self.connectingLabel.setText("Getting signal please wait.."))
        QtCore.QTimer.singleShot(8000, lambda: self.connectingLabel.setText("Getting signal please wait..."))
        QtCore.QTimer.singleShot(9500, lambda: self.connectingLabel.setText(self.trade_infomation))

    def startAds(self):
        self.youtubeContainer.setEnabled(False)
        if self.youtube_view is None:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            cur = conn.cursor()
            cur.execute("SELECT youtube FROM Links ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()

            if result:
                video_url = result[0]
                youtubeWidget = self.youtubeContainer

                # Clear the previous screen
                if youtubeWidget.layout() is not None:
                    while youtubeWidget.layout().count() > 0:
                        item = youtubeWidget.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)

                # Modify the video URL to include the ads
                modified_video_url = video_url + "?advertising=1"

                self.youtube_view = QWebEngineView()
                self.youtube_view.load(QUrl(modified_video_url))
                youtubeWidget.layout().addWidget(self.youtube_view)

            def play_video():
                self.youtube_view.page().runJavaScript("document.querySelector('video').currentTime = 0; document.querySelector('video').play();")
            self.youtube_view.loadFinished.connect(play_video)
        else:
            conn = psycopg2.connect(
                host="dpg-ch6j1fg2qv26p18mdph0-a.oregon-postgres.render.com",
                database="fx_signal_spot_forex_database",
                user="fx_signal_spot_forex_database_user",
                password="OtnJCQXdTOUYvHFGylOa6TGGsNsypluI",
            )
            cur = conn.cursor()
            cur.execute("SELECT youtube FROM Links ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()

            if result:
                video_url = result[0]

                youtubeWidget = self.youtubeContainer
                if youtubeWidget.layout() is not None:
                    while youtubeWidget.layout().count() > 0:
                        item = youtubeWidget.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)

                # Modify the video URL to include the ads
                modified_video_url = video_url + "?advertising=1"

                self.youtube_view.load(QUrl(modified_video_url))
                youtubeWidget.layout().addWidget(self.youtube_view)

            def play_video():
                self.youtube_view.page().runJavaScript("document.querySelector('video').currentTime = 0; document.querySelector('video').play();")
            self.youtube_view.loadFinished.connect(play_video)

    def get_trading_pairs_from_combo_box(self):
        try:
            self.selected_pair = self.combo_1.currentText()
            selected_pair = self.combo_1.currentText()
            if selected_pair not in self.trade_pair:
                QMessageBox.about(self, "Notice", "<strong><small><center>You either did not select any Trading Pair or your Trading Pair is not found in the list.</center></small></strong>")
            else:
                base_currency = selected_pair.split("/")[0]
                quote_currency = selected_pair.split("/")[1]

                base_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

                # Make a GET request to the API
                response = requests.get(base_url)

                # Check the status code of the response to make sure it was successful
                if response.status_code == 200:
                    # Parse the response data as JSON
                    data = response.json()

                    # Get the exchange rate for the selected pair from the response data
                    rate = data['rates'][quote_currency]

                    # Return the currency pair and exchange rate as a tuple
                    return (selected_pair, rate)
                else:
                    # If the request was not successful, return None
                    return None
        except Exception as e:
            QMessageBox.about(self, "Notice", "<strong><small><center>An Error Occurred</center></small></strong><br> <p><small></small></p><br/>" + str(e))

    def get_selected_pair(self):
        try:
            # Get the selected trading pair and rate
            selected_pair, rate = self.get_trading_pairs_from_combo_box()
            if selected_pair is None:
                QMessageBox.about(self, "Notice", "<strong><small><center>You either did not select any Trading Pair or your Trading Pair is not found in the list.</center></small></strong>")
            else:
                #set to a label
                self.labelPair.setText(selected_pair)
                self.labelPair_1.setText(str(rate))

                # Calculate the signal strength (you can use any method you want to calculate the signal strength)
                signal_strength = rate * 80
                
                signal_strength = random.uniform(0.85, 0.95)
                getPercentage = round(int(signal_strength*100), 3)
                self.strengthBar_5.setText(str(getPercentage) + " %")
        except Exception as e:
            QMessageBox.about(self, "Notice", "<center><strong><small><center>An Error Occurred</center></small></strong><br> <p><small>Check your Network Connection!!!</small></p></center><br/>" + str(e))

    def start_timer_thread(self,counter_value):
        self.my_thread.counter = counter_value
        self.my_thread.start()
    
    def combo_selection_changed(self):
        combo_value = self.combo_2.currentText()
        if combo_value == "1 mins":
            counter_value = 60
        elif combo_value == "2 mins":
            counter_value = 120
        elif combo_value == "3 mins":
            counter_value = 180
        elif combo_value == "4 mins":
            counter_value = 240
        elif combo_value == "5 mins":
            counter_value = 300
        elif combo_value == "10 mins":
            counter_value = 600
        elif combo_value == "15 mins":
            counter_value = 900
        elif combo_value == "30 mins":
            counter_value = 1800
        elif combo_value == "1 hrs":
            counter_value = 3600
        elif combo_value == "2 hrs":
            counter_value = 7200
        elif combo_value == "3 hrs":
            counter_value = 10800
        elif combo_value == "4 hrs":
            counter_value = 14400
        elif combo_value == "5 hrs":
            counter_value = 18000

        self.start_timer_thread(counter_value)

    def update_progress_bar(self, display_text):
        hours, minutes, seconds = map(int, display_text.split(':'))
        total_seconds = 3600*hours + 60*minutes + seconds
        self.timerBar.display(display_text)
        if total_seconds <= 20:
            self.timerBar.hide()
            self.timerBar_2.show()
            self.telegramAction.show()
            self.telegramAction_2.hide()
            self.timerBar_2.display(display_text)
            # Stop the video playback and remove the widget from the layout
            self.youtubeContainer.layout().removeWidget(self.youtube_view)
            self.youtube_view = None
            self.youtubeWidget.setEnabled(False)
            self.premiumAds.show()
        else:
            self.premiumAds.hide()
            self.youtubeWidget.setEnabled(True)
            self.timerBar.show()
            self.timerBar_2.hide()
            self.telegramAction.hide()
            self.telegramAction_2.show()
            self.timerBar.display(display_text)

    def reset(self):
        self.menuContainer.setEnabled(True)
        self.getPairButton.setEnabled(True)
        self.comboPair.setEnabled(True)
        self.comboTimer.setEnabled(True)
        self.signalBanner.hide()
        self.signalBanner_2.hide()
        self.connectingLabel.hide()
        self.combo_1 = self.findChild(QComboBox, "comboPair")
        self.combo_1.setCurrentText("EUR/USD")
        self.combo_2 = self.findChild(QComboBox, "comboTimer")
        self.combo_2.setCurrentText("1 mins")

    def runSignal(self):
        self.get_selected_pair()
        self.combo_selection_changed()
        self.delayresult()
        self.startAds()
        self.premiumAds.hide()
        self.menuContainer.setEnabled(False)
        self.option_generator.generateOption()

    @pyqtSlot(str)
    def updateLabel(self, option):
        self.telegramAction.setText(option)
        self.telegramAction_2.setText(option)
        if option == 'Buy':
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.show())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.hide())
        elif option == 'Sell':
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.hide())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.show())
        else:
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner.hide())
            QtCore.QTimer.singleShot(9000, lambda: self.signalBanner_2.hide())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    welcome=ApplicationScreen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(welcome)
    app.setApplicationName("FXsignalspot")
    app.setWindowIcon(QIcon("resources/fxsignalspot.png"))
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
