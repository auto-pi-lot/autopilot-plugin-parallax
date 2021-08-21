try:
    import OpenGL as ogl

    try:
        import OpenGL.GL  # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        print('Drat, patching for Big Sur')
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res: return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
except ImportError:
    pass

import sys
from time import time
import numpy as np
from collections import deque
from PySide2 import QtWidgets, QtCore, QtGui
import PySide2
import pyqtgraph as pg
import pyqtgraph.opengl as gl

import autopilot
from autopilot.networking import Net_Node

def mesh_sphere(x_points = 13, y_points=13):
    u = np.linspace(0, 2 * np.pi, x_points)
    v = np.linspace(0, np.pi, y_points)

    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    return np.column_stack((x.flatten(), y.flatten(), z.flatten()))

class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, queue_size=500, *args, **kwargs):
        super(PlotWindow, self).__init__(*args, **kwargs)
        self.layout = QtWidgets.QGridLayout()
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # timeseries plot of accel, gyro, and position
        self.accel = pg.PlotWidget(parent=self, title='Acceleration')
        self.gyro = pg.PlotWidget(parent=self, title='Gyro')
        self.position = pg.PlotWidget(parent=self, title='Position')
        self.velocity = pg.PlotWidget(parent=self, title='Velocity Estimate')

        self.curves = {'accel':{}, 'gyro':{}}
        self.arrays = {'accel':{}, 'gyro':{}}
        for ax, color in zip(('x', 'y', 'z'), ((255,0,0),(0,255,0),(0,0,255))):
            for sensor in ('accel', 'gyro'):
                widg = getattr(self, sensor)
                self.curves[sensor][ax] = widg.plot(pen=color,name=ax)
                self.arrays[sensor][ax] = (deque(maxlen=queue_size), deque(maxlen=queue_size))
        self.curves['position'] = self.position.plot(name='z position')
        self.curves['velocity'] = self.velocity.plot(name='z velocity')
        self.arrays['position'] = (deque(maxlen=queue_size), deque(maxlen=queue_size))
        self.arrays['velocity'] = (deque(maxlen=queue_size), deque(maxlen=queue_size))

        # orientation vector
        self.sphere = gl.GLScatterPlotItem(pos=mesh_sphere(), color=(1,1,1,0.3),size=5)
        self.glview = gl.GLViewWidget()
        self.glview.opts['distance']=3
        self.orientation = gl.GLLinePlotItem(color=(1,0,0,1))
        self.glview.addItem(self.orientation)
        self.glview.addItem(self.sphere)

        gz = gl.GLGridItem()
        gz.translate(0, 0, -1)
        self.glview.addItem(gz)

        self.rotator = autopilot.get('transform', 'Rotate')(dims='xy', inverse='y')

        # image display
        self.imagewidget = pg.PlotWidget(parent=self, title='Video Feed')
        self.image = pg.ImageItem()
        self.image.setZValue(-100)
        self.dlc_points = pg.ScatterPlotItem()
        self.imagewidget.addItem(self.image)
        self.imagewidget.addItem(self.dlc_points)
        self.image = pg.ImageView(parent=self, name='Video Feed')

        self.layout.addWidget(self.position, 0, 0, 1,2)
        self.layout.addWidget(self.velocity, 1, 0, 1,2)
        self.layout.addWidget(self.accel, 2, 0, 1,2)
        self.layout.addWidget(self.gyro, 3, 0, 1,2)
        self.layout.addWidget(self.glview, 0,2, 2, 1)
        self.layout.addWidget(self.image, 2,2, 2, 1)

        self.node = Net_Node(id='plotter',upstream='',port=9999,
                             listens={'DATA':self.l_data,'IMAGE':self.l_image},
                             router_port=6000)

        #self.test()

    def test(self):
        for ax in ('x','y','z'):
            self.curves['accel'][ax].setData(np.random.rand(100))
            self.curves['gyro'][ax].setData(np.random.rand(100))

    def l_data(self, data:dict):
        if 'accel' in data.keys():
            for val, ax in zip(data['accel'], ('x','y','z')):
                self.arrays['accel'][ax][0].append(time())
                self.arrays['accel'][ax][1].append(val)
                self.curves['accel'][ax].setData(self.arrays['accel'][ax][0], self.arrays['accel'][ax][1])

        if 'gyro' in data.keys():
            for val, ax in zip(data['gyro'], ('x','y','z')):
                self.arrays['gyro'][ax][0].append(time())
                self.arrays['gyro'][ax][1].append(val)
                self.curves['gyro'][ax].setData(self.arrays['gyro'][ax][0], self.arrays['gyro'][ax][1])

        if 'position' in data.keys():
            self.arrays['position'][0].append(time())
            self.arrays['position'][1].append(data['position'])
            self.curves['position'].setData(self.arrays['position'][0], self.arrays['position'][1])

        if 'velocity' in data.keys():
            self.arrays['velocity'][0].append(time())
            self.arrays['velocity'][1].append(data['velocity'])
            self.curves['velocity'].setData(self.arrays['velocity'][0], self.arrays['velocity'][1])

        if 'rotation' in data.keys():
            x, y, z = self.rotator.process(((1,1,1),data['rotation']))
            self.orientation.setData(pos=np.array(((0,0,0),(x,y,z))))

    def l_image(self, image):
        self.image.setImage(image['input'])
        self.dlc_points.setData(pos=image[output][:,0:2])




if __name__ == "__main__":




    app = QtWidgets.QApplication(sys.argv)

    main = PlotWindow()
    main.show()
    sys.exit(app.exec_())