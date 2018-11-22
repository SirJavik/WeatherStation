import sys
import os
import time
import sys


from pprint                 import pprint
from PyQt5                  import QtCore, QtWidgets, Qt, QtWebKitWidgets
from PyQt5.QtCore           import QUrl, QThread, QSize, pyqtSignal
from PyQt5.QtWidgets        import QMainWindow, QWidget, QLabel, QLineEdit, QSlider, QPushButton,QHBoxLayout,QVBoxLayout,QSpacerItem,QSizePolicy,QGridLayout,QGroupBox, QApplication, QWidget 
from PyQt5.QtWebKitWidgets  import QWebView , QWebPage
from PyQt5.QtWebKit         import QWebSettings
from PyQt5.QtNetwork        import *


from WeatherSensors import *

ProgramEnd = False

class WeatherWindow(QWidget):
    def createURL(self, localRes):
        lclStr = "file://"+os.path.dirname(os.path.abspath(__file__))+"/"+localRes
        return lclStr
        
    def trigger_sensor(self, value):
        self.webview.page().mainFrame().evaluateJavaScript('$(".barometer").html("'+str(value[2]/100)+' hPa")')
        self.webview.page().mainFrame().evaluateJavaScript('$(".temperature_indoor").html("'+str(value[3])+' °C")')
        self.webview.page().mainFrame().evaluateJavaScript('$(".humidity_indoor").html("'+str(value[0])+' %")')
    
    def __init__(self, parent=None):
        super(WeatherWindow, self).__init__(parent)


        self.setMinimumSize(QSize(480,270))
        self.setWindowTitle("WeatherStation")

        url = self.createURL("html/start.html")
        self.webview = QtWebKitWidgets.QWebView()
        self.webview.load(QUrl(url))



        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        layout.addWidget(self.webview)
        self.showFullScreen()
        self.setLayout(layout)

    def keyPressEvent(self, event):
        try:
            if event.key() == QtCore.Qt.Key_Escape:
                print ("RIP Program")
                global ProgramEnd
                ProgramEnd = True
                self.deleteLater()
            elif event.key() == QtCore.Qt.Key_F11:
                if self.windowState() & QtCore.Qt.WindowFullScreen:
                    self.showNormal()
                else:
                    self.showFullScreen()
            elif event.key() == QtCore.Qt.Key_Enter:
                self.proceed()
            event.accept()
        except Exception as e:
            print(e)

class childThread(QThread):
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self,Winclass, parent=None):
        try:
            super(childThread, self).__init__(parent)
            self.sig.connect(Winclass.trigger_sensor)
        except Exception as e:
            print(e)

    def __del__(self):
        self.wait()

    def _sensor_runner(self):
        try:
            
            barometer = Barometer()
            barometer_result = barometer.run()

            humidity = Humidity()
            humidity_result = humidity.run()

            while isinstance(humidity_result, (bool)):
                humidity_result = humidity.run()

            hum_humidity, hum_temperature = humidity_result
            bar_pressure, bar_temperature = barometer_result
            
            sensorData = [
                hum_humidity,
                hum_temperature,
                bar_pressure,
                bar_temperature
            ]
            
            return sensorData
        except Exception as e:
            print(e)

    def run(self):
        try:
            global ProgramEnd
            while ProgramEnd != True:
                sensorData = self._sensor_runner()
                pprint(sensorData)
                self.sig.emit(sensorData)
                time.sleep(10)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWin=WeatherWindow()
    mainWin.show()

    try:
        thread = childThread(mainWin)
        thread.start()
    except Exception as e:
        print(e)

    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
