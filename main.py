# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\scene.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import random
import sys
import time

import cv2
import dlib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QMessageBox
from numpy import iterable

from detector import detector
from pose_liveness_video import load_model, face_direction_detect
from scene import Ui_MainWindow
import config as cfg


class Main_Window(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.CAM_NUM = 0  # 为0时表示视频流来自笔记本内置摄像头
        self.slot_init()
        self.ui_init()
        # self.EYE_BLINK = 0
        # self.OPEN_MOUSE = 1
        # self.RIGHT_HEAD = 2
        # self.LEFT_HEAD = 3
        self.action_list = range(4)
        self.ACTION_NUM = 4  # 动作数量
        self.keep_status = 0  # 当前状态持续了多久
        self.status = -1

    def ui_init(self):
        self.ui.tipLabel.setText('请正对屏幕')

    def model_init(self):
        self.face_pos_detector = dlib.get_frontal_face_detector()
        self.detector = detector(detector=dlib.shape_predictor(cfg.landmarks),
                                 face_pos_detector=self.face_pos_detector)
        self.face_dir_model = load_model(cfg.path_hopenet, device=cfg.device)

    def slot_init(self):
        self.ui.realTimeVideoButton.clicked.connect(self.button_open_camera_clicked)
        self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()

    def stats_init(self):  # 初始化需要用到的统计参数
        self.blink_frame = 0
        self.blink_times = 0

        self.open_frame = 0
        self.open_times = 0
        self.keep_status = 0  # 帧数计数器

    def button_open_camera_clicked(self):
        if self.timer_camera.isActive() == False:
            # 打开摄像头并显示图像信息
            self.openCamera()
            self.chosen_action=[0,1,2,3]
            # self.chosen_action = random.sample(range(len(self.action_list)), self.ACTION_NUM)  # 随机挑选动作
            self.cur_act = 0  # 当前进行的动作
            time.sleep(1)
            self.stats_init()
            self.model_init()
        else:
            # 关闭摄像头并清空显示信息
            self.closeCamera()

    def openCamera(self):
        flag = self.cap.open(self.CAM_NUM)
        if flag == False:
            msg = QMessageBox.Warning(self, u'Warning', u'请检测相机与电脑是否连接正确',
                                      buttons=QMessageBox.Ok,
                                      defaultButton=QMessageBox.Ok)
        else:
            self.timer_camera.start(30)
        self.ui.realTimeVideoButton.setText('关闭摄像头')

    def closeCamera(self):
        self.timer_camera.stop()
        self.cap.release()
        self.ui.videoLabel.clear()
        self.ui.realTimeVideoButton.setText('打开摄像头')

    def show_camera(self):
        if self.keep_status > cfg.FRAME_LIMIT:
            self.detect_finish(0)  # 超过限定时间没有通过验证
        flag, self.image = self.cap.read()  # 从视频流中读取
        show = cv2.resize(self.image, (320, 320))  # 把读到的帧的大小重新设置为 320 320
        # 检测人脸位置
        face_result = self.detect_face(show)
        if iterable(face_result):
            x1, y1, x2, y2, rect = face_result
            show = cv2.rectangle(show, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            self.ui.tipLabel.setText('请正对屏幕')
            if self.status == -1:
                self.keep_status += 1
            self.status = -1
        # cv2.rectangle(show, (60, 60), (260, 260), (0, 255, 0), 2)
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                 QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.ui.videoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
        if not iterable(face_result): return  # 没检测到人脸直接返回
        real_flag = False

        self.make_instruction()  # 对用户做出指示

        if self.action_list[self.chosen_action[self.cur_act]] == 0:
            self.blink_frame, self.blink_times = self.detect_blink(show, rect, self.blink_frame, self.blink_times)
            if self.blink_times > cfg.EYE_AR_TOTAL_THRESH:
                real_flag = True
            if self.status == 0: self.keep_status += 1
            self.status = 0
        elif self.action_list[self.chosen_action[self.cur_act]] == 1:
            self.open_frame, self.open_times = self.detect_open_mouse(show, rect, self.open_frame, self.open_times)
            if self.open_times >= cfg.MOUTH_OPEN_TOTAL_THRESH:
                real_flag = True
            if self.status == 1: self.keep_status += 1
            self.status = 1
        elif self.action_list[self.chosen_action[self.cur_act]] == 2:
            if self.detect_turn_head(show, rect, right=0):
                real_flag = True
            if self.status == 2: self.keep_status += 1
            self.status = 2
        elif self.action_list[self.chosen_action[self.cur_act]] == 3:
            if self.detect_turn_head(show, rect, right=1):
                real_flag = True
            if self.status == 3: self.keep_status += 1
            self.status = 3
        if real_flag:
            self.cur_act += 1
            if self.cur_act >= len(self.chosen_action):
                self.detect_finish()
            else:
                self.stats_init()

    def make_instruction(self):
        if self.action_list[self.chosen_action[self.cur_act]] == 0:
            self.ui.tipLabel.setText('请眨眼')
        elif self.action_list[self.chosen_action[self.cur_act]] == 1:
            self.ui.tipLabel.setText('请张嘴')
        elif self.action_list[self.chosen_action[self.cur_act]] == 2:
            self.ui.tipLabel.setText('请向左转头')
        elif self.action_list[self.chosen_action[self.cur_act]] == 3:
            self.ui.tipLabel.setText('请向右转头')

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = self.face_pos_detector(gray, 0)  # 框出人脸
        if len(rects) != 1: return len(rects)
        for rect in rects:
            y1 = rect.top() if rect.top() > 0 else 0
            y2 = rect.bottom() if rect.bottom() > 0 else 0
            x1 = rect.left() if rect.left() > 0 else 0
            x2 = rect.right() if rect.right() > 0 else 0
            return x1, y1, x2, y2, rect

    def detect_blink(self, img, rect, blink_frame, blink_times):
        blink_frame, blink_times = self.detector.eye_blink(img, rect, blink_frame, blink_times)
        return blink_frame, blink_times

    def detect_open_mouse(self, img, rect, open_frame, open_times):
        open_frame, open_times = self.detector.mouth_open(img, rect, open_frame, open_times)
        return open_frame, open_times

    def detect_turn_head(self, img, rect, right=0):  # right=0：左转头
        y1 = rect.top() if rect.top() > 0 else 0
        y2 = rect.bottom() if rect.bottom() > 0 else 0
        x1 = rect.left() if rect.left() > 0 else 0
        x2 = rect.right() if rect.right() > 0 else 0
        head = img[x1:x2, y1:y2, :]
        return face_direction_detect(head, self.face_dir_model, right, device=cfg.device)

    # 检测完成
    def detect_finish(self, success=1):
        if success:
            self.ui.tipLabel.setText('验证成功！')
        else:
            self.ui.tipLabel.setText('验证失败')
        self.ui.videoLabel.clear()
        self.cap.release()
        self.closeCamera()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = Main_Window()
    dlg.show()
    sys.exit(app.exec_())
