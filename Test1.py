#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import Thread
from multiprocessing import Process
from collections import deque
from datetime import datetime
import time
import torch
import neoapi
import sys, pdb, traceback
import cv2
import numpy as np
import os
import glob
#import modbus_tk
#import modbus_tk.defines as cst
#from modbus_tk import modbus_rtu
import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from detect_qt5 import main_detect, my_lodelmodel

dir_path = os.getcwd()
path = dir_path + 'data/shots/'
frame_cam = None

####MODBUS BLOCK##########
try:
    PORT = 'COM3'
    modbusServ = modbus_rtu.RtuServer(serial.Serial(PORT), baudrate= 19200,
                                  bytesize=8, parity='N', stopbits=1, xonxoff=0)
    print("start")
    modbusServ.start() #Enable MB server
    slave_1 = modbus_tk.modbus.Slave(1) #Add slave
    slave_1.add_block ( "1", modbus_tk.defines.HOLDING_REGISTERS, 1, 5)
except:
    print(f'COM-port with name {PORT} can not be opend')


######---------Виджет отоброжения-----------
class CameraWidget(QWidget):
    new_detect = pyqtSignal()
    def __init__(self, width, height, stream_link=0, aspect_ratio=False, parent=None, deque_size=1):
        super(CameraWidget, self).__init__(parent)
        self.date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        # Initialize deque used to store frames read from the stream
        self.deque = deque(maxlen=deque_size)
        self.shot_taken = False
        self.screen_width = width
        self.screen_height = height
        self.maintain_aspect_ratio = aspect_ratio
        self.date = " "
        self.camera_stream_link = stream_link
        self.Grid = QGridLayout()
        #self.detect_check = pyqtSignal(bool, name='Det_check')
        #self.detect_check.connect(self.detected_out)
        #self.detect_check.emit()
        # Flag to check if camera is valid/working
        self.online = False
        self.frame_cam = None
        self.my_model = my_lodelmodel()
        self.video_frame = QLabel()
        # Start background frame grabbings
        self.get_frame_thread = Thread(target=self.get_frame, args=([0.05]))
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()
        self.thread_name = self.get_frame_thread.ident
        #print('Frame thread', self.get_frame_thread.ident)
        self.timer = QTimer()
        #self.timer2 = QTimer()
        #self.timer2.timeout.connect(self.get_frame)
        self.timer.timeout.connect(self.set_frame)
        #self.timer2.start(10)
        self.timer.start(5)
        self.detected = False
        #print('Started camera: {}'.format(self.camera_stream_link))


    def get_frame(self, t = 0.05):
        """Reads frame"""
        while True:
            frame = self.camera_stream_link.GetImage().GetNPArray()
            self.deque.append(frame)
            self.spin(.001)
            #time.sleep(t)


    def spin(self, seconds):
        """Pause for set amount of seconds, replaces time.sleep so program doesnt stall"""
        time_end = time.time() + seconds
        while time.time() < time_end:
            QApplication.processEvents()


    def set_frame(self, but_pres=False):
        """Sets pixmap image to video frame"""
        self.proc = False
        self.but_press = but_pres
        #if not self.yolo_active: Test with one thread and two methods
        if self.deque:
            if pb4.text() == 'Disabled YOLO':
                frame = self.deque[-1]
                if not self.but_press:
                    self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = self.frame.shape
                    bytesPerLine = ch * w
                    self.img = QImage(self.frame, w, h, bytesPerLine, QImage.Format_RGB888)
                    self.pix = QPixmap.fromImage(self.img)
                    self.video_frame.setPixmap(self.pix)
                else:
                    self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                    self.img_name = (f'frame_{datetime.now().strftime("%Y_%m_%d--%I-%M-%S.%f_%p")}.png')
                    cv2.imwrite(os.path.join(path, self.img_name), self.frame)
                    print("{} written!".format(self.img_name))
                    self.but_press = False
            else:
                frame = self.deque[-1]
                #try:
                time_st = time.time()
                camera_source = dir_path + f"\\data\\test\\{self.thread_name}.jpg"
                print(camera_source)
                cv2.imwrite(camera_source, frame)
                print('Img to model step', time.time() - time_st)
                im0, label, s_out = main_detect(self.my_model, camera_source)
                print('Last step', time.time() - time_st)
                #print('Sec step', time.time() - time_st)
                if not (len(s_out)==0):
                    s_out = s_out.split(',')
                    if len(s_out) > 2:
                        #print('DETECTED!')
                        self.detected = True
                        self.detected_out()
                    else:
                        self.detected = False
                        #print(s_out[i])
                    #print('lable:', self.lables)
                if label == 'debug':
                    print("labelkong")
                self.frame = cv2.resize(im0, (self.screen_width, self.screen_height))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = self.frame.shape
                bytesPerLine = ch * w
                self.img = QImage(self.frame, w, h, bytesPerLine, QImage.Format_RGB888)
                self.pix = QPixmap.fromImage(self.img)
                self.video_frame.setPixmap(self.pix)
                self.spin(.001)
                #except:
                #    extype, value, tb = sys.exc_info()
                #    traceback.print_exc()
                #    pdb.post_mortem(tb)


    def get_video_frame(self):
        return self.video_frame

    @pyqtSlot()
    def detected_out(self):
        self.new_detect.emit()
        #assert self.detected


