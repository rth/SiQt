from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


from ..dep_resolv import calculate_dependencies


class ProgressBarWidget(QtWidgets.QWidget):

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        self.setGeometry(QtCore.QRect(100, 100, 400, 200))

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0, 100)
        layout.addWidget(self.progressBar)

        self.myLongTask = TaskThread(parent, main_window)
        self.progressTask = ProgressThread(parent, main_window)
        self.myLongTask.start()
        self.progressTask.start()
        self.myLongTask.taskFinished.connect(self.onFinished)

        self.progressTask.notifyProgress.connect(self.onProgress)
        self.base = main_window

    def onProgress(self, i):
        self.progressBar.setValue(i)

    def onFinished(self):
        obj = self.base.tabs['convolution']['threshold_slider']['qtobj']
        obj.setRange(0, self.base.gpr.cxx_max.max())

        self.base.view_mode = 'convolution'
        self.base.on_draw()
        self.base.set_dep_flag_recursive('convolution', True)

        calculate_dependencies(self.base)

        self.progressTask.terminate()
        self.close()


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.Signal()

    def __init__(self, parent, main_window):
        QtCore.QThread.__init__(self, parent)
        self.base = main_window

    def run(self):
        self.base.gpr.convolve()
        self.taskFinished.emit()


class ProgressThread(QtCore.QThread):
    notifyProgress = QtCore.Signal(int)

    def __init__(self, parent, main_window):
        QtCore.QThread.__init__(self, parent)
        self.base = main_window

    def run(self):
        from time import sleep
        res = 0
        self.base.gpr.conv_progress = 0
        while res < 98:
            res = int(self.base.gpr.conv_progress)
            self.notifyProgress.emit(res)
            sleep(0.5)
