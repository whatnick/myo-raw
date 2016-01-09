


#adapted from:
#https://github.com/ptone/pyosc/blob/master/examples/knect-rcv.py

#!/usr/bin/env python3
from OSC import OSCServer
import sys
from time import sleep

server = OSCServer( ("localhost", 7110) )
server.timeout = 0
run = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def user_callback_imu(path, tags, args, source):
    global orientation, acceleration, newImuData
    orientation = args[:3]
    acceleration = args[3:]
    newImuData = [orientation, acceleration]
    update('imu')
    
    
def user_callback_emg(path, tags, args, source):
    global newEmgData

    newEmgData = args
    update('emg')


def quit_callback(path, tags, args, source):
    # don't do this at home (or it'll quit blender)
    global run
    run = False

server.addMsgHandler( "/myo/imu", user_callback_imu )
server.addMsgHandler( "/myo/emg", user_callback_emg )
#server.addMsgHandler( "/quit", quit_callback )

# user script that's called by the game engine every frame
def each_frame():
    print("each_frame")
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()


##############################################################################
##############################################################################
##############################################################################

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import time
import numpy as np


app = QtGui.QApplication([])

win = pg.GraphicsWindow()
win.resize(1000,600)
win.setWindowTitle('Myo Raw Osc GUI')


nEmg = 8

orientationPlot = win.addPlot(row=1,col=1,title="ORIENTATION")
accelerationPlot = win.addPlot(row=2,col=1,title="ACCELERATION")
emgPlot = win.addPlot(row=3,col=1,title="EMG")

plots=[]
plots.append(orientationPlot)
plots.append(accelerationPlot)
plots.append(emgPlot)

orientationPlot.setYRange(-np.pi,np.pi, padding=0)
accelerationPlot.setYRange(-2000,2000, padding=0)
emgPlot.setYRange(0,1000, padding=0)

for p in plots:
    p.hideButtons()
    p.showGrid(x=True,y=True,alpha=0.5)
    p.addLegend();
    p.setMouseEnabled(x=False,y=False)


orientationCurves = []
accelerationCurves = []
orientationNames = ['azimuth','elevation','roll']
accelerationNames = ['x','y','z']
for i in np.arange(3):
    orientationCurves.append(orientationPlot.plot(pen=pg.intColor(i),name=orientationNames[i]))
    accelerationCurves.append(accelerationPlot.plot(pen=pg.intColor(i),name=accelerationNames[i]))


emgCurves = []
for i in np.arange(nEmg):
    emgCurves.append(emgPlot.plot(pen=pg.intColor(i),name=i))

curves = []
curves.append(orientationCurves)
curves.append(accelerationCurves)
curves.append(emgCurves)

# values read from handler event

orientation = []
acceleration = []
newImuData = []
newEmgData = []

# historic trace of values
maxHist = 200
orientationHist = []
accelerationHist = []
emgHist = []

for i in np.arange(3):
    orientationHist.append(np.zeros(maxHist))
    accelerationHist.append(np.zeros(maxHist))
    
for i in np.arange(nEmg):
    emgHist.append(np.zeros(maxHist))
    
hist = [orientationHist, accelerationHist,emgHist]

indx = 0
def update(who):
    global hist, newImuData, newEmgData
    global curves, emgCurves, emgHist

    # imu
    if (who == 'imu'):
        for ii in np.arange(2):
            h = hist[ii]
            c = curves[ii]
            for i in np.arange(3):
                h[i][:-1] = h[i][1:]
                h[i][-1] = newImuData[ii][i]
                c[i].setData(h[i])
                
    if (who == 'emg'):
        h = emgHist
        c = emgCurves
        for i in np.arange(nEmg):
            h[i][:-1] = h[i][1:]
            h[i][-1] = newEmgData[i]
            c[i].setData(h[i])
                
    app.processEvents()
    
    



while run:
    server.handle_request()


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
        QtGui.QApplication.instance().exec_()

server.close()