def exit_application():
    """Exit program event handler"""
    sys.exit(1)


def CamExec():
    cameraIds = []
    camerainfolist = neoapi.CamInfoList()
    camerainfolist.Refresh()
    try:
        for camerainfo in camerainfolist:
            cameraname = camerainfo.GetModelName() + "_" + camerainfo.GetSerialNumber()
            print(' [{:2d}]'.format(len(cameraIds) + 1), '{:27s}'.format(cameraname), end="")
            if camerainfo.GetTLType() == "GEV":
                print(' at {:s}'.format(camerainfo.GetGevIpAddress()), end="")
            elif camerainfo.GetTLType() == "U3V":
                print(' at {:s}'.format(camerainfo.GetUSBPortID()), end="")
            print("")
            # cameraIds.append(camerainfo.GetId())
            cameraIds.append(camerainfo.GetSerialNumber())
        print("")

        # Cam1 = neoapi.Cam()
        # Cam2 = neoapi.Cam()
        # Cam3 = neoapi.Cam()

        Cam1.Connect('700007168243')
        Cam1.f.TriggerMode.SetString("On")  # temporary On to stop capturing
        Cam2.Connect('700007168244')
        Cam2.f.TriggerMode.SetString("On")  # temporary On to stop capturing
        Cam3.Connect('700007168246')
        Cam3.f.TriggerMode.SetString("On")  # temporary On to stop capturing

        ###Уставка для первой камеры
        Cam1.f.ExposureTime.Set(5000)
        Cam1.f.Height.Set(640)
        Cam1.f.Width.Set(960)
        # Cam1.
        # Cam1.f.OffsetX.Set(320)
        Cam1.f.OffsetY.Set(230)
        #Cam1.f.ColorTransformationEnable(True)
        Cam1.f.ColorTransformationAuto.SetString("Continuous")

        ###Уставка для второй камеры
        Cam2.f.ExposureTime.Set(5000)
        Cam2.f.Height.Set(600)
        Cam2.f.Width.Set(960)
        Cam2.f.OffsetX.Set(480)
        Cam2.f.OffsetY.Set(120)
        Cam2.f.ColorTransformationAuto.SetString("Continuous")

        ###Уставка для третьей камеры
        Cam3.f.ExposureTime.Set(5000)
        Cam3.f.Height.Set(600)
        Cam3.f.Width.Set(960)
        Cam3.f.OffsetY.Set(150)
        Cam3.f.ColorTransformationAuto.SetString("Continuous")


        Cam1.f.PixelFormat.SetString('BGR8')
        Cam2.f.PixelFormat.SetString('BGR8')
        Cam3.f.PixelFormat.SetString('BGR8')

        Cam1.f.GevSCPD.Set(((3 - 1) * Cam1.f.GevSCPSPacketSize.Get() * 8) * 110 // 100)  # 0.33 Gbit/s
        Cam2.f.GevSCPD.Set(((3 - 1) * Cam2.f.GevSCPSPacketSize.Get() * 8) * 110 // 100)  # 0.33 Gbit/s
        Cam3.f.GevSCPD.Set(((3 - 1) * Cam3.f.GevSCPSPacketSize.Get() * 8) * 110 // 100)  # 0.33 Gbit/s

        print(" Cam1 GevSCPD: ", Cam1.f.GevSCPD.Get())
        print(" Cam2 GevSCPD: ", Cam2.f.GevSCPD.Get())
        print(" Cam3 GevSCPD: ", Cam3.f.GevSCPD.Get())

        Cam1.f.TriggerMode.SetString("Off")
        Cam2.f.TriggerMode.SetString("Off")
        Cam3.f.TriggerMode.SetString("Off")
    except (neoapi.NeoException) as exc:
        print('error: ', exc.GetDescription())


# set value to the registers of modbus slave
def slave_server(data):
        slave_1.set_values("1", 1, data)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mw = QMainWindow()
    mw.setWindowTitle('Camera GUI')
    cw = QWidget()
    ml = QGridLayout()
    cw.setLayout(ml)
    mw.setCentralWidget(cw)
    Cam1 = neoapi.Cam()
    Cam2 = neoapi.Cam()
    Cam3 = neoapi.Cam()
    #files = glob.glob(dir_path + '\\data\\test\\')
    #for f in files:
    #    os.remove(f)
    #Init cam
    CamExec()
    # Dynamically determine screen width/height
    screen_width = 780
    screen_height = 250
    # Create camera widgets
    print('Creating Camera Widgets...')
    zero = CameraWidget(screen_width, screen_height, Cam1)
    one = CameraWidget(screen_width, screen_height, Cam2)
    two = CameraWidget(screen_width, screen_height, Cam3)
    pb1 = QPushButton("Shot1")
    pb2 = QPushButton("Shot2")
    pb3 = QPushButton("Shot3")
    pb4 = QPushButton("Disabled YOLO")

# detected on first cam
    def Cam1_det():
        print('CAM1')

# detected on second cam
    def Cam2_det():
        print('CAM2')

# detected on third cam
    def Cam3_det():
        print('CAM3')

# signal when yolo detected objects on images
    zero.new_detect.connect(Cam1_det)
    one.new_detect.connect(Cam2_det)
    two.new_detect.connect(Cam3_det)

# Check radioBut status and turn on/off yolo computing
    def radio_check():
        if pb4.text() == 'Disabled YOLO':
            pb4.setText('Enabled YOLO')
        else:
            pb4.setText('Disabled YOLO')


# Buttons for take images from camera frames
    pb1.clicked.connect(lambda: zero.set_frame(True))
    pb2.clicked.connect(lambda: one.set_frame(True))
    pb3.clicked.connect(lambda: two.set_frame(True))
    pb4.clicked.connect(radio_check)



# Add widgets to layout
    print('Adding widgets to layout...')
    ml.addWidget(pb4, 0, 0, 1, 1)
    ml.addWidget(zero.get_video_frame(), 1, 0, 1, 1)
    ml.addWidget(one.get_video_frame(), 3, 0, 1, 1)
    ml.addWidget(two.get_video_frame(), 5, 0, 1, 1)
    ml.addWidget(pb1, 2, 0, 1, 1)
    ml.addWidget(pb2, 4, 0, 1, 1)
    ml.addWidget(pb3, 6, 0, 1, 1)
    print('Verifying camera credentials...')
    mw.show()
    QShortcut(QKeySequence('Ctrl+Q'), mw, exit_application)

    sys.exit(app.exec())



