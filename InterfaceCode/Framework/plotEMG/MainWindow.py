import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtCore import QTimer
import random
import numpy as np
from scipy import interpolate
import socket
import pytrigno
import _thread
import time

from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = '这里可以修改标题'
        self.width = 1280
        self.height = 720
        self.path = ''
        samples_per_read = 100
        self.dev = pytrigno.TrignoEMG(channel_range = (0, 3), samples_per_read = samples_per_read, host = '', buffered = True)
        try:
            self.dev.start()
        except:
            print("something went wrong")
            raise socket.timeout("Could not connect to Delsys Station")
        self.dev.recordFlag = True
        _thread.start_new_thread(self.dev.read, ())
        _thread.start_new_thread(self.dev.getFeatures, ())
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.button1 = QPushButton('video1', self)
        self.button1.move(600, 320)
        self.button1.resize(100, 40)
        self.button1.clicked.connect(lambda: self.changeVideo(0))

        self.button2 = QPushButton('video2', self)
        self.button2.move(800, 320)
        self.button2.resize(100, 40)
        self.button2.clicked.connect(lambda: self.changeVideo(1))

        self.button3 = QPushButton('video3', self)
        self.button3.move(1000, 320)
        self.button3.resize(100, 40)
        self.button3.clicked.connect(lambda: self.changeVideo(2))

        m1 = PlotCurves(self, width=12, height=3, dev = self.dev)#实例化一个画布对象
        m1.move(0, 0)
        m2 = PlotRadar(self, width=6, height=3, dev = self.dev)#实例化一个画布对象
        m2.move(0, 360)
        video = QVideoWidget(self)
        video.setGeometry(600,360,600,300)
        self.mplayer = QMediaPlayer(video)
        self.mplayer.setVideoOutput(video)
        self.mplayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.path))) 
        # mplayer.play()
        self.show()


    def changeVideo(self, i):
        play_list = ['/Users/lwre/Downloads/毕业设计/movie.mov', '/Users/lwre/Downloads/毕业设计/陈宏源.mp4', '/Users/lwre/Desktop/1.mov']
        print(i)
        m3 = PlayVideo(self, path = play_list[i])
        self.path = play_list[i]
        self.mplayer.play()
class PlayVideo(QVideoWidget):
    def __init__(self, parent = None, path = ''):
        super().__init__(parent)
        self.setGeometry(600,360,600,300)
        self.show()
        self.mplayer = QMediaPlayer(self)
        self.mplayer.setVideoOutput(self)
        self.mplayer.setMedia(QMediaContent(QUrl.fromLocalFile(path))) 
        self.mplayer.play()

class PlotRadar(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100, dev = None):



        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111,polar = True)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


        # self.ax.set_title("MAV", va='bottom')
        low_ch = 0
        high_ch = 3
        self.channel_num = high_ch - low_ch + 1
        self.dev = parent.dev


        self.plot()#打开App时可以初始化图片
        #self.plot()


    def plot(self):

        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def update_figure(self):
        if self.dev.features.shape[1]:
            self.ax.cla()
            angles = np.linspace(0, 2*np.pi, self.channel_num, endpoint=False)
            labels = np.array(['ch1','ch2','ch3','ch4'])
            self.ax.set_thetagrids(angles * 180/np.pi, labels = labels)
            self.ax.grid(True)
            self.ax.plot(np.concatenate((angles, [angles[0]])), np.concatenate((self.dev.features[:,-1], [self.dev.features[0,-1]]))*1e5, 'ro-', linewidth=2)
            self.draw()

class PlotCurves(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100, dev = None):



        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        low_ch = 0
        high_ch = 3
        self.channel_num = high_ch - low_ch + 1
        self.dev = dev

        self.t = 0
        self.plot()#打开App时可以初始化图片
        self.t0 = time.time()

        #self.plot()


    def plot(self):

        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1)

    def initLabel(self):
        self.ax.set_title("EMG", va='bottom')
        self.ax.set_yticks([0,4,8,12])
        self.ax.set_yticklabels(['ch1', 'ch2', 'ch3', 'ch4'])
        self.ax.invert_yaxis()

    def update_figure(self):
        fs = 2000
        plot_time = 10
        if self.dev.buffer.shape[1]<fs*plot_time*(self.t+1):
            self.ax.cla()
            self.initLabel()
            self.ax.set_xlim((self.t*10,self.t*10+10))
            self.ax.set_ylim((-1.5,1.5+13.5))
            for i in range(4):
                y = self.dev.buffer
                self.ax.plot(np.arange(y.shape[1])/fs, y[i]*1e4+4*i)
            self.draw()
        else:
            print(time.time() - self.t0) 
            self.t0 =time.time()
            self.t += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
