# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scene.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.realTimeVideoButton = QtWidgets.QPushButton(self.centralwidget)
        self.realTimeVideoButton.setGeometry(QtCore.QRect(300, 440, 93, 28))
        self.realTimeVideoButton.setObjectName("realTimeVideoButton")
        self.videoLabel = QtWidgets.QLabel(self.centralwidget)
        self.videoLabel.setGeometry(QtCore.QRect(190, 90, 320, 320))
        self.videoLabel.setObjectName("videoLabel")
        self.tipLabel = QtWidgets.QLabel(self.centralwidget)
        self.tipLabel.setGeometry(QtCore.QRect(310, 60, 81, 16))
        self.tipLabel.setObjectName("tipLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.realTimeVideoButton.setText(_translate("MainWindow", "开启摄像头"))
        self.videoLabel.setText(_translate("MainWindow", "TextLabel"))
        self.tipLabel.setText(_translate("MainWindow", "TextLabel"